# Biz Layer - 业务编排层

## 概述

Biz Layer 是测试平台的业务编排层，也称为"胶水层"。它的核心职责是将 App Layer 提供的各种 API 调用组合成完整的业务流程，构建端到端的测试场景。这一层包含了所有的业务逻辑和测试流程编排。

## 核心职责

1. **业务流程编排**: 组合多个 API 调用构建完整业务场景
2. **测试逻辑组织**: 将测试步骤按业务逻辑顺序组织
3. **数据流管理**: 管理测试过程中的数据传递和状态维护
4. **异常处理**: 处理业务流程中的各种异常情况
5. **断言验证**: 对业务结果进行全面验证

## 业务领域分类

### 1. Enterprise 业务 (enterprise/)

企业级业务流程编排，处理内部系统的复杂业务场景。

```python
from biz.enterprise.user.biz_ops import UserFlow

# 初始化业务流程
flow = UserFlow(env="test")

# 执行完整的用户下单流程
order_id = flow.login_and_create_order(
    user_id="user123",
    order_data={"product_id": "P001", "quantity": 2}
)

print(f"订单创建成功: {order_id}")
```

### 2. Open API 业务 (open_api/)

开放 API 相关的业务流程编排。

```python
from biz.open_api.biz_ops.external_flow import ExternalFlow

# 处理第三方集成业务流程
flow = ExternalFlow(env="test")
result = flow.integrate_external_service(params={"key": "value"})
```

## 架构设计

### 目录结构

```
biz/src/biz/
├── enterprise/         # 企业业务编排
│   ├── biz_ops/        # 业务操作
│   ├── checker/        # 数据检查器
│   └── fixed_data/     # 固定测试数据
└── open_api/          # 开放API业务编排
    ├── biz_ops/
    ├── checker/
    └── fixed_data/
```

### 组件说明

