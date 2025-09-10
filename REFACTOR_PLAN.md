# 四层架构重构方案 (Core-App-Biz-Test)

## 🎯 重构目标
将当前项目重构为标准的四层测试架构，提升代码组织性、可维护性和扩展性。

## 📋 当前状态分析

### 优点
- ✅ 已有四层基础结构
- ✅ 分层职责相对清晰  
- ✅ 有完整的文档体系
- ✅ 集成了性能测试和监控

### 需要优化的点
- 🔧 完善Core层的工具模块
- 🔧 标准化App层的caller模式
- 🔧 增强Biz层的业务编排能力
- 🔧 优化Test层的用例组织
- 🔧 统一CLI和脚手架工具

## 📁 目标架构设计

```
test_platform/
├── 📁 nut_core/                    # 第一层：系统地基层
│   ├── setup.py                    # 独立安装包
│   └── src/nut_core/
│       ├── __init__.py
│       ├── base_util/              # 基础工具
│       │   ├── config_handler.py   # 配置管理
│       │   ├── logger.py           # 日志系统
│       │   ├── retry_util.py       # 重试机制
│       │   └── wait_util.py        # 等待工具
│       ├── protocol/               # 协议封装
│       │   ├── http_handler.py     # HTTP客户端
│       │   ├── ws_handler.py       # WebSocket客户端
│       │   └── auth_handler.py     # 认证处理
│       ├── db/                     # 数据库工具
│       │   ├── mysql_handler.py    # MySQL操作
│       │   ├── redis_handler.py    # Redis操作
│       │   └── es_handler.py       # Elasticsearch操作
│       ├── mq/                     # 消息队列
│       │   ├── kafka_handler.py    # Kafka操作
│       │   └── rabbitmq_handler.py # RabbitMQ操作
│       ├── ui/                     # UI自动化基础
│       │   ├── driver_factory.py   # 驱动工厂
│       │   ├── browser_handler.py  # 浏览器操作
│       │   └── element_handler.py  # 元素操作
│       ├── pytest_util/            # 测试工具
│       │   ├── assertions.py       # 断言工具
│       │   ├── fixtures.py         # 测试夹具
│       │   └── marks.py            # 测试标记
│       └── cli/                    # 脚手架工具
│           ├── hammer.py           # 代码生成器
│           └── templates/          # 模板文件
│
├── 📁 nut_app/                     # 第二层：API封装层
│   ├── setup.py
│   └── src/nut_app/
│       ├── __init__.py
│       ├── enterprise/             # 企业API域
│       │   ├── caller/             # API调用器
│       │   │   ├── __init__.py
│       │   │   ├── user_caller.py
│       │   │   ├── order_caller.py
│       │   │   └── product_caller.py
│       │   ├── constants/          # 常量定义
│       │   │   ├── __init__.py
│       │   │   ├── urls.py
│       │   │   └── enums.py
│       │   └── model/              # 数据模型
│       │       ├── __init__.py
│       │       ├── user_model.py
│       │       └── order_model.py
│       ├── open_api/               # 开放API域
│       │   ├── caller/
│       │   ├── constants/
│       │   └── model/
│       ├── public_api/             # 公共API域
│       │   ├── caller/
│       │   ├── constants/
│       │   └── model/
│       └── internal_api/           # 内部API域
│           ├── caller/
│           ├── constants/
│           └── model/
│
├── 📁 nut_biz/                     # 第三层：业务编排层
│   ├── setup.py
│   └── src/nut_biz/
│       ├── __init__.py
│       ├── enterprise/             # 企业业务域
│       │   ├── biz_ops/            # 业务操作
│       │   │   ├── __init__.py
│       │   │   ├── user_flow.py    # 用户业务流程
│       │   │   ├── order_flow.py   # 订单业务流程
│       │   │   └── payment_flow.py # 支付业务流程
│       │   ├── checker/            # 业务检查器
│       │   │   ├── __init__.py
│       │   │   ├── user_checker.py
│       │   │   └── order_checker.py
│       │   ├── fixed_data/         # 固定测试数据
│       │   │   ├── __init__.py
│       │   │   ├── users.py
│       │   │   └── orders.py
│       │   ├── request_body/       # 请求体模板
│       │   │   ├── __init__.py
│       │   │   ├── user_requests.py
│       │   │   └── order_requests.py
│       │   └── helper/             # 辅助工具
│       │       ├── __init__.py
│       │       └── data_helper.py
│       ├── open_api/               # 开放API业务域
│       │   ├── biz_ops/
│       │   ├── checker/
│       │   └── fixed_data/
│       └── enterprise_ui/          # UI业务域
│           ├── page_objects/       # 页面对象
│           │   ├── __init__.py
│           │   ├── login_page.py
│           │   ├── user_page.py
│           │   └── order_page.py
│           └── step_definitions/   # 步骤定义
│               ├── __init__.py
│               ├── user_steps.py
│               └── order_steps.py
│
├── 📁 nut_test/                    # 第四层：测试用例层
│   ├── conftest.py                 # 全局测试配置
│   └── domain/
│       ├── enterprise/             # 企业域测试
│       │   ├── conftest.py         # 域级配置
│       │   ├── api/                # API测试
│       │   │   ├── test_user_api.py
│       │   │   ├── test_order_api.py
│       │   │   └── test_product_api.py
│       │   ├── scenario/           # 场景测试
│       │   │   ├── test_user_journey.py
│       │   │   └── test_order_flow.py
│       │   ├── schemas/            # 数据模式
│       │   │   ├── user_schema.json
│       │   │   └── order_schema.json
│       │   └── test_data/          # 测试数据
│       │       ├── users.json
│       │       └── orders.json
│       ├── enterprise_ui/          # UI测试域
│       │   ├── conftest.py
│       │   ├── easyui/             # 基础UI测试
│       │   │   ├── test_login.py
│       │   │   ├── test_user.py
│       │   │   └── test_order.py
│       │   └── features/           # BDD特性测试
│       │       ├── user_management.feature
│       │       └── order_process.feature
│       └── open_api/               # 开放API测试
│           ├── conftest.py
│           ├── api/
│           └── scenario/
│
├── 📁 easyuilib/                   # UI自动化库(独立)
│   ├── setup.py
│   └── src/easyui/
│       ├── __init__.py
│       ├── components/             # UI组件
│       ├── locators/               # 定位器
│       └── utils/                  # UI工具
│
├── 📁 perf/                        # 性能测试(独立)
│   ├── k6/
│   ├── prometheus/
│   └── grafana/
│
├── 📁 config/                      # 配置管理
├── 📁 cicd/                        # CI/CD配置
├── 📁 utils/                       # 通用工具
├── 📁 cli/                         # 命令行工具
├── setup.py                        # 顶层安装配置
├── requirements.txt                # 依赖管理
├── develop.sh                      # 开发脚本
└── run_test.sh                     # 测试脚本
```

