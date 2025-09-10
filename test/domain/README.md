# Test Domain - 测试用例

## 概述

Test Domain 模块包含所有的测试用例，按照业务领域和测试类型进行组织。测试用例基于已搭建的三层架构（Core-App-Biz）编写，确保测试的可维护性和可扩展性。

## 测试分类

### 1. 单元测试 (Unit Tests)

测试单个组件或函数的功能，确保基础组件的正确性。

```python
# test/domain/unit/test_core_config.py
import pytest
from core.config.config_loader import ConfigLoader

class TestConfigLoader:
    def test_load_default_config(self):
        """测试加载默认配置"""
        config = ConfigLoader()
        assert config is not None
    
    def test_load_specific_env_config(self):
        """测试加载特定环境配置"""
        config = ConfigLoader(env="test")
        assert config is not None
    
    def test_get_config_value(self):
        """测试获取配置值"""
        config = ConfigLoader()
        value = config.get("API", "base_url")
        assert value is not None
    
    def test_get_config_with_fallback(self):
        """测试带默认值的配置获取"""
        config = ConfigLoader()
        value = config.get("MISSING", "key", fallback="default")
        assert value == "default"
```

### 2. 集成测试 (Integration Tests)

测试不同组件之间的集成，验证组件间的协作。

```python
# test/domain/integration/test_api_integration.py
import pytest
from app.enterprise.caller.enterprise_client import EnterpriseClient
from core.pytest_util.assertions import CustomAssertions

class TestEnterpriseAPIIntegration:
    def setup_method(self):
        """测试设置"""
        self.client = EnterpriseClient(env="test")
        self.assertions = CustomAssertions()
    
    def test_get_user_info_integration(self):
        """测试获取用户信息的集成"""
        # 假设测试环境有预设用户
        user_id = "test_user_001"
        response = self.client.get_user_info(user_id)
        
        self.assertions.assert_status_code(response, 200)
        self.assertions.assert_json_key(response, "user_id")
        self.assertions.assert_json_value(response, "user_id", user_id)
    
    def test_create_order_integration(self):
        """测试创建订单的集成"""
        order_data = {
            "user_id": "test_user_001",
            "product_id": "P001",
            "quantity": 1
        }
        
        response = self.client.create_order(order_data)
        
        self.assertions.assert_status_code(response, 201)
        self.assertions.assert_json_key(response, "order_id")
        
        # 验证订单详情
        order_id = response.json()["order_id"]
        detail_response = self.client.get_order_info(order_id)
        self.assertions.assert_status_code(detail_response, 200)
        self.assertions.assert_json_value(detail_response, "user_id", order_data["user_id"])
```

### 3. 业务流程测试 (Business Flow Tests)

测试完整的业务流程，验证端到端的用户场景。

```python
# test/domain/business/test_user_journey.py
import pytest
from biz.enterprise.biz_ops.user_flow import UserFlow
from utils.data_generator import DataGenerator

class TestUserJourney:
    def setup_method(self):
        """测试设置"""
        self.flow = UserFlow(env="test")
        self.data_generator = DataGenerator()
    
    @pytest.mark.integration
    def test_complete_user_shopping_flow(self):
        """测试完整的用户购物流程"""
        # 生成测试用户数据
        user_data = self.data_generator.generate_user_data()
        
        # 1. 用户注册（假设有注册功能）
        user_id = self.flow.register_user(user_data)
        assert user_id is not None
        
        # 2. 用户登录并创建订单
        order_data = self.data_generator.generate_order_data()
        order_id = self.flow.login_and_create_order(user_id, order_data)
        assert order_id is not None
        
        # 3. 验证订单状态
        order_info = self.flow.get_order_details(order_id)
        assert order_info["status"] == "created"
        assert order_info["user_id"] == user_id
        
        # 4. 更新订单状态
        self.flow.update_order_status(order_id, "confirmed")
        
        # 5. 验证最终状态
        final_order_info = self.flow.get_order_details(order_id)
        assert final_order_info["status"] == "confirmed"
    
    @pytest.mark.smoke
    def test_user_login_and_order_creation(self):
        """冒烟测试：用户登录并创建订单"""
        user_id = "test_user_smoke"
        order_data = {
            "product_id": "P001",
            "quantity": 1
        }
        
        order_id = self.flow.login_and_create_order(user_id, order_data)
        assert order_id is not None
        
        # 验证订单基本信息
        order_info = self.flow.get_order_details(order_id)
        assert order_info["user_id"] == user_id
        assert order_info["product_id"] == order_data["product_id"]
```

