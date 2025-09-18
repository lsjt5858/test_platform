"""
Kafka message queue handler for test data streaming and validation.
"""

import json
import time
from typing import Any, Dict, List, Optional, Callable, TYPE_CHECKING
from dataclasses import dataclass, field

try:
    from kafka import KafkaProducer, KafkaConsumer, KafkaAdminClient
    from kafka.admin import ConfigResource, ConfigResourceType, NewTopic
    from kafka.errors import KafkaError, KafkaTimeoutError
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False
    # 定义占位符异常类，当 Kafka 不可用时使用
    class KafkaError(Exception):
        pass
    class KafkaTimeoutError(Exception):
        pass

if TYPE_CHECKING:
    from kafka import KafkaConsumer

from .base_mq_handler import BaseMQHandler, Message, MessageQueueError
from ..base_util.logger import get_logger
from ..base_util.retry_util import retry, RetryConfig

logger = get_logger(__name__)


@dataclass
class KafkaProducerConfig:
    """Configuration for Kafka producer."""
    bootstrap_servers: List[str] = field(default_factory=lambda: ['localhost:9092'])
    acks: str = 'all'
    retries: int = 3
    max_in_flight_requests_per_connection: int = 1
    key_serializer: str = 'json'
    value_serializer: str = 'json'
    compression_type: Optional[str] = None
    batch_size: int = 16384
    linger_ms: int = 10
    buffer_memory: int = 33554432
    security_protocol: str = 'PLAINTEXT'
    sasl_mechanism: Optional[str] = None
    sasl_plain_username: Optional[str] = None
    sasl_plain_password: Optional[str] = None


@dataclass
class KafkaConsumerConfig:
    """Configuration for Kafka consumer."""
    bootstrap_servers: List[str] = field(default_factory=lambda: ['localhost:9092'])
    group_id: str = 'test-platform-consumer'
    auto_offset_reset: str = 'latest'
    enable_auto_commit: bool = True
    auto_commit_interval_ms: int = 1000
    key_deserializer: str = 'json'
    value_deserializer: str = 'json'
    max_poll_records: int = 500
    fetch_min_bytes: int = 1
    fetch_max_wait_ms: int = 500
    security_protocol: str = 'PLAINTEXT'
    sasl_mechanism: Optional[str] = None
    sasl_plain_username: Optional[str] = None
    sasl_plain_password: Optional[str] = None