## 🔄 重构实施步骤

### Step 1: 创建独立包结构
每层都是独立的Python包，支持单独安装和依赖管理

### Step 2: 重新组织代码
- Core层：基础工具和协议封装
- App层：各域的API调用器
- Biz层：业务流程编排和检查
- Test层：按域组织的测试用例

### Step 3: 建立依赖关系
```
nut_test → nut_biz → nut_app → nut_core
```

### Step 4: 统一工具集成
- 脚手架工具 (hamster命令)
- CLI工具集成
- 性能测试集成
- 监控系统集成

## 🎯 重构后的优势

1. **清晰的层次分离**: 每层职责单一，依赖关系清晰
2. **独立包管理**: 每层可独立开发、测试、部署
3. **可扩展性**: 新增域或功能时结构清晰
4. **可维护性**: 代码组织有序，易于维护
5. **工具集成**: 统一的CLI和脚手架工具
6. **性能监控**: 集成K6+Prometheus+Grafana

## 🚀 使用方式

```bash
# 1. 一键开发环境搭建
./develop.sh

# 2. 激活虚拟环境
source nut_venv/bin/activate

# 3. 使用脚手架创建新域
hamster new --domain payment --type api

# 4. 运行测试
pytest nut_test/domain/enterprise/api/

# 5. 运行性能测试
./run_perf.sh

# 6. 查看监控
open http://localhost:3000  # Grafana
```