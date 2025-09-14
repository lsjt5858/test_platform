"""
RabbitMQ message queue handler for test messaging and validation.
"""

import json
import time
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass

try:
    import pika
    from pika.exceptions import AMQPConnectionError, AMQPChannelError
    RABBITMQ_AVAILABLE = True
except ImportError:
    RABBITMQ_AVAILABLE = False
    # 定义占位符异常类，当 RabbitMQ 不可用时使用
    class AMQPConnectionError(Exception):
        pass
    class AMQPChannelError(Exception):
        pass

from .base_mq_handler import BaseMQHandler, Message, MessageQueueError
from ..base_util.logger import get_logger
from ..base_util.retry_util import retry, RetryConfig

logger = get_logger(__name__)


@dataclass
class RabbitMQConfig:
    """Configuration for RabbitMQ connection."""
    host: str = 'localhost'
    port: int = 5672
    virtual_host: str = '/'
    username: str = 'guest'
    password: str = 'guest'
    connection_timeout: int = 30
    heartbeat: int = 600
    blocked_connection_timeout: int = 300
    socket_timeout: int = 10
    ssl_enabled: bool = False
    ssl_options: Optional[Dict[str, Any]] = None
    exchange_type: str = 'direct'
    queue_durable: bool = True
    queue_auto_delete: bool = False
    message_persistent: bool = True