class KafkaHandler(BaseMQHandler):
    """Kafka message queue handler with producer/consumer support."""
    
    def __init__(self, 
                 connection_config: Dict[str, Any],
                 producer_config: Optional[KafkaProducerConfig] = None,
                 consumer_config: Optional[KafkaConsumerConfig] = None):
        
        if not KAFKA_AVAILABLE:
            raise MessageQueueError(
"kafka-python is not installed. Install it with: pip install kafka-python"
            )
        
        super().__init__(connection_config)
        
        self.producer_config = producer_config or KafkaProducerConfig()
        self.consumer_config = consumer_config or KafkaConsumerConfig()
        
        # Override configs with connection_config values
        if 'bootstrap_servers' in connection_config:
            self.producer_config.bootstrap_servers = connection_config['bootstrap_servers']
            self.consumer_config.bootstrap_servers = connection_config['bootstrap_servers']
        
        self.producer = None
        self.consumer = None
        self.admin_client = None
        
        # Message serializers
        self._serializers = {
            'json': lambda x: json.dumps(x).encode('utf-8') if x is not None else None,
            'string': lambda x: str(x).encode('utf-8') if x is not None else None,
            'bytes': lambda x: x if isinstance(x, bytes) else str(x).encode('utf-8')
        }
        
        # Message deserializers
        self._deserializers = {
            'json': lambda x: json.loads(x.decode('utf-8')) if x else None,
            'string': lambda x: x.decode('utf-8') if x else None,
            'bytes': lambda x: x
        }
    
    def connect(self) -> None:
        """Establish Kafka connection."""
        try:
            self._create_producer()
            self._create_admin_client()
            self._connected = True
            logger.info(f"Connected to Kafka: {self.producer_config.bootstrap_servers}")
            
        except Exception as e:
            error_msg = f"Failed to connect to Kafka: {str(e)}"
            logger.error(error_msg)
            raise MessageQueueError(error_msg)
    
    def _create_producer(self) -> None:
        """Create Kafka producer."""
        producer_kwargs = {
            'bootstrap_servers': self.producer_config.bootstrap_servers,
            'acks': self.producer_config.acks,
            'retries': self.producer_config.retries,
            'max_in_flight_requests_per_connection': self.producer_config.max_in_flight_requests_per_connection,
            'batch_size': self.producer_config.batch_size,
            'linger_ms': self.producer_config.linger_ms,
            'buffer_memory': self.producer_config.buffer_memory,
            'security_protocol': self.producer_config.security_protocol
        }
        
        # Add serializers
        key_serializer = self._serializers.get(self.producer_config.key_serializer)
        value_serializer = self._serializers.get(self.producer_config.value_serializer)
        
        if key_serializer:
            producer_kwargs['key_serializer'] = key_serializer
        if value_serializer:
            producer_kwargs['value_serializer'] = value_serializer
        
        # Add compression
        if self.producer_config.compression_type:
            producer_kwargs['compression_type'] = self.producer_config.compression_type
        
        # Add SASL authentication
        if self.producer_config.sasl_mechanism:
            producer_kwargs['sasl_mechanism'] = self.producer_config.sasl_mechanism
            producer_kwargs['sasl_plain_username'] = self.producer_config.sasl_plain_username
            producer_kwargs['sasl_plain_password'] = self.producer_config.sasl_plain_password
        
        self.producer = KafkaProducer(**producer_kwargs)
    
    def _create_consumer(self, topics: List[str]) -> 'KafkaConsumer':
        """Create Kafka consumer for specific topics."""
        consumer_kwargs = {
            'bootstrap_servers': self.consumer_config.bootstrap_servers,
            'group_id': self.consumer_config.group_id,
            'auto_offset_reset': self.consumer_config.auto_offset_reset,
            'enable_auto_commit': self.consumer_config.enable_auto_commit,
            'auto_commit_interval_ms': self.consumer_config.auto_commit_interval_ms,
            'max_poll_records': self.consumer_config.max_poll_records,
            'fetch_min_bytes': self.consumer_config.fetch_min_bytes,
            'fetch_max_wait_ms': self.consumer_config.fetch_max_wait_ms,
            'security_protocol': self.consumer_config.security_protocol
        }
        
        # Add deserializers
        key_deserializer = self._deserializers.get(self.consumer_config.key_deserializer)
        value_deserializer = self._deserializers.get(self.consumer_config.value_deserializer)
        
        if key_deserializer:
            consumer_kwargs['key_deserializer'] = key_deserializer
        if value_deserializer:
            consumer_kwargs['value_deserializer'] = value_deserializer
        
        # Add SASL authentication
        if self.consumer_config.sasl_mechanism:
            consumer_kwargs['sasl_mechanism'] = self.consumer_config.sasl_mechanism
            consumer_kwargs['sasl_plain_username'] = self.consumer_config.sasl_plain_username
            consumer_kwargs['sasl_plain_password'] = self.consumer_config.sasl_plain_password
        
        consumer = KafkaConsumer(*topics, **consumer_kwargs)
        return consumer
    
    def _create_admin_client(self) -> None:
        """Create Kafka admin client."""
        admin_kwargs = {
            'bootstrap_servers': self.producer_config.bootstrap_servers,
            'security_protocol': self.producer_config.security_protocol
        }
        
        if self.producer_config.sasl_mechanism:
            admin_kwargs['sasl_mechanism'] = self.producer_config.sasl_mechanism
            admin_kwargs['sasl_plain_username'] = self.producer_config.sasl_plain_username
            admin_kwargs['sasl_plain_password'] = self.producer_config.sasl_plain_password
        
        self.admin_client = KafkaAdminClient(**admin_kwargs)
    
    def disconnect(self) -> None:
        """Close Kafka connections."""
        try:
            if self.producer:
                self.producer.close()
                self.producer = None
            
            if self.consumer:
                self.consumer.close()
                self.consumer = None
            
            if self.admin_client:
                self.admin_client.close()
                self.admin_client = None
            
            self._connected = False
            logger.debug("Kafka connections closed")
            
        except Exception as e:
            logger.warning(f"Error closing Kafka connections: {str(e)}")
    
    def is_connected(self) -> bool:
        """Check if Kafka connection is active."""
        try:
            if not self.producer:
                return False
            
            # Try to get metadata (this will fail if connection is dead)
            metadata = self.producer._client.cluster
            return len(metadata.brokers()) > 0
            
        except:
            self._connected = False
            return False
    
    @retry(RetryConfig(max_attempts=3, exceptions=(KafkaError,)))
    def send_message(self, message: Message) -> bool:
        """Send message to Kafka topic."""
        if not self.is_connected():
            self.connect()
        
        try:
            future = self.producer.send(
                message.topic,
                key=message.key,
                value=message.value,
                headers=message.headers,
                partition=message.partition,
                timestamp_ms=message.timestamp
            )
            
            # Wait for message to be sent
            record_metadata = future.get(timeout=10)
            
            logger.debug(
                f"Message sent to topic '{message.topic}', "
                f"partition {record_metadata.partition}, "
                f"offset {record_metadata.offset}"
            )
            
            return True
            
        except KafkaTimeoutError as e:
            error_msg = f"Timeout sending message to topic '{message.topic}': {str(e)}"
            logger.error(error_msg)
            raise MessageQueueError(error_msg)
        
        except Exception as e:
            error_msg = f"Failed to send message to topic '{message.topic}': {str(e)}"
            logger.error(error_msg)
            raise MessageQueueError(error_msg)
    
    def receive_messages(self, topic: str, timeout: Optional[float] = None) -> List[Message]:
        """Receive messages from Kafka topic."""
        timeout_ms = int(timeout * 1000) if timeout else 1000
        
        consumer = self._create_consumer([topic])
        messages = []
        
        try:
            # Poll for messages
            message_batch = consumer.poll(timeout_ms=timeout_ms)
            
            for topic_partition, records in message_batch.items():
                for record in records:
                    message = Message(
                        topic=record.topic,
                        key=record.key,
                        value=record.value,
                        headers=dict(record.headers) if record.headers else None,
                        partition=record.partition,
                        offset=record.offset,
                        timestamp=record.timestamp
                    )
                    messages.append(message)
            
            logger.debug(f"Received {len(messages)} messages from topic '{topic}'")
            return messages
            
        except Exception as e:
            error_msg = f"Failed to receive messages from topic '{topic}': {str(e)}"
            logger.error(error_msg)
            raise MessageQueueError(error_msg)
        
        finally:
            consumer.close()
    
    def create_topic(self, 
                    topic_name: str,
                    num_partitions: int = 1,
                    replication_factor: int = 1,
                    topic_configs: Optional[Dict[str, str]] = None) -> bool:
        """Create Kafka topic."""
        if not self.admin_client:
            self._create_admin_client()
        
        try:
            topic = NewTopic(
                name=topic_name,
                num_partitions=num_partitions,
                replication_factor=replication_factor,
                topic_configs=topic_configs or {}
            )
            
            result = self.admin_client.create_topics([topic])
            
            # Wait for topic creation
            for topic_name, future in result.items():
                future.result()  # Will raise exception if creation failed
            
            logger.info(f"Topic '{topic_name}' created successfully")
            return True
            
        except Exception as e:
            if "already exists" in str(e).lower():
                logger.warning(f"Topic '{topic_name}' already exists")
                return True
            
            error_msg = f"Failed to create topic '{topic_name}': {str(e)}"
            logger.error(error_msg)
            raise MessageQueueError(error_msg)
    
    def delete_topic(self, topic_name: str) -> bool:
        """Delete Kafka topic."""
        if not self.admin_client:
            self._create_admin_client()
        
        try:
            result = self.admin_client.delete_topics([topic_name])
            
            # Wait for topic deletion
            for topic_name, future in result.items():
                future.result()
            
            logger.info(f"Topic '{topic_name}' deleted successfully")
            return True
            
        except Exception as e:
            error_msg = f"Failed to delete topic '{topic_name}': {str(e)}"
            logger.error(error_msg)
            raise MessageQueueError(error_msg)
    
    def list_topics(self) -> List[str]:
        """List all Kafka topics."""
        if not self.admin_client:
            self._create_admin_client()
        
        try:
            metadata = self.admin_client.list_topics()
            topics = list(metadata.topics)
            logger.debug(f"Found {len(topics)} topics")
            return topics
            
        except Exception as e:
            error_msg = f"Failed to list topics: {str(e)}"
            logger.error(error_msg)
            raise MessageQueueError(error_msg)
    
    def get_topic_metadata(self, topic_name: str) -> Dict[str, Any]:
        """Get metadata for specific topic."""
        if not self.admin_client:
            self._create_admin_client()
        
        try:
            metadata = self.admin_client.list_topics()
            
            if topic_name not in metadata.topics:
                raise MessageQueueError(f"Topic '{topic_name}' not found")
            
            topic_metadata = metadata.topics[topic_name]
            
            return {
                'topic': topic_name,
                'partitions': len(topic_metadata.partitions),
                'partition_info': {
                    partition_id: {
                        'leader': partition.leader,
                        'replicas': partition.replicas,
                        'isr': partition.isr
                    }
                    for partition_id, partition in topic_metadata.partitions.items()
                }
            }
            
        except Exception as e:
            error_msg = f"Failed to get metadata for topic '{topic_name}': {str(e)}"
            logger.error(error_msg)
            raise MessageQueueError(error_msg)
    
    def send_batch_messages(self, messages: List[Message]) -> int:
        """Send multiple messages in batch."""
        if not self.is_connected():
            self.connect()
        
        sent_count = 0
        futures = []
        
        try:
            # Send all messages
            for message in messages:
                future = self.producer.send(
                    message.topic,
                    key=message.key,
                    value=message.value,
                    headers=message.headers,
                    partition=message.partition,
                    timestamp_ms=message.timestamp
                )
                futures.append(future)
            
            # Wait for all messages to be sent
            for future in futures:
                try:
                    future.get(timeout=10)
                    sent_count += 1
                except Exception as e:
                    logger.warning(f"Failed to send one message in batch: {str(e)}")
            
            logger.info(f"Sent {sent_count}/{len(messages)} messages in batch")
            return sent_count
            
        except Exception as e:
            error_msg = f"Batch send failed: {str(e)}"
            logger.error(error_msg)
            raise MessageQueueError(error_msg)
    
    def consume_continuously(self, 
                           topic: str,
                           handler: Callable[[Message], None],
                           max_messages: Optional[int] = None) -> None:
        """Consume messages continuously from topic."""
        consumer = self._create_consumer([topic])
        message_count = 0
        
        try:
            logger.info(f"Starting continuous consumption from topic '{topic}'")
            
            for record in consumer:
                message = Message(
                    topic=record.topic,
                    key=record.key,
                    value=record.value,
                    headers=dict(record.headers) if record.headers else None,
                    partition=record.partition,
                    offset=record.offset,
                    timestamp=record.timestamp
                )
                
                try:
                    handler(message)
                    message_count += 1
                    
                    if max_messages and message_count >= max_messages:
                        logger.info(f"Reached max messages limit: {max_messages}")
                        break
                        
                except Exception as e:
                    logger.error(f"Error processing message: {str(e)}")
            
        except KeyboardInterrupt:
            logger.info("Continuous consumption interrupted")
        
        finally:
            consumer.close()
            logger.info(f"Processed {message_count} messages from topic '{topic}'")
