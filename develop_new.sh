#!/bin/bash

# 四层架构测试平台开发环境一键搭建脚本
# Usage: ./develop_new.sh

set -e

echo "🚀 开始搭建四层架构测试平台开发环境..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印彩色信息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 检查Python版本
check_python() {
    print_info "检查Python版本..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
        REQUIRED_VERSION="3.9"
        
        if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then
            print_success "Python版本 $PYTHON_VERSION 满足要求"
        else
            print_error "需要Python 3.9或更高版本，当前版本: $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "未找到Python3，请先安装Python 3.9+"
        exit 1
    fi
}

# 创建虚拟环境
create_venv() {
    print_info "创建虚拟环境..."
    
    if [ -d "nut_venv" ]; then
        print_warning "虚拟环境已存在，跳过创建"
    else
        python3 -m venv nut_venv
        print_success "虚拟环境创建完成"
    fi
}

# 激活虚拟环境
activate_venv() {
    print_info "激活虚拟环境..."
    source nut_venv/bin/activate
    
    # 升级pip
    pip install --upgrade pip setuptools wheel
    print_success "虚拟环境激活完成"
}

# 安装各层依赖
install_layers() {
    print_info "开始安装四层架构组件..."
    
    # 1. 安装Core层（地基层）
    print_info "安装Core层 (nut_core)..."
    cd nut_core && pip install -e . && cd ..
    print_success "Core层安装完成"
    
    # 2. 安装App层（API封装层）  
    print_info "安装App层 (nut_app)..."
    cd nut_app && pip install -e . && cd ..
    print_success "App层安装完成"
    
    # 3. 安装Biz层（业务编排层）
    print_info "安装Biz层 (nut_biz)..."
    cd nut_biz && pip install -e . && cd ..
    print_success "Biz层安装完成"
    
    # 4. 安装UI组件库
    print_info "安装UI组件库 (easyuilib)..."
    cd easyuilib && pip install -e . && cd ..
    print_success "UI组件库安装完成"
    
    # 5. 安装顶层项目
    print_info "安装顶层项目..."
    pip install -e .
    print_success "顶层项目安装完成"
}

# 安装额外依赖
install_extras() {
    print_info "安装额外工具..."
    
    # 性能测试工具
    if command -v k6 &> /dev/null; then
        print_success "K6已安装"
    else
        print_warning "K6未安装，请访问 https://k6.io/docs/getting-started/installation/ 手动安装"
    fi
    
    # 开发工具
    pip install pytest-cov pytest-html black flake8 mypy
    print_success "开发工具安装完成"
}

# 创建配置文件
setup_config() {
    print_info "设置配置文件..."
    
    # 创建默认配置
    if [ ! -f "config/env/config_default.ini" ]; then
        mkdir -p config/env
        cat > config/env/config_default.ini << EOF
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
db = 0

[LOGGING]
level = INFO
file = logs/test.log

[PERFORMANCE]
k6_scripts_path = perf/k6/scripts
prometheus_url = http://localhost:9090
grafana_url = http://localhost:3000
EOF
        print_success "默认配置文件创建完成"
    else
        print_warning "配置文件已存在，跳过创建"
    fi
}

# 初始化目录结构
init_directories() {
    print_info "初始化目录结构..."
    
    # 创建必要的目录
    mkdir -p {logs,reports,test_data}
    mkdir -p perf/k6/{scripts,results}
    mkdir -p nut_test/domain/{enterprise,enterprise_ui,open_api}
    
    print_success "目录结构初始化完成"
}

# 验证安装
verify_installation() {
    print_info "验证安装..."
    
    # 检查Python包
    python -c "import nut_core; print('nut_core:', nut_core.__version__)" || print_error "nut_core导入失败"
    python -c "import nut_app; print('nut_app:', nut_app.__version__)" || print_error "nut_app导入失败"  
    python -c "import nut_biz; print('nut_biz:', nut_biz.__version__)" || print_error "nut_biz导入失败"
    python -c "import easyui; print('easyui: OK')" || print_error "easyui导入失败"
    
    # 检查命令行工具
    if command -v hamster &> /dev/null; then
        print_success "hamster命令可用"
        hamster --version || true
    else
        print_warning "hamster命令不可用，请检查安装"
    fi
    
    print_success "安装验证完成"
}

# 显示使用说明
show_usage() {
    print_success "🎉 四层架构测试平台安装完成！"
    echo
    print_info "快速开始："
    echo "  1. 激活虚拟环境:"
    echo "     source nut_venv/bin/activate"
    echo
    echo "  2. 运行示例测试:"
    echo "     pytest nut_test/domain/enterprise/api/ -v"
    echo
    echo "  3. 启动性能监控:"
    echo "     cd perf && docker-compose up -d"
    echo
    echo "  4. 创建新域:"
    echo "     hamster new --domain payment --type api"
    echo
    echo "  5. 运行性能测试:"
    echo "     ./run_perf.sh"
    echo
    print_info "架构说明："
    echo "  📁 nut_core/   - 核心地基层（配置、协议、数据库、UI基础）"
    echo "  📁 nut_app/    - API封装层（各域的调用器、常量、模型）"
    echo "  📁 nut_biz/    - 业务编排层（流程编排、检查器、页面对象）"
    echo "  📁 nut_test/   - 测试用例层（按域组织的测试用例）"
    echo "  📁 easyuilib/  - UI组件库（独立的UI自动化组件）"
    echo "  📁 perf/       - 性能测试（K6+Prometheus+Grafana）"
    echo
    print_info "更多信息请查看各层的README文档"
}

# 主要执行流程
main() {
    check_python
    create_venv
    activate_venv
    install_layers
    install_extras
    setup_config
    init_directories
    verify_installation
    show_usage
}

# 执行主函数
main