- **biz_ops/**: 业务操作核心，包含各种业务流程的实现
- **checker/**: 数据验证和检查组件，用于业务结果验证
- **fixed_data/**: 固定测试数据，提供稳定的测试基础数据

## 核心特性

### 1. 流程编排

将多个 API 调用组合成有意义的业务流程：

```python
class UserFlow:
    def __init__(self, env="default"):
        # 依赖 App Layer 的 API 客户端
        self.client = EnterpriseClient(env)
        # 使用 Core Layer 的断言工具
        self.assertions = CustomAssertions()

    def login_and_create_order(self, user_id, order_data):
        """用户登录并创建订单的完整流程"""
        
        # Step 1: 验证用户存在
        user_resp = self.client.get_user_info(user_id)
        self.assertions.assert_status_code(user_resp)
        
        # Step 2: 创建订单
        order_resp = self.client.create_order(order_data)
        self.assertions.assert_status_code(order_resp)
        self.assertions.assert_json_key(order_resp, "order_id")
        
        # Step 3: 返回订单ID供后续使用
        return order_resp.json()["order_id"]
```

### 2. 数据传递

在业务流程中管理数据的流转：

```python
class OrderFlow:
    def complete_order_lifecycle(self, user_id):
        """订单完整生命周期测试"""
        
        # 1. 创建订单
        order_data = {"product_id": "P001", "quantity": 1}
        order_id = self.create_order(user_id, order_data)
        
        # 2. 更新订单（使用上一步的结果）
        update_data = {"status": "processing"}
        self.update_order_status(order_id, update_data)
        
        # 3. 完成订单（继续使用订单ID）
        self.complete_order(order_id)
        
        return order_id
```

### 3. 业务验证

对业务结果进行全面的验证：

```python
class OrderFlow:
    def verify_order_creation(self, user_id, product_id):
        """验证订单创建的完整性"""
        
        # 创建订单
        order_data = {"product_id": product_id, "quantity": 1}
        order_resp = self.client.create_order(order_data)
        
        # 业务层面的验证
        self.assertions.assert_status_code(order_resp, 201)
        self.assertions.assert_json_key(order_resp, "order_id")
        
        order_id = order_resp.json()["order_id"]
        
        # 验证订单详情
        detail_resp = self.client.get_order_info(order_id)
        self.assertions.assert_json_value(detail_resp, "user_id", user_id)
        self.assertions.assert_json_value(detail_resp, "product_id", product_id)
        self.assertions.assert_json_value(detail_resp, "status", "created")
        
        return order_id
```

## 设计原则

### 1. 业务导向

每个业务流程都应该对应真实的业务场景：

```python
class UserFlow:
    def user_shopping_journey(self, user_id):
        """用户购物完整旅程"""
        # 1. 浏览商品
        products = self.browse_products()
        
        # 2. 加入购物车
        cart_id = self.add_to_cart(user_id, products[0]["id"])
        
        # 3. 创建订单
        order_id = self.checkout(cart_id)
        
        # 4. 支付订单
        payment_result = self.pay_order(order_id)
        
        return {
            "order_id": order_id,
            "payment_id": payment_result["payment_id"]
        }
```

### 2. 层次分离

Biz Layer 只关注业务逻辑，不关注具体的 API 实现细节：

```python
# ✅ 正确：关注业务流程
def process_user_registration(self, user_data):
    # 业务逻辑：注册用户
    user_resp = self.client.register_user(user_data)
    self.verify_registration_success(user_resp)
    
    # 业务逻辑：发送欢迎邮件
    welcome_resp = self.client.send_welcome_email(user_data["email"])
    self.verify_email_sent(welcome_resp)

# ❌ 错误：包含低层实现细节
def process_user_registration_wrong(self, user_data):
    # 不应该在 Biz Layer 处理 HTTP 请求细节
    headers = {"Content-Type": "application/json"}
    response = requests.post("http://api.com/users", json=user_data, headers=headers)
```

### 3. 可复用性

设计可复用的业务组件：

```python
class CommonFlow:
    def setup_test_user(self, user_type="normal"):
        """创建测试用户 - 可在多个业务场景中复用"""
        user_data = self.get_test_user_data(user_type)
        user_resp = self.client.create_user(user_data)
        self.assertions.assert_status_code(user_resp, 201)
        return user_resp.json()["user_id"]
    
    def cleanup_test_data(self, user_id):
        """清理测试数据 - 可在多个测试中复用"""
        self.client.delete_user(user_id)
```

## 使用示例

### 复杂业务流程

```python
from biz.enterprise.user.biz_ops import UserFlow


def test_complete_shopping_flow():
    """测试完整的购物流程"""

    # 初始化业务流程
    flow = UserFlow(env="test")

    # 执行完整的购物业务流程
    try:
        # 1. 用户注册
        user_id = flow.register_new_user({
            "username": "testuser",
            "email": "test@example.com"
        })

        # 2. 用户登录并创建订单
        order_id = flow.login_and_create_order(
            user_id=user_id,
            order_data={"product_id": "P001", "quantity": 2}
        )

        # 3. 订单支付
        payment_id = flow.pay_for_order(order_id, {
            "payment_method": "credit_card",
            "amount": 199.99
        })

        # 4. 验证整个流程
        flow.verify_order_completion(order_id, payment_id)

        print(f"购物流程测试完成: 订单 {order_id}, 支付 {payment_id}")

    except Exception as e:
        print(f"业务流程失败: {e}")
        raise
```

### 数据驱动测试

```python
class UserFlow:
    def test_multiple_user_scenarios(self, user_scenarios):
        """测试多种用户场景"""
        results = []
        
        for scenario in user_scenarios:
            try:
                # 根据场景数据执行业务流程
                result = self.execute_user_scenario(scenario)
                results.append({"scenario": scenario["name"], "result": "success"})
            except Exception as e:
                results.append({"scenario": scenario["name"], "result": "failed", "error": str(e)})
        
        return results
```

## 扩展指南

### 添加新的业务流程

1. 在对应的 `biz_ops` 目录创建新的流程类：

```python
# biz/enterprise/biz_ops/payment_flow.py
from app.enterprise.user.caller.enterprise_client import EnterpriseClient
from core.pytest_util.assertions import CustomAssertions


class PaymentFlow:
    def __init__(self, env="default"):
        self.client = EnterpriseClient(env)
        self.assertions = CustomAssertions()

    def process_payment(self, order_id, payment_data):
        """处理支付流程"""
        # 1. 验证订单状态
        order_resp = self.client.get_order_info(order_id)
        self.assertions.assert_json_value(order_resp, "status", "pending")

        # 2. 创建支付
        payment_resp = self.client.create_payment(payment_data)
        self.assertions.assert_status_code(payment_resp, 201)

        return payment_resp.json()["payment_id"]
```

### 添加数据检查器

1. 在 `checker` 目录创建数据验证器：

```python
# biz/enterprise/checker/order_checker.py
class OrderChecker:
    def __init__(self, client):
        self.client = client
    
    def verify_order_integrity(self, order_id):
        """验证订单数据完整性"""
        order_resp = self.client.get_order_info(order_id)
        order_data = order_resp.json()
        
        # 业务规则验证
        assert "user_id" in order_data
        assert "product_id" in order_data
        assert order_data["quantity"] > 0
        assert order_data["total_amount"] > 0
```

## 最佳实践

1. **业务语言**: 使用业务领域的术语命名方法和变量
2. **流程完整**: 每个业务流程应该有明确的开始和结束
3. **异常处理**: 妥善处理业务流程中的各种异常情况
4. **状态管理**: 正确管理业务对象的状态转换
5. **测试隔离**: 确保不同的业务流程测试之间相互隔离
6. **数据清理**: 在测试完成后清理产生的测试数据