class RabbitMQHandler(BaseMQHandler):
    """RabbitMQ message queue handler with exchange and queue management."""
    
    def __init__(self, 
                 connection_config: Dict[str, Any],
                 rabbitmq_config: Optional[RabbitMQConfig] = None):
        
        if not RABBITMQ_AVAILABLE:
            raise MessageQueueError(
                "pika is not installed. Install it with: pip install pika"
            )
        
        super().__init__(connection_config)
        
        self.rabbitmq_config = rabbitmq_config or RabbitMQConfig()
        
        # Override config with connection_config values
        for key, value in connection_config.items():
            if hasattr(self.rabbitmq_config, key):
                setattr(self.rabbitmq_config, key, value)
        
        self.connection = None
        self.channel = None
        self.exchanges: Dict[str, str] = {}  # exchange_name -> exchange_type
        self.queues: Dict[str, Dict[str, Any]] = {}  # queue_name -> queue_config
    
    def connect(self) -> None:
        """Establish RabbitMQ connection."""
        try:
            # Build connection parameters
            credentials = pika.PlainCredentials(
                self.rabbitmq_config.username,
                self.rabbitmq_config.password
            )
            
            parameters = pika.ConnectionParameters(
                host=self.rabbitmq_config.host,
                port=self.rabbitmq_config.port,
                virtual_host=self.rabbitmq_config.virtual_host,
                credentials=credentials,
                connection_attempts=3,
                retry_delay=2,
                socket_timeout=self.rabbitmq_config.socket_timeout,
                heartbeat=self.rabbitmq_config.heartbeat,
                blocked_connection_timeout=self.rabbitmq_config.blocked_connection_timeout
            )
            
            # Add SSL configuration if enabled
            if self.rabbitmq_config.ssl_enabled:
                ssl_options = self.rabbitmq_config.ssl_options or {}
                parameters.ssl_options = pika.SSLOptions(
                    context=ssl_options.get('context'),
                    server_hostname=ssl_options.get('server_hostname')
                )
            
            # Establish connection
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            self._connected = True
            logger.info(
                f"Connected to RabbitMQ: {self.rabbitmq_config.host}:"
                f"{self.rabbitmq_config.port}/{self.rabbitmq_config.virtual_host}"
            )
            
        except AMQPConnectionError as e:
            error_msg = f"Failed to connect to RabbitMQ: {str(e)}"
            logger.error(error_msg)
            raise MessageQueueError(error_msg)
        
        except Exception as e:
            error_msg = f"Unexpected error connecting to RabbitMQ: {str(e)}"
            logger.error(error_msg)
            raise MessageQueueError(error_msg)
    
    def disconnect(self) -> None:
        """Close RabbitMQ connection."""
        try:
            if self.channel and not self.channel.is_closed:
                self.channel.close()
                self.channel = None
            
            if self.connection and not self.connection.is_closed:
                self.connection.close()
                self.connection = None
            
            self._connected = False
            logger.debug("RabbitMQ connection closed")
            
        except Exception as e:
            logger.warning(f"Error closing RabbitMQ connection: {str(e)}")
    
    def is_connected(self) -> bool:
        """Check if RabbitMQ connection is active."""
        try:
            if not self.connection or self.connection.is_closed:
                return False
            
            if not self.channel or self.channel.is_closed:
                return False
            
            # Try a simple operation to test connection
            self.channel.basic_nop()
            return True
            
        except:
            self._connected = False
            return False
    
    def declare_exchange(self, 
                        exchange_name: str,
                        exchange_type: str = 'direct',
                        durable: bool = True,
                        auto_delete: bool = False) -> None:
        """Declare an exchange."""
        if not self.is_connected():
            self.connect()
        
        try:
            self.channel.exchange_declare(
                exchange=exchange_name,
                exchange_type=exchange_type,
                durable=durable,
                auto_delete=auto_delete
            )
            
            self.exchanges[exchange_name] = exchange_type
            logger.debug(f"Exchange '{exchange_name}' declared (type: {exchange_type})")
            
        except Exception as e:
            error_msg = f"Failed to declare exchange '{exchange_name}': {str(e)}"
            logger.error(error_msg)
            raise MessageQueueError(error_msg)
    
    def declare_queue(self, 
                     queue_name: str,
                     durable: bool = None,
                     exclusive: bool = False,
                     auto_delete: bool = None,
                     arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Declare a queue and return queue information."""
        if not self.is_connected():
            self.connect()
        
        # Use default values from config if not specified
        if durable is None:
            durable = self.rabbitmq_config.queue_durable
        if auto_delete is None:
            auto_delete = self.rabbitmq_config.queue_auto_delete
        
        try:
            method_frame = self.channel.queue_declare(
                queue=queue_name,
                durable=durable,
                exclusive=exclusive,
                auto_delete=auto_delete,
                arguments=arguments
            )
            
            queue_info = {
                'queue': method_frame.method.queue,
                'message_count': method_frame.method.message_count,
                'consumer_count': method_frame.method.consumer_count,
                'durable': durable,
                'exclusive': exclusive,
                'auto_delete': auto_delete
            }
            
            self.queues[queue_name] = queue_info
            logger.debug(f"Queue '{queue_name}' declared")
            
            return queue_info
            
        except Exception as e:
            error_msg = f"Failed to declare queue '{queue_name}': {str(e)}"
            logger.error(error_msg)
            raise MessageQueueError(error_msg)
    
    def bind_queue(self, 
                   queue_name: str,
                   exchange_name: str,
                   routing_key: str = '') -> None:
        """Bind queue to exchange with routing key."""
        if not self.is_connected():
            self.connect()
        
        try:
            self.channel.queue_bind(
                exchange=exchange_name,
                queue=queue_name,
                routing_key=routing_key
            )
            
            logger.debug(
                f"Queue '{queue_name}' bound to exchange '{exchange_name}' "
                f"with routing key '{routing_key}'"
            )
            
        except Exception as e:
            error_msg = (
                f"Failed to bind queue '{queue_name}' to exchange '{exchange_name}': {str(e)}"
            )
            logger.error(error_msg)
            raise MessageQueueError(error_msg)
    
    @retry(RetryConfig(max_attempts=3, exceptions=(AMQPChannelError,)))
    def send_message(self, message: Message) -> bool:
        """Send message to RabbitMQ exchange or queue."""
        if not self.is_connected():
            self.connect()
        
        try:
            # Prepare message body
            if isinstance(message.value, (dict, list)):
                body = json.dumps(message.value)
                content_type = 'application/json'
            else:
                body = str(message.value)
                content_type = 'text/plain'
            
            # Prepare message properties
            properties = pika.BasicProperties(
                content_type=content_type,
                delivery_mode=2 if self.rabbitmq_config.message_persistent else 1,
                headers=message.headers,
                timestamp=message.timestamp or int(time.time())
            )
            
            # Determine exchange and routing key
            # message.topic can be 'exchange:routing_key' or just 'queue_name'
            if ':' in message.topic:
                exchange, routing_key = message.topic.split(':', 1)
            else:
                # Direct queue publishing
                exchange = ''
                routing_key = message.topic
            
            # Publish message
            self.channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=body,
                properties=properties
            )
            
            logger.debug(
                f"Message sent to exchange '{exchange}', routing key '{routing_key}'"
            )
            
            return True
            
        except Exception as e:
            error_msg = f"Failed to send message to '{message.topic}': {str(e)}"
            logger.error(error_msg)
            raise MessageQueueError(error_msg)
    
    def receive_messages(self, topic: str, timeout: Optional[float] = None) -> List[Message]:
        """Receive messages from RabbitMQ queue."""
        if not self.is_connected():
            self.connect()
        
        messages = []
        queue_name = topic
        
        try:
            # Set timeout if specified
            if timeout:
                self.connection.add_timeout(timeout, self._timeout_callback)
            
            while True:
                method_frame, header_frame, body = self.channel.basic_get(
                    queue=queue_name,
                    auto_ack=True
                )
                
                if method_frame is None:
                    # No more messages
                    break
                
                # Parse message body
                try:
                    if header_frame.content_type == 'application/json':
                        value = json.loads(body.decode('utf-8'))
                    else:
                        value = body.decode('utf-8')
                except:
                    value = body
                
                message = Message(
                    topic=method_frame.routing_key,
                    key=None,  # RabbitMQ doesn't have message keys like Kafka
                    value=value,
                    headers=header_frame.headers,
                    partition=None,  # Not applicable to RabbitMQ
                    offset=None,  # Not applicable to RabbitMQ
                    timestamp=header_frame.timestamp
                )
                
                messages.append(message)
            
            logger.debug(f"Received {len(messages)} messages from queue '{queue_name}'")
            return messages
            
        except Exception as e:
            error_msg = f"Failed to receive messages from queue '{queue_name}': {str(e)}"
            logger.error(error_msg)
            raise MessageQueueError(error_msg)
    
    def _timeout_callback(self):
        """Callback for operation timeout."""
        logger.debug("RabbitMQ operation timeout reached")
    
    def consume_continuously(self,
                           queue_name: str,
                           handler: Callable[[Message], None],
                           auto_ack: bool = True,
                           max_messages: Optional[int] = None) -> None:
        """Consume messages continuously from queue."""
        if not self.is_connected():
            self.connect()
        
        message_count = 0
        
        def callback(channel, method, properties, body):
            nonlocal message_count
            
            try:
                # Parse message body
                if properties.content_type == 'application/json':
                    value = json.loads(body.decode('utf-8'))
                else:
                    value = body.decode('utf-8')
                
                message = Message(
                    topic=method.routing_key,
                    key=None,
                    value=value,
                    headers=properties.headers,
                    partition=None,
                    offset=None,
                    timestamp=properties.timestamp
                )
                
                handler(message)
                message_count += 1
                
                if not auto_ack:
                    channel.basic_ack(delivery_tag=method.delivery_tag)
                
                if max_messages and message_count >= max_messages:
                    channel.stop_consuming()
                    
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")
                if not auto_ack:
                    channel.basic_nack(
                        delivery_tag=method.delivery_tag, 
                        requeue=True
                    )
        
        try:
            logger.info(f"Starting continuous consumption from queue '{queue_name}'")
            
            self.channel.basic_consume(
                queue=queue_name,
                on_message_callback=callback,
                auto_ack=auto_ack
            )
            
            self.channel.start_consuming()
            
        except KeyboardInterrupt:
            logger.info("Continuous consumption interrupted")
            self.channel.stop_consuming()
        
        finally:
            logger.info(f"Processed {message_count} messages from queue '{queue_name}'")
    
    def purge_queue(self, queue_name: str) -> int:
        """Purge all messages from queue."""
        if not self.is_connected():
            self.connect()
        
        try:
            method_frame = self.channel.queue_purge(queue=queue_name)
            message_count = method_frame.method.message_count
            
            logger.info(f"Purged {message_count} messages from queue '{queue_name}'")
            return message_count
            
        except Exception as e:
            error_msg = f"Failed to purge queue '{queue_name}': {str(e)}"
            logger.error(error_msg)
            raise MessageQueueError(error_msg)
    
    def delete_queue(self, queue_name: str, if_unused: bool = False, if_empty: bool = False) -> int:
        """Delete queue and return message count."""
        if not self.is_connected():
            self.connect()
        
        try:
            method_frame = self.channel.queue_delete(
                queue=queue_name,
                if_unused=if_unused,
                if_empty=if_empty
            )
            
            message_count = method_frame.method.message_count
            
            if queue_name in self.queues:
                del self.queues[queue_name]
            
            logger.info(f"Queue '{queue_name}' deleted ({message_count} messages)")
            return message_count
            
        except Exception as e:
            error_msg = f"Failed to delete queue '{queue_name}': {str(e)}"
            logger.error(error_msg)
            raise MessageQueueError(error_msg)
    
    def delete_exchange(self, exchange_name: str, if_unused: bool = False) -> None:
        """Delete exchange."""
        if not self.is_connected():
            self.connect()
        
        try:
            self.channel.exchange_delete(
                exchange=exchange_name,
                if_unused=if_unused
            )
            
            if exchange_name in self.exchanges:
                del self.exchanges[exchange_name]
            
            logger.info(f"Exchange '{exchange_name}' deleted")
            
        except Exception as e:
            error_msg = f"Failed to delete exchange '{exchange_name}': {str(e)}"
            logger.error(error_msg)
            raise MessageQueueError(error_msg)
    
    def get_queue_info(self, queue_name: str) -> Dict[str, Any]:
        """Get queue information."""
        if not self.is_connected():
            self.connect()
        
        try:
            method_frame = self.channel.queue_declare(
                queue=queue_name,
                passive=True  # Only check if queue exists
            )
            
            return {
                'queue': method_frame.method.queue,
                'message_count': method_frame.method.message_count,
                'consumer_count': method_frame.method.consumer_count
            }
            
        except Exception as e:
            error_msg = f"Failed to get info for queue '{queue_name}': {str(e)}"
            logger.error(error_msg)
            raise MessageQueueError(error_msg)
    
    def setup_test_environment(self, 
                             exchange_name: str = 'test_exchange',
                             queue_name: str = 'test_queue',
                             routing_key: str = 'test') -> Dict[str, str]:
        """Setup basic test environment with exchange and queue."""
        self.declare_exchange(exchange_name, 'direct')
        self.declare_queue(queue_name)
        self.bind_queue(queue_name, exchange_name, routing_key)
        
        logger.info(f"Test environment setup complete: {exchange_name} -> {queue_name}")
        
        return {
            'exchange': exchange_name,
            'queue': queue_name,
            'routing_key': routing_key
        }