### 4. API 契约测试 (Contract Tests)

验证 API 的输入输出契约，确保 API 的稳定性。

```python
# test/domain/contract/test_api_contract.py
import pytest
import jsonschema
from app.enterprise.caller.enterprise_client import EnterpriseClient

class TestAPIContract:
    def setup_method(self):
        """测试设置"""
        self.client = EnterpriseClient(env="test")
        
        # 定义 API 响应的 JSON Schema
        self.user_schema = {
            "type": "object",
            "properties": {
                "user_id": {"type": "string"},
                "username": {"type": "string"},
                "email": {"type": "string"},
                "created_at": {"type": "string"}
            },
            "required": ["user_id", "username", "email"]
        }
        
        self.order_schema = {
            "type": "object",
            "properties": {
                "order_id": {"type": "string"},
                "user_id": {"type": "string"},
                "product_id": {"type": "string"},
                "quantity": {"type": "integer"},
                "status": {"type": "string"},
                "created_at": {"type": "string"}
            },
            "required": ["order_id", "user_id", "product_id", "quantity", "status"]
        }
    
    def test_user_info_api_contract(self):
        """测试用户信息 API 契约"""
        user_id = "contract_test_user"
        response = self.client.get_user_info(user_id)
        
        assert response.status_code == 200
        
        # 验证响应结构符合契约
        response_data = response.json()
        jsonschema.validate(response_data, self.user_schema)
    
    def test_order_creation_api_contract(self):
        """测试订单创建 API 契约"""
        order_data = {
            "user_id": "contract_test_user",
            "product_id": "P001",
            "quantity": 2
        }
        
        response = self.client.create_order(order_data)
        
        assert response.status_code == 201
        
        # 验证响应结构符合契约
        response_data = response.json()
        jsonschema.validate(response_data, self.order_schema)
```

### 5. 性能测试用例 (Performance Test Cases)

结合性能测试脚本的测试用例验证。

```python
# test/domain/performance/test_performance_validation.py
import pytest
import json
from pathlib import Path

class TestPerformanceValidation:
    @pytest.mark.performance
    def test_load_test_results(self):
        """验证负载测试结果"""
        results_file = Path("perf/k6/results/load_test_latest.json")
        
        if not results_file.exists():
            pytest.skip("No load test results found")
        
        with open(results_file) as f:
            results = json.load(f)
        
        # 验证性能指标
        metrics = results.get("metrics", {})
        
        # 平均响应时间应小于 500ms
        avg_response_time = metrics.get("http_req_duration", {}).get("avg", 0)
        assert avg_response_time < 500, f"Average response time {avg_response_time}ms exceeds 500ms"
        
        # 95% 响应时间应小于 1000ms
        p95_response_time = metrics.get("http_req_duration", {}).get("p(95)", 0)
        assert p95_response_time < 1000, f"95% response time {p95_response_time}ms exceeds 1000ms"
        
        # 错误率应小于 1%
        error_rate = metrics.get("http_req_failed", {}).get("rate", 0)
        assert error_rate < 0.01, f"Error rate {error_rate*100}% exceeds 1%"
```

## 测试数据管理

### 1. 测试夹具 (Fixtures)

```python
# test/conftest.py
import pytest
from utils.data_generator import DataGenerator
from core.config.config_loader import ConfigLoader

@pytest.fixture
def test_config():
    """测试配置夹具"""
    return ConfigLoader(env="test")

@pytest.fixture
def test_user_data():
    """测试用户数据夹具"""
    generator = DataGenerator()
    return generator.generate_user_data()

@pytest.fixture
def test_order_data():
    """测试订单数据夹具"""
    generator = DataGenerator()
    return generator.generate_order_data()

@pytest.fixture
def enterprise_client():
    """企业客户端夹具"""
    from app.enterprise.caller.enterprise_client import EnterpriseClient
    return EnterpriseClient(env="test")

@pytest.fixture
def user_flow():
    """用户流程夹具"""
    from biz.enterprise.biz_ops.user_flow import UserFlow
    return UserFlow(env="test")

@pytest.fixture(scope="session")
def test_database():
    """测试数据库夹具"""
    # 设置测试数据库
    yield "test_database_connection"
    # 清理测试数据库
```

