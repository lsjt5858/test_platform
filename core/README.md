# Test Platform Core Layer | 测试平台核心层

> Enterprise-grade test infrastructure foundation | 企业级测试基础设施

The core layer provides production-ready infrastructure components including database handlers, protocol clients, message queues, and utilities for scalable test automation.

核心层提供生产级基础设施组件，包括数据库处理器、协议客户端、消息队列和可扩展测试自动化工具。

## Architecture | 架构

```
core/src/core/
├── base_util/    # Core utilities | 核心工具
├── config/       # Config management | 配置管理  
├── db/           # Database handlers | 数据库处理器
├── mq/           # Message queues | 消息队列
├── protocol/     # HTTP/Auth clients | HTTP/认证客户端
├── pytest_util/ # Test utilities | 测试工具
└── ui_util/      # UI automation | UI自动化
```

## Quick Start | 快速开始

```python
from core.base_util.logger import get_logger
from core.db.mysql_handler import MySQLHandler
from core.protocol.http_client import HTTPClient

logger = get_logger("test")
db = MySQLHandler({'host': 'localhost', 'user': 'test', 'password': 'pass'})
client = HTTPClient("https://api.example.com")
```

## Components | 组件

### 🛠️ Base Utilities | 基础工具 (`base_util`)

| Component | Description | 组件描述 |
|-----------|-------------|----------|
| **Logger** | Production logging system | 生产级日志系统 |
| **Retry** | Exponential backoff retry | 指数退避重试机制 |
| **File** | Atomic file operations | 原子文件操作 |
| **Exception** | Structured error handling | 结构化异常处理 |

```python
# Logger | 日志
logger = get_logger("test")
logger.info("Test started", extra={'test_id': '123'})

# Retry | 重试
@retry(RetryConfig(max_attempts=3, backoff_factor=2.0))
def api_call(): pass

# File | 文件
FileUtil.write_json("/output/results.json", {"status": "success"})
```

### 🗄️ Database Handlers | 数据库处理器 (`db`)

| Handler | Features | 特性 |
|---------|----------|------|
| **MySQL** | Connection pooling, transactions | 连接池、事务管理 |
| **Redis** | JSON serialization, data structures | JSON序列化、数据结构 |
| **Elasticsearch** | Search, analytics, indexing | 搜索、分析、索引 |

```python
# MySQL
db = MySQLHandler(config)
with db.transaction():
    results = db.execute_query("SELECT * FROM users")

# Redis  
redis = RedisHandler(config)
redis.set('user:123', {'name': 'John'}, expire=3600)

# Elasticsearch
es = ElasticsearchHandler(config)
results = es.search('logs', {'query': {'match': {'level': 'ERROR'}}})
```

### 🌐 Protocol Handlers | 协议处理器 (`protocol`)

| Component | Features | 特性 |
|-----------|----------|------|
| **HTTP Client** | Hooks, retry, session management | 钩子函数、重试、会话管理 |
| **Auth Handler** | Multi-auth, token caching | 多种认证、令牌缓存 |
| **cURL Utility** | Command generation, execution | 命令生成、执行 |

```python
# HTTP Client
client = HTTPClient("https://api.example.com")
auth = AuthHandler({'type': AuthType.BEARER, 'token': 'jwt-token'})
client.set_auth_handler(auth)
response = client.get("/users")

# cURL Generation
curl_cmd = CurlUtil.build_curl_command('POST', url, data={'name': 'John'})
result = CurlUtil.execute_curl(curl_cmd)
```

### 📨 Message Queue | 消息队列 (`mq`)

| Handler | Features | 特性 |
|---------|----------|------|
| **Kafka** | High throughput, partitioning | 高吞吐量、分区 |
| **RabbitMQ** | Exchange routing, queues | 交换路由、队列 |

```python
# Kafka
kafka = KafkaHandler({'bootstrap_servers': ['localhost:9092']})
message = Message(topic='events', value={'user_id': 123})
kafka.send_message(message)

# RabbitMQ  
rabbitmq = RabbitMQHandler(config)
rabbitmq.declare_exchange('events', 'direct')
rabbitmq.send_message(message)
```

### ⚙️ Configuration | 配置管理 (`config`)

```python
config_loader = ConfigLoader()
config = config_loader.load_environment_config('production')
db_config = config_loader.get_nested_value(config, 'database.mysql.host')
```

## Example Usage | 使用示例

### Integration Test | 集成测试
```python
from core.config.config_loader import ConfigLoader
from core.base_util.logger import get_logger
from core.db.mysql_handler import MySQLHandler
from core.protocol.http_client import HTTPClient

config = ConfigLoader().load_environment_config('test')
logger = get_logger("integration_test")

db = MySQLHandler(config['database']['mysql'])
client = HTTPClient(base_url=config['api']['base_url'])

try:
    with db:
        users = db.execute_query("SELECT * FROM users LIMIT 10")
        logger.info(f"Found {len(users)} users")
    
    response = client.get("/health")
    logger.info(f"API health: {response.status_code}")
    
except Exception as e:
    logger.error(f"Test failed: {e}")
```

## Configuration | 配置文件

```yaml
# config/production.yaml
database:
  mysql:
    host: db.prod.com
    user: prod_user
    password: ${DB_PASSWORD}
    database: prod_db
    max_connections: 20
    
  redis:
    host: cache.prod.com
    port: 6379
    max_connections: 50
    
api:
  base_url: https://api.prod.com
  timeout: 30
  max_retries: 3
  
messaging:
  kafka:
    bootstrap_servers: ["kafka1.prod.com:9092", "kafka2.prod.com:9092"]
    
logging:
  level: INFO
  file_path: /var/log/test-platform.log
```

## Installation | 安装

### Dependencies | 依赖项
```bash
# Core dependencies | 核心依赖
pip install pymysql redis elasticsearch kafka-python pika requests pyyaml

# Optional | 可选
pip install python-magic orjson prometheus-client
```

### Environment Setup | 环境配置
```bash
export DB_PASSWORD="your-secure-password"
export REDIS_URL="redis://localhost:6379/0"
export KAFKA_BROKERS="localhost:9092"
```

## Best Practices | 最佳实践

- **Connection Management**: Use context managers for database connections | 使用上下文管理器管理数据库连接
- **Error Handling**: Implement comprehensive retry logic | 实现完善的重试逻辑  
- **Logging**: Include contextual information in logs | 在日志中包含上下文信息
- **Configuration**: Use environment-specific configs | 使用特定环境配置
- **Testing**: Write unit tests for all components | 为所有组件编写单元测试

## License | 许可证

This project is licensed under the MIT License. See LICENSE file for details.

本项目采用MIT许可证，详情请参见LICENSE文件。