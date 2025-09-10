# Core Layer - 系统地基层

## 概述

Core Layer 是整个测试平台的地基，提供各种基础服务和工具组件，为上层的 App 和 Biz 层提供稳定可靠的基础设施支持。

## 核心功能

### 1. 配置管理 (config/)

提供统一的配置管理服务，支持多环境配置。

```python
from core.config.config_loader import ConfigLoader

# 加载默认环境配置
config = ConfigLoader()
base_url = config.get("API", "base_url")

# 加载指定环境配置
config = ConfigLoader(env="test")
db_host = config.get("DATABASE", "host")
```

**特性**：
- 支持多环境配置（default、test、prod 等）
- 自动回退到默认配置
- 基于 INI 格式的配置文件

### 2. HTTP 客户端 (protocol/)

提供标准化的 HTTP 请求客户端，支持会话管理和配置化 base_url。

```python
from core.protocol.http_client import HttpClient

# 创建 HTTP 客户端
client = HttpClient(env="test")

# 发送请求
response = client.get("/api/users")
response = client.post("/api/orders", json={"item": "book"})
```

**特性**：
- 基于 requests.Session 的会话管理
- 支持所有 HTTP 方法（GET、POST、PUT、DELETE 等）
- 自动从配置文件读取 base_url
- 支持环境切换

### 3. 测试断言工具 (pytest_util/)

提供丰富的自定义断言方法，简化测试验证逻辑。

```python
from core.pytest_util.assertions import CustomAssertions

assertions = CustomAssertions()

# 状态码断言
assertions.assert_status_code(response, 200)

# JSON 响应断言
assertions.assert_json_key(response, "user_id")
assertions.assert_json_value(response, "status", "success")
assertions.assert_json_value_type(response, "age", int)
```

**断言方法**：
- `assert_status_code()`: HTTP 状态码断言
- `assert_json_key()`: JSON 键存在性断言
- `assert_json_value()`: JSON 值精确匹配断言
- `assert_json_values()`: JSON 值包含断言
- `assert_json_value_type()`: JSON 值类型断言

### 4. 数据库工具 (db/)

提供数据库连接和操作的基础组件。

### 5. 消息队列 (mq/)

提供消息队列相关的基础服务。

### 6. UI 工具 (ui_util/)

提供 UI 自动化测试的基础工具和组件。

### 7. 基础工具 (base_util/)

提供各种通用的工具函数和辅助方法。

## 设计原则

1. **单一职责**: 每个模块专注于特定的基础服务
2. **配置驱动**: 通过配置文件管理不同环境的差异
3. **易于扩展**: 提供清晰的接口，方便上层调用
4. **错误处理**: 提供完善的异常处理机制

## 使用示例

### 完整的 HTTP 请求示例

```python
from core.protocol.http_client import HttpClient
from core.pytest_util.assertions import CustomAssertions

# 初始化
client = HttpClient(env="test")
assertions = CustomAssertions()

# 发送请求并验证
response = client.get("/api/user/123")
assertions.assert_status_code(response, 200)
assertions.assert_json_key(response, "user_id")
assertions.assert_json_value(response, "user_id", "123")
```

### 配置管理示例

```python
from core.config.config_loader import ConfigLoader

# 加载配置
config = ConfigLoader(env="production")

# 获取各种配置
api_base_url = config.get("API", "base_url")
db_host = config.get("DATABASE", "host", fallback="localhost")
timeout = int(config.get("HTTP", "timeout", fallback="30"))
```

## 目录结构

```
core/src/core/
├── base_util/          # 基础工具
├── config/             # 配置管理
│   └── config_loader.py
├── db/                 # 数据库工具
├── mq/                 # 消息队列
├── protocol/           # 协议相关
│   └── http_client.py
├── pytest_util/        # pytest 工具
│   └── assertions.py
└── ui_util/            # UI 工具
```

## 扩展指南

### 添加新的断言方法

在 `pytest_util/assertions.py` 中添加新的静态方法：

```python
@staticmethod
def assert_response_time(response, max_time):
    elapsed = response.elapsed.total_seconds()
    assert elapsed < max_time, f"Response time {elapsed}s exceeds {max_time}s"
```

### 添加新的协议支持

在 `protocol/` 目录下创建新的协议客户端，参考 `http_client.py` 的设计模式。