### 2. 测试数据文件

```json
// test/data/users.json
[
  {
    "user_id": "test_user_001",
    "username": "testuser1",
    "email": "testuser1@example.com",
    "password": "password123"
  },
  {
    "user_id": "test_user_002", 
    "username": "testuser2",
    "email": "testuser2@example.com",
    "password": "password456"
  }
]
```

```json
// test/data/orders.json
[
  {
    "order_id": "test_order_001",
    "user_id": "test_user_001",
    "product_id": "P001",
    "quantity": 2,
    "unit_price": 99.99,
    "status": "created"
  }
]
```

## 测试配置

### 1. pytest 配置

```ini
# pytest.ini
[tool:pytest]
minversion = 6.0
addopts = 
    -ra 
    --strict-markers 
    --strict-config 
    --cov=core 
    --cov=app 
    --cov=biz
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-report=xml
testpaths = 
    test
python_files = 
    test_*.py
    *_test.py
python_classes = 
    Test*
python_functions = 
    test_*
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: integration tests
    unit: unit tests
    smoke: smoke tests
    performance: performance tests
    contract: API contract tests
    regression: regression tests
filterwarnings =
    ignore::UserWarning
    ignore::DeprecationWarning
```

### 2. 测试环境配置

```ini
# config/env/config_test.ini
[API]
base_url = http://localhost:8080
timeout = 30

[DATABASE]
host = localhost
port = 3306
user = test_user
password = test_password
database = test_db

[REDIS]
host = localhost
port = 6379
db = 1

[LOGGING]
level = DEBUG
file = logs/test.log
```

## 测试执行策略

### 1. 测试分层执行

```bash
# 单元测试（快速）
pytest test/domain/unit/ -v

# 集成测试（中等）
pytest test/domain/integration/ -v

# 业务流程测试（较慢）
pytest test/domain/business/ -v

# 契约测试
pytest test/domain/contract/ -v

# 全量测试
pytest test/domain/ -v
```

### 2. 标签化执行

```bash
# 冒烟测试
pytest -m smoke

# 回归测试
pytest -m regression

# 性能测试
pytest -m performance

# 排除慢速测试
pytest -m "not slow"

# 组合标签
pytest -m "smoke or regression"
```

### 3. 并行执行

```bash
# 并行运行测试
pytest -n auto

# 指定进程数
pytest -n 4

# 按测试文件分发
pytest --dist worksteal
```

## 测试报告

### 1. HTML 报告

```bash
# 生成 HTML 报告
pytest --html=reports/report.html --self-contained-html
```

### 2. 覆盖率报告

```bash
# 生成覆盖率报告
pytest --cov=core --cov=app --cov=biz --cov-report=html
```

### 3. JUnit XML 报告

```bash
# 生成 JUnit XML 报告（CI/CD 集成）
pytest --junit-xml=reports/junit.xml
```

## 目录结构

```
test/domain/
├── conftest.py              # 全局测试配置和夹具
├── unit/                    # 单元测试
│   ├── test_core_config.py
│   ├── test_http_client.py
│   └── test_assertions.py
├── integration/             # 集成测试
│   ├── test_api_integration.py
│   └── test_db_integration.py
├── business/               # 业务流程测试
│   ├── test_user_journey.py
│   └── test_order_flow.py
├── contract/               # 契约测试
│   ├── test_api_contract.py
│   └── schemas/
├── performance/            # 性能测试验证
│   └── test_performance_validation.py
└── data/                   # 测试数据
    ├── users.json
    ├── orders.json
    └── scenarios.yaml
```

## 最佳实践

1. **测试独立性**: 每个测试应该独立运行，不依赖其他测试的结果
2. **测试数据隔离**: 使用独立的测试数据，避免数据污染
3. **分层测试**: 按照测试金字塔原则，多写单元测试，少写 UI 测试
4. **明确的测试目的**: 每个测试应该有明确的验证目标
5. **可读的测试名称**: 测试名称应该清晰表达测试意图
6. **适当的断言**: 使用合适的断言方法，提供清晰的错误信息
7. **测试维护**: 定期审查和更新测试用例，保持测试的有效性
