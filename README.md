# Test Platform

## 项目简介

Test Platform 是一个基于分层架构的自动化测试平台，采用 Core-App-Biz 三层架构设计，支持企业级应用和开放 API 的自动化测试。

## 架构设计

```
┌─────────────────┐
│   Biz Layer     │  业务编排层 - 组合 API 构建完整业务流程
├─────────────────┤
│   App Layer     │  API 封装层 - 对各类 API 进行标准化封装
├─────────────────┤
│   Core Layer    │  系统地基层 - 提供基础服务和工具组件
└─────────────────┘
```

### 三层架构说明

- **Core Layer（系统地基）**: 提供配置管理、HTTP 客户端、数据库连接、消息队列、断言工具等基础服务
- **App Layer（API 封装）**: 对企业 API 和开放 API 进行封装，提供标准化的调用接口
- **Biz Layer（业务编排）**: 组合多个 API 调用，构建完整的业务测试流程

## 技术栈

- **Python 3.9+**: 主要编程语言
- **pytest**: 测试框架
- **requests**: HTTP 客户端库
- **playwright**: UI 自动化测试
- **MySQL**: 数据库支持
- **Redis**: 缓存和消息队列
- **Elasticsearch**: 搜索和分析
- **Docker**: 容器化部署

## 快速开始

### 环境准备

```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 激活虚拟环境（可选）
source nut_venv/bin/activate

# 配置环境变量
cp config/env/config_default.ini config/env/config_local.ini
# 修改 config_local.ini 中的配置信息
```

### 运行测试

```bash
# 运行所有测试
./run_test.sh

# 运行性能测试
./run_perf.sh

# 开发模式启动
./develop.sh
```

### Docker 部署

```bash
# 构建镜像
docker build -t test-platform .

# 使用 docker-compose 启动
docker-compose up -d
```

## 目录结构

```
test_platform/
├── core/           # 系统地基层
├── app/            # API 封装层
├── biz/            # 业务编排层
├── test/           # 测试用例
├── perf/           # 性能测试
├── utils/          # 工具集
├── cli/            # 命令行工具
├── cicd/           # CI/CD 配置
├── config/         # 配置文件
└── docs/           # 文档目录
```

## 开发指南

每个层次都有独立的 README 文档，详细说明该层的职责和使用方法：

- [Core Layer 说明](core/src/core/README.md)
- [App Layer 说明](app/src/app/README.md)
- [Biz Layer 说明](biz/src/biz/README.md)
- [性能测试说明](perf/README.md)
- [工具集说明](utils/README.md)

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交代码
4. 发起 Pull Request
