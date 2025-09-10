# App Layer - API 封装层

## 概述

App Layer 是测试平台的 API 封装层，专门负责对各类外部 API 进行标准化封装，提供统一的调用接口。该层不包含业务逻辑，仅做"请求封装"，为上层的 Biz Layer 提供干净、简洁的 API 调用接口。

## 核心职责

1. **API 封装**: 将原始 API 调用封装成简洁的方法
2. **参数标准化**: 统一不同 API 的参数格式
3. **响应规范化**: 标准化 API 响应格式
4. **错误处理**: 统一异常处理机制

## 支持的 API 类型

### 1. Enterprise API (enterprise/)

企业级内部 API 封装，主要用于内部系统间的数据交互。

```python
from app.enterprise.caller.enterprise_client import EnterpriseClient

# 初始化客户端
client = EnterpriseClient(env="test")

# 用户相关操作
user_info = client.get_user_info(user_id="12345")

# 订单相关操作
order_data = {"product_id": "P001", "quantity": 2}
order_resp = client.create_order(order_data)
order_info = client.get_order_info(order_id="O001")
client.update_order(order_id="O001", data={"status": "shipped"})
client.delete_order(order_id="O001")
```

**功能特性**：
- 用户信息查询
- 订单 CRUD 操作
- 统一的异常处理
- 支持环境切换

### 2. Open API (open_api/)

开放 API 封装，用于第三方服务集成。

```python
from app.open_api.caller.open_api_client import OpenApiClient

# 初始化客户端
client = OpenApiClient(env="test")

# 调用开放 API
result = client.call_external_service(params={"key": "value"})
```

### 3. Public API (public_api/)

公共 API 封装，面向外部用户的接口封装。

```python
from app.public_api.caller.public_api_client import PublicApiClient

# 初始化客户端
client = PublicApiClient(env="test")

# 调用公共 API
response = client.public_method(data={"field": "value"})
```

## 架构设计

### 分层结构

```
app/src/app/
├── enterprise/         # 企业 API 封装
│   ├── caller/         # API 调用器
│   ├── constants/      # 常量定义
│   └── model/          # 数据模型
├── open_api/          # 开放 API 封装
│   ├── caller/
│   ├── constants/
│   └── model/
└── public_api/        # 公共 API 封装
    ├── caller/
    ├── constants/
    └── model/
```

### 组件说明

- **caller/**: API 调用器，负责具体的 HTTP 请求封装
- **constants/**: 常量定义，包括 URL 端点、错误码等
- **model/**: 数据模型，定义请求和响应的数据结构

## 设计原则

### 1. 单一职责原则

每个 API 封装类只负责特定领域的 API 调用，不混合不同业务。

```python
class EnterpriseClient:
    """只负责企业 API 的封装，不包含业务逻辑"""
    
    def get_user_info(self, user_id):
        """获取用户信息 - 纯 API 调用封装"""
        return self.client.get(f"/api/v1/users/{user_id}")
```

### 2. 依赖倒置原则

App Layer 依赖于 Core Layer 的抽象接口，不依赖具体实现。

```python
from core.protocol.http_client import HttpClient

class EnterpriseClient:
    def __init__(self, env="default"):
        # 依赖于 Core Layer 的 HTTP 客户端
        self.client = HttpClient(env=env)
```

### 3. 开闭原则

对扩展开放，对修改封闭。新增 API 通过添加新方法实现。

```python
class EnterpriseClient:
    # 现有方法保持不变
    def get_user_info(self, user_id):
        return self.client.get(f"/api/v1/users/{user_id}")
    
    # 新增功能通过添加新方法
    def get_user_orders(self, user_id):
        return self.client.get(f"/api/v1/users/{user_id}/orders")
```

## 使用示例

### 基本用法

```python
from app.enterprise.caller.enterprise_client import EnterpriseClient

# 1. 初始化客户端
client = EnterpriseClient(env="test")

# 2. 调用 API
try:
    # 获取用户信息
    user_response = client.get_user_info("user123")
    print(f"Status: {user_response.status_code}")
    print(f"Data: {user_response.json()}")
    
    # 创建订单
    order_data = {
        "user_id": "user123",
        "product_id": "P001",
        "quantity": 2
    }
    order_response = client.create_order(order_data)
    order_id = order_response.json()["order_id"]
    
    # 查询订单
    order_info = client.get_order_info(order_id)
    print(f"Order info: {order_info.json()}")
    
except Exception as e:
    print(f"API call failed: {e}")
```

### 环境切换

```python
# 开发环境
dev_client = EnterpriseClient(env="dev")

# 测试环境
test_client = EnterpriseClient(env="test")

# 生产环境
prod_client = EnterpriseClient(env="prod")
```

## 扩展指南

### 添加新的 API 方法

1. 在对应的 `caller` 类中添加新方法：

```python
class EnterpriseClient:
    def get_user_profile(self, user_id):
        """获取用户详细资料"""
        return self.client.get(f"/api/v1/users/{user_id}/profile")
```

2. 如需要，在 `constants` 中定义相关常量：

```python
# constants/endpoints.py
USER_PROFILE_ENDPOINT = "/api/v1/users/{}/profile"
```

3. 在 `model` 中定义数据结构（如需要）：

```python
# model/user.py
from dataclasses import dataclass

@dataclass
class UserProfile:
    user_id: str
    name: str
    email: str
    phone: str
```

### 添加新的 API 分类

1. 创建新的目录结构：

```
app/src/app/new_api/
├── caller/
│   └── new_api_client.py
├── constants/
│   └── endpoints.py
└── model/
    └── data_models.py
```

2. 实现 API 客户端：

```python
# new_api/caller/new_api_client.py
from core.protocol.http_client import HttpClient

class NewApiClient:
    def __init__(self, env="default"):
        self.client = HttpClient(env=env)
    
    def new_method(self, params):
        return self.client.post("/api/new/endpoint", json=params)
```

## 最佳实践

1. **保持简洁**: API 封装方法应该简洁明了，避免复杂逻辑
2. **统一命名**: 方法名称应该清晰表达功能，遵循一致的命名规范
3. **异常处理**: 让异常向上传播，由上层业务逻辑处理
4. **文档完善**: 为每个 API 方法编写清晰的文档字符串
5. **版本管理**: 通过 URL 路径管理 API 版本
