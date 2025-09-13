# Test Platform | 企业级测试平台

> Enterprise-grade automated testing platform with microservice architecture | 基于微服务架构的企业级自动化测试平台

## Project Overview | 项目概述

Test Platform is an enterprise-grade automated testing platform built on a layered architecture design, supporting automated testing for enterprise applications and open APIs with comprehensive infrastructure.

Test Platform 是一个基于分层架构的企业级自动化测试平台，采用四层架构设计，支持企业级应用和开放API的全面自动化测试。

## Architecture | 架构设计

```
┌─────────────────────┐
│    Test Layer       │  测试用例层 - Test Cases & Scenarios
├─────────────────────┤
│    Biz Layer        │  业务编排层 - Business Process Orchestration
├─────────────────────┤
│    App Layer        │  API封装层 - API Abstraction & Standardization  
├─────────────────────┤
│    Core Layer       │  基础设施层 - Infrastructure Foundation
└─────────────────────┘
```

### Layer Description | 层次说明

- **Core Layer（基础设施层）**: Database handlers, message queues, HTTP clients, authentication, logging, retry mechanisms | 数据库处理器、消息队列、HTTP客户端、认证、日志、重试机制
- **App Layer（API封装层）**: Enterprise API and Open API standardization | 企业API和开放API标准化封装
- **Biz Layer（业务编排层）**: Business process orchestration combining multiple APIs | 组合多个API构建业务测试流程
- **Test Layer（测试用例层）**: Domain-specific test cases and scenarios | 领域特定的测试用例和场景

## Tech Stack | 技术栈

### Core Technologies | 核心技术
| Technology | Purpose | 用途 |
|------------|---------|------|
| **Python 3.9+** | Main programming language | 主要编程语言 |
| **pytest** | Testing framework | 测试框架 |
| **requests** | HTTP client library | HTTP客户端库 |
| **Selenium** | UI automation testing | UI自动化测试 |
| **Docker** | Containerization | 容器化部署 |

### Infrastructure | 基础设施
| Component | Technology | 技术栈 |
|-----------|------------|--------|
| **Database** | MySQL, Redis, Elasticsearch | 数据库、缓存、搜索引擎 |
| **Message Queue** | Kafka, RabbitMQ | 消息队列 |
| **Monitoring** | K6, Prometheus, Grafana | 性能监控栈 |
| **Authentication** | OAuth2, JWT, API Key | 多种认证方式 |

## Quick Start | 快速开始

### Environment Setup | 环境准备
```bash
# Install dependencies | 安装依赖
pip install -r requirements.txt

# Activate virtual environment | 激活虚拟环境  
source nut_venv/bin/activate

# Setup configuration | 配置环境
cp config/env/config_default.ini config/env/config_local.ini
# Edit config_local.ini with your settings | 修改配置文件
```

### Running Tests | 运行测试
```bash
# Run all tests | 运行所有测试
./run_test.sh

# Run performance tests | 运行性能测试  
./run_perf.sh

# Development mode | 开发模式
./develop.sh
```

### Docker Deployment | Docker部署
```bash
# Build image | 构建镜像
docker build -t test-platform .

# Start with docker-compose | 使用docker-compose启动
docker-compose up -d
```

## Project Structure | 项目结构

```
test_platform/
├── core/                    # Core infrastructure layer | 基础设施层
│   ├── base_util/          # Base utilities | 基础工具
│   ├── config/             # Configuration management | 配置管理
│   ├── db/                 # Database handlers | 数据库处理器
│   ├── mq/                 # Message queue handlers | 消息队列
│   ├── protocol/           # HTTP/Auth clients | HTTP/认证客户端
│   ├── pytest_util/       # Test utilities | 测试工具
│   └── ui_util/            # UI automation | UI自动化
├── app/                    # API abstraction layer | API封装层
│   ├── enterprise/         # Enterprise API wrappers | 企业API封装
│   ├── open_api/          # Open API wrappers | 开放API封装
│   └── public_api/        # Public API wrappers | 公共API封装
├── biz/                    # Business orchestration layer | 业务编排层
│   └── enterprise/         # Enterprise business flows | 企业业务流程
├── test/                   # Test cases layer | 测试用例层
│   └── domain/            # Domain-specific tests | 领域特定测试
├── performance/            # Performance monitoring | 性能监控
│   ├── k6_runner.py       # K6 test runner | K6测试运行器
│   ├── prometheus_client.py # Prometheus client | Prometheus客户端
│   ├── grafana_dashboard.py # Grafana dashboard | Grafana仪表盘
│   └── performance_analyzer.py # Performance analyzer | 性能分析器
├── perf/                   # Performance test configs | 性能测试配置
├── cli/                    # Command line tools | 命令行工具
├── config/                 # Configuration files | 配置文件
└── utils/                  # Utility scripts | 工具脚本
```

