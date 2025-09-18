# 四层架构重构迁移指南

## 🎯 重构概述

您的测试平台已成功重构为标准的四层架构 (Core-App-Biz-Test)，新结构更清晰、更可维护、更易扩展。

## 📋 架构对比

### 原始结构 → 新架构

```
原始结构                    新四层架构
├── core/                   ├── nut_core/     (Core层 - 系统地基)
├── app/                    ├── nut_app/      (App层 - API封装)  
├── biz/                    ├── nut_biz/      (Biz层 - 业务编排)
├── test/                   ├── nut_test/     (Test层 - 测试用例)
├── perf/                   ├── easyuilib/    (UI组件库 - 独立)
├── utils/                  ├── perf/         (性能测试 - 保留)
├── cli/                    └── [其他模块]    (工具和配置)
└── [其他模块]
```

## 🔄 迁移步骤

### Step 1: 使用新的开发脚本

```bash
# 使用新的四层架构脚本
./develop_new.sh

# 激活虚拟环境
source nut_venv/bin/activate
```

### Step 2: 代码迁移对照表

#### 导入语句更新

```python
# 旧导入 → 新导入

# Core层
from core.config.config_loader import ConfigLoader
→ from nut_core.base_util.config_handler import ConfigHandler

from core.protocol.http_client import HttpClient
→ from nut_core.protocol.http_handler import HttpHandler

from core.pytest_util.assertions import CustomAssertions
→ from nut_core.pytest_util.assertions import CustomAssertions

# App层
from app.enterprise.user.caller.enterprise_client import EnterpriseClient
→ from nut_app.enterprise.caller.user_caller import UserCaller
→ from nut_app.enterprise.caller.order_caller import OrderCaller

# Biz层
from biz.enterprise.biz_ops.user_flow import UserFlow
→ from nut_biz.enterprise.biz_ops.user_flow import UserFlow

# Test层
# 测试用例位置从 test/domain/ 迁移到 nut_test/domain/
```

#### API调用方式更新

```python
# 旧方式
client = HttpClient(env="test")
response = client.get("/api/users/123")

# 新方式 
client = HttpHandler(env="test")
response = client.get("/api/users/123")

# 或使用专门的调用器
user_caller = UserCaller(env="test")
response = user_caller.get_user_info("123")
```

### Step 3: 配置文件迁移

配置文件位置和格式保持不变，无需修改：
- `config/env/config_default.ini`
- `config/env/config_test.ini`

### Step 4: 测试用例迁移

```bash
# 将现有测试迁移到新位置
cp -r test/domain/* nut_test/domain/

# 更新导入语句 (使用编辑器批量替换)
# 旧: from app.enterprise.caller.enterprise_client import EnterpriseClient
# 新: from nut_app.enterprise.caller.user_caller import UserCaller
```

## 🆕 新功能特性

### 1. 增强的脚手架工具

```bash
# 创建新的API域
hamster new --domain payment --type api

# 创建完整域 (API + UI)
hamster new --domain order --type full
```

### 2. 改进的HTTP处理器

```python
# 新的HttpHandler具有更多功能
from nut_core.protocol.http_handler import HttpHandler

client = HttpHandler(env="test")

# 支持请求/响应拦截器
client.add_request_interceptor(log_request)
client.add_response_interceptor(log_response)

# 支持多种认证方式
client.set_auth('bearer', token='your_token')
client.set_auth('api_key', api_key='your_key', header_name='X-API-Key')
```

### 3. 数据模型验证

```python
# 新的数据模型支持Pydantic验证
from nut_app.enterprise.model.user_model import UserModel

user_data = UserModel(
    username="test_user",
    email="test@example.com",
    password="SecurePass123"
)

# 自动数据验证和类型检查
```

### 4. 独立包管理

每层都是独立的Python包，支持单独安装：

```bash
# 仅安装Core层
cd nut_core && pip install -e .

# 仅安装App层  
cd nut_app && pip install -e .
```

## 🔧 实际使用示例

### 创建新的测试域

```bash
# 1. 创建payment域
hamster new --domain payment --type api

# 2. 查看生成的文件
ls nut_app/src/nut_app/payment/
ls nut_biz/src/nut_biz/payment/
ls nut_test/domain/payment/

# 3. 运行生成的测试
pytest nut_test/domain/payment/api/ -v
```

### 编写新的测试用例

```python
# nut_test/domain/payment/api/test_payment_api.py
import pytest
from nut_app.payment.caller.payment_caller import PaymentCaller
from nut_core.pytest_util.assertions import CustomAssertions

class TestPaymentAPI:
    def setup_method(self):
        self.payment_caller = PaymentCaller(env="test")  
        self.assertions = CustomAssertions()
    
    def test_create_payment(self):
        payment_data = {
            "order_id": "ORDER_001",
            "amount": 99.99,
            "method": "credit_card"
        }
        
        response = self.payment_caller.create_payment(payment_data)
        
        self.assertions.assert_status_code(response, 201)
        self.assertions.assert_json_key(response, "payment_id")
```

## 🚀 运行和部署

### 开发环境

```bash
# 一键搭建
./develop_new.sh

# 激活环境
source nut_venv/bin/activate

# 运行测试
pytest nut_test/domain/enterprise/api/ -v
```

### 性能测试

```bash
# 启动监控栈
cd perf && docker-compose up -d

# 运行K6测试
./run_perf.sh
```

### CI/CD集成

原有的CI/CD配置保持不变，只需要更新脚本使用新的安装方式：

```yaml
# .github/workflows/ci.yml
- name: Setup Environment
  run: |
    ./develop_new.sh
    source nut_venv/bin/activate
    
- name: Run Tests  
  run: |
    pytest nut_test/domain/ -v --cov
```

## 🔍 故障排除

### 常见问题

1. **导入错误**: 更新import语句，使用新的包路径
2. **配置问题**: 检查config/env/目录下的配置文件
3. **依赖问题**: 运行`./develop_new.sh`重新安装依赖

### 检查清单

- [ ] 运行`./develop_new.sh`成功
- [ ] 虚拟环境激活成功
- [ ] 四个包都能正常导入
- [ ] 脚手架工具`hamster`可用
- [ ] 现有测试用例迁移完成
- [ ] 新测试用例可以正常运行

## 📚 进一步学习

- 查看各层的README文档了解详细功能
- 使用`hamster new`命令体验脚手架功能
- 尝试集成性能测试和监控功能
- 探索数据模型验证和API契约测试

## ✅ 重构完成确认

重构完成后，您将拥有：

1. ✅ **清晰的四层架构**: Core-App-Biz-Test分层明确
2. ✅ **独立包管理**: 每层可独立开发和部署
3. ✅ **强大的脚手架**: hamster工具快速生成代码
4. ✅ **增强的功能**: 数据验证、拦截器、认证支持等
5. ✅ **保留所有优势**: 性能测试、监控、CI/CD等功能完整保留

恭喜您成功完成四层架构重构！🎉