## Core Modules | 核心模块

### 🛠️ Base Utilities | 基础工具
- **Logger**: Production-ready logging system | 生产级日志系统
- **Retry**: Exponential backoff retry mechanism | 指数退避重试机制
- **File**: Atomic file operations | 原子文件操作
- **Exception**: Structured error handling | 结构化异常处理

### 🗄️ Database Support | 数据库支持
- **MySQL**: Connection pooling, transactions | 连接池、事务管理
- **Redis**: JSON serialization, data structures | JSON序列化、数据结构
- **Elasticsearch**: Search, analytics, indexing | 搜索、分析、索引

### 🌐 Protocol Handlers | 协议处理器
- **HTTP Client**: Hooks, retry, session management | 钩子函数、重试、会话管理
- **Auth Handler**: Multi-auth support, token caching | 多种认证、令牌缓存
- **cURL Utility**: Command generation and execution | 命令生成和执行

### 📨 Message Queues | 消息队列
- **Kafka**: High throughput, partitioning | 高吞吐量、分区支持
- **RabbitMQ**: Exchange routing, queue management | 交换路由、队列管理

### 📊 Performance Monitoring | 性能监控
- **K6 Integration**: Load testing automation | 负载测试自动化
- **Prometheus**: Metrics collection | 指标收集
- **Grafana**: Real-time dashboards | 实时仪表盘
- **Performance Analysis**: Automated regression detection | 自动化回归检测

## Usage Examples | 使用示例

### Basic HTTP Client | 基础HTTP客户端
```python
from core.protocol.http_client import HTTPClient
from core.protocol.auth_handler import AuthHandler, AuthType

client = HTTPClient("https://api.example.com")
auth = AuthHandler({'type': AuthType.BEARER, 'token': 'your-token'})
client.set_auth_handler(auth)
response = client.get("/users")
```

### Database Operations | 数据库操作
```python
from core.db.mysql_handler import MySQLHandler

config = {'host': 'localhost', 'user': 'test', 'password': 'pass'}
with MySQLHandler(config) as db:
    users = db.execute_query("SELECT * FROM users WHERE active = %s", (True,))
```

### Performance Testing | 性能测试
```python
from performance.k6_runner import K6Runner, K6Config

config = K6Config(virtual_users=50, duration="5m", script_path="test.js")
runner = K6Runner(config)
results = runner.run_k6_test()
```

### UI Automation | UI自动化
```python
from core.ui_util.webdriver_factory import WebDriverFactory, BrowserConfig
from core.ui_util.page_base import BasePage

config = BrowserConfig(browser="chrome", headless=True)
driver = WebDriverFactory.create_driver(config)
page = BasePage(driver, "https://example.com")
```

## Development Guide | 开发指南

Each layer has independent documentation with detailed responsibilities and usage:

每个层次都有独立的文档说明职责和使用方法：

- [Core Layer Documentation | 核心层文档](core/README.md)
- [App Layer Documentation | API封装层文档](app/src/app/README.md)  
- [Biz Layer Documentation | 业务编排层文档](biz/src/biz/README.md)
- [Performance Testing Guide | 性能测试指南](perf/README.md)
- [Utilities Documentation | 工具集文档](utils/README.md)

## Key Features | 核心特性

### 🚀 High Performance | 高性能
- Connection pooling for all database operations | 所有数据库操作支持连接池
- Asynchronous processing support | 异步处理支持
- Batch operation optimization | 批量操作优化

### 🔧 Easy Maintenance | 易维护  
- Modular design with clear separation | 模块化设计，职责分离
- Comprehensive logging and monitoring | 全面的日志和监控
- Configuration-driven architecture | 配置驱动架构

### 🛡️ High Reliability | 高可靠性
- Retry mechanisms with exponential backoff | 指数退避重试机制
- Comprehensive error handling | 全面错误处理
- Health check capabilities | 健康检查功能

### 📊 Observable | 可观测性
- Integrated performance monitoring | 集成性能监控
- Real-time metrics collection | 实时指标收集
- Automated dashboard generation | 自动化仪表盘生成

## Contributing | 贡献指南

1. Fork the repository | Fork项目
2. Create a feature branch | 创建功能分支
3. Make your changes | 提交更改
4. Add tests for new functionality | 为新功能添加测试
5. Submit a Pull Request | 提交Pull Request

## License | 许可证

This project is licensed under the MIT License. See [LICENSE](LICENSE) file for details.

本项目采用MIT许可证，详情请参见[LICENSE](LICENSE)文件。
