# CLI - 命令行工具

## 概述

CLI 模块提供命令行界面，方便用户通过命令行执行各种测试任务，管理测试环境，查看测试结果等。基于 Click 框架构建，提供友好的命令行体验。

## 核心功能

### 1. 测试执行命令

#### 运行功能测试

```bash
# 运行所有测试
test-platform test run

# 运行指定模块的测试
test-platform test run --module core
test-platform test run --module app
test-platform test run --module biz

# 运行指定环境的测试
test-platform test run --env test
test-platform test run --env staging

# 运行指定标签的测试
test-platform test run --tags smoke
test-platform test run --tags regression

# 并发运行测试
test-platform test run --parallel 4

# 生成测试报告
test-platform test run --report html
test-platform test run --report json
```

#### 运行性能测试

```bash
# 运行负载测试
test-platform perf run --type load --users 100 --duration 300s

# 运行压力测试
test-platform perf run --type stress --users 500 --ramp-up 120s

# 运行特定场景
test-platform perf run --script user_journey.js

# 实时监控模式
test-platform perf run --script load_test.js --monitor

# 生成性能报告
test-platform perf run --script stress_test.js --report dashboard
```

### 2. 环境管理命令

#### 环境配置

```bash
# 列出所有环境
test-platform env list

# 查看环境详情
test-platform env show test

# 切换环境
test-platform env switch staging

# 验证环境配置
test-platform env validate test

# 创建新环境配置
test-platform env create local --template default
```

#### 服务管理

```bash
# 启动测试服务
test-platform service start

# 停止测试服务
test-platform service stop

# 重启测试服务
test-platform service restart

# 查看服务状态
test-platform service status

# 查看服务日志
test-platform service logs --tail 100
```

### 3. 数据管理命令

#### 测试数据

```bash
# 生成测试数据
test-platform data generate --type user --count 100
test-platform data generate --type order --count 50

# 导入测试数据
test-platform data import users.json
test-platform data import --file orders.csv --type order

# 导出测试数据
test-platform data export --type user --format json
test-platform data export --type order --format csv

# 清理测试数据
test-platform data cleanup --type user --older-than 7d
test-platform data cleanup --all
```

#### 数据库操作

```bash
# 数据库迁移
test-platform db migrate

# 重置数据库
test-platform db reset

# 备份数据库
test-platform db backup --file backup_$(date +%Y%m%d).sql

# 恢复数据库
test-platform db restore --file backup_20231201.sql

# 查看数据库状态
test-platform db status
```

### 4. 报告和分析命令

#### 测试报告

```bash
# 生成测试报告
test-platform report generate --type summary
test-platform report generate --type detailed --format html

# 查看最近的测试结果
test-platform report show --latest
test-platform report show --date 2023-12-01

# 比较测试结果
test-platform report compare --base v1.0 --current v1.1

# 导出报告
test-platform report export --format pdf --output report.pdf
```

#### 性能分析

```bash
# 分析性能测试结果
test-platform analysis perf --file results/load_test.json

# 趋势分析
test-platform analysis trend --metric response_time --days 30

# 生成性能基准
test-platform analysis baseline --create

# 与基准对比
test-platform analysis baseline --compare
```

## CLI 实现示例

### 1. 主命令结构

```python
# cli/main.py
import click
from cli.commands import test, perf, env, service, data, db, report, analysis

@click.group()
@click.version_option(version='1.0.0')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--config', '-c', type=click.Path(), help='Config file path')
@click.pass_context
def cli(ctx, verbose, config):
    """Test Platform Command Line Interface"""
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['config'] = config

# 注册子命令
cli.add_command(test.test)
cli.add_command(perf.perf)
cli.add_command(env.env)
cli.add_command(service.service)
cli.add_command(data.data)
cli.add_command(db.db)
cli.add_command(report.report)
cli.add_command(analysis.analysis)

if __name__ == '__main__':
    cli()
```

### 2. 测试命令实现

```python
# cli/commands/test.py
import click
import subprocess
from pathlib import Path

@click.group()
def test():
    """Test execution commands"""
    pass

@test.command()
@click.option('--module', '-m', help='Test module to run')
@click.option('--env', '-e', default='default', help='Test environment')
@click.option('--tags', '-t', help='Test tags to filter')
@click.option('--parallel', '-p', type=int, help='Number of parallel processes')
@click.option('--report', '-r', type=click.Choice(['html', 'json', 'junit']), help='Report format')
@click.option('--output', '-o', help='Output directory')
@click.pass_context
def run(ctx, module, env, tags, parallel, report, output):
    """Run functional tests"""
    verbose = ctx.obj.get('verbose', False)
    
    # 构建 pytest 命令
    cmd = ['pytest']
    
    if module:
        cmd.append(f'tests/{module}/')
    else:
        cmd.append('tests/')
    
    if tags:
        cmd.extend(['-m', tags])
    
    if parallel:
        cmd.extend(['-n', str(parallel)])
    
    if report:
        if report == 'html':
            cmd.extend(['--html=reports/report.html', '--self-contained-html'])
        elif report == 'json':
            cmd.extend(['--json-report', '--json-report-file=reports/report.json'])
        elif report == 'junit':
            cmd.extend(['--junit-xml=reports/report.xml'])
    
    if verbose:
        cmd.append('-v')
    
    # 设置环境变量
    import os
    env_vars = os.environ.copy()
    env_vars['TEST_ENV'] = env
    
    # 执行命令
    click.echo(f"Running command: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, env=env_vars, check=False)
        if result.returncode == 0:
            click.echo(click.style("✓ Tests completed successfully", fg='green'))
        else:
            click.echo(click.style("✗ Tests failed", fg='red'))
        return result.returncode
    except Exception as e:
        click.echo(click.style(f"Error running tests: {e}", fg='red'))
        return 1
```

### 3. 性能测试命令

```python
# cli/commands/perf.py
import click
import subprocess
import json
from pathlib import Path

@click.group()
def perf():
    """Performance testing commands"""
    pass

@perf.command()
@click.option('--type', 't', type=click.Choice(['load', 'stress', 'spike']), 
              default='load', help='Test type')
@click.option('--users', '-u', type=int, default=10, help='Number of virtual users')
@click.option('--duration', '-d', default='30s', help='Test duration')
@click.option('--ramp-up', default='10s', help='Ramp-up time')
@click.option('--script', '-s', help='K6 script file')
@click.option('--monitor', is_flag=True, help='Enable monitoring')
@click.option('--report', type=click.Choice(['console', 'json', 'dashboard']), 
              default='console', help='Report type')
@click.pass_context
def run(ctx, type, users, duration, ramp_up, script, monitor, report):
    """Run performance tests"""
    verbose = ctx.obj.get('verbose', False)
    
    if script:
        script_path = Path(f'perf/k6/scripts/{script}')
    else:
        script_path = Path(f'perf/k6/scripts/{type}_test.js')
    
    if not script_path.exists():
        click.echo(click.style(f"Script not found: {script_path}", fg='red'))
        return 1
    
    # 构建 K6 命令
    cmd = ['k6', 'run']
    
    # 添加输出格式
    if report == 'json':
        output_file = f'perf/k6/results/{type}_test_{click.DateTime().now().strftime("%Y%m%d_%H%M%S")}.json'
        cmd.extend(['--out', f'json={output_file}'])
    elif report == 'dashboard':
        cmd.extend(['--out', 'influxdb=http://localhost:8086/k6'])
    
    # 添加监控
    if monitor:
        cmd.extend(['--out', 'prometheus'])
    
    # 设置环境变量
    env_vars = {
        'K6_VUS': str(users),
        'K6_DURATION': duration,
        'K6_RAMP_UP': ramp_up
    }
    
    cmd.append(str(script_path))
    
    click.echo(f"Running performance test: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, env=env_vars)
        if result.returncode == 0:
            click.echo(click.style("✓ Performance test completed", fg='green'))
        else:
            click.echo(click.style("✗ Performance test failed", fg='red'))
        return result.returncode
    except Exception as e:
        click.echo(click.style(f"Error running performance test: {e}", fg='red'))
        return 1
```

### 4. 环境管理命令

```python
# cli/commands/env.py
import click
import yaml
from pathlib import Path

@click.group()
def env():
    """Environment management commands"""
    pass

@env.command()
def list():
    """List all available environments"""
    config_dir = Path('config/env')
    if not config_dir.exists():
        click.echo("No environment configurations found")
        return
    
    configs = list(config_dir.glob('config_*.ini'))
    click.echo("Available environments:")
    for config in configs:
        env_name = config.stem.replace('config_', '')
        click.echo(f"  - {env_name}")

@env.command()
@click.argument('environment')
def show(environment):
    """Show environment configuration"""
    config_file = Path(f'config/env/config_{environment}.ini')
    if not config_file.exists():
        click.echo(click.style(f"Environment '{environment}' not found", fg='red'))
        return 1
    
    with open(config_file) as f:
        content = f.read()
        click.echo(f"Configuration for environment '{environment}':")
        click.echo(content)

@env.command()
@click.argument('environment')
def switch(environment):
    """Switch to specified environment"""
    config_file = Path(f'config/env/config_{environment}.ini')
    if not config_file.exists():
        click.echo(click.style(f"Environment '{environment}' not found", fg='red'))
        return 1
    
    # 创建符号链接或设置环境变量
    current_env_file = Path('.current_env')
    with open(current_env_file, 'w') as f:
        f.write(environment)
    
    click.echo(click.style(f"✓ Switched to environment: {environment}", fg='green'))

@env.command()
@click.argument('environment')
def validate(environment):
    """Validate environment configuration"""
    from core.config.config_loader import ConfigLoader
    
    try:
        config = ConfigLoader(env=environment)
        # 验证必要的配置项
        api_url = config.get('API', 'base_url')
        if not api_url:
            raise ValueError("Missing API base_url")
        
        click.echo(click.style(f"✓ Environment '{environment}' is valid", fg='green'))
        click.echo(f"  API URL: {api_url}")
        
    except Exception as e:
        click.echo(click.style(f"✗ Environment validation failed: {e}", fg='red'))
        return 1
```

### 5. 数据管理命令

```python
# cli/commands/data.py
import click
import json
from utils.data_generator import DataGenerator
from utils.file_handler import FileHandler

@click.group()
def data():
    """Data management commands"""
    pass

@data.command()
@click.option('--type', 't', type=click.Choice(['user', 'order']), 
              required=True, help='Data type to generate')
@click.option('--count', '-c', type=int, default=10, help='Number of records')
@click.option('--output', '-o', help='Output file path')
@click.option('--format', 'fmt', type=click.Choice(['json', 'csv']), 
              default='json', help='Output format')
def generate(type, count, output, fmt):
    """Generate test data"""
    generator = DataGenerator()
    
    if type == 'user':
        data = generator.generate_user_data(count=count)
    elif type == 'order':
        data = [generator.generate_order_data() for _ in range(count)]
    
    if not output:
        output = f'test_data/{type}_data.{fmt}'
    
    if fmt == 'json':
        FileHandler.write_json(data, output)
    elif fmt == 'csv':
        FileHandler.write_csv(data, output)
    
    click.echo(click.style(f"✓ Generated {count} {type} records to {output}", fg='green'))

@data.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--type', help='Data type')
def import_data(file_path, type):
    """Import test data from file"""
    try:
        if file_path.endswith('.json'):
            data = FileHandler.read_json(file_path)
        elif file_path.endswith('.csv'):
            data = FileHandler.read_csv(file_path)
        else:
            click.echo(click.style("Unsupported file format", fg='red'))
            return 1
        
        # 这里可以添加数据导入到数据库的逻辑
        click.echo(click.style(f"✓ Imported {len(data)} records from {file_path}", fg='green'))
        
    except Exception as e:
        click.echo(click.style(f"✗ Import failed: {e}", fg='red'))
        return 1
```

## 配置文件

### CLI 配置

```yaml
# cli/config/cli_config.yml
default_settings:
  verbose: false
  parallel_jobs: 4
  report_format: html
  output_dir: reports

environments:
  default: config_default.ini
  test: config_test.ini
  staging: config_staging.ini
  production: config_production.ini

k6_settings:
  default_vus: 10
  default_duration: "30s"
  default_ramp_up: "10s"
  scripts_dir: "perf/k6/scripts"
  results_dir: "perf/k6/results"

report_settings:
  template_dir: "templates"
  output_formats:
    - html
    - json
    - pdf
    - junit
```

## 安装和使用

### 1. 安装

```bash
# 开发模式安装
pip install -e .

# 生产安装
pip install test-platform-cli
```

### 2. 自动补全

```bash
# Bash
eval "$(_TEST_PLATFORM_COMPLETE=bash_source test-platform)"

# Zsh
eval "$(_TEST_PLATFORM_COMPLETE=zsh_source test-platform)"

# Fish
eval (env _TEST_PLATFORM_COMPLETE=fish_source test-platform)
```

### 3. 配置文件

```bash
# 创建用户配置目录
mkdir -p ~/.test-platform

# 复制默认配置
cp cli/config/cli_config.yml ~/.test-platform/config.yml
```

## 扩展功能

### 1. 插件系统

```python
# cli/plugins/__init__.py
import pkg_resources

def load_plugins():
    """加载插件"""
    plugins = {}
    for entry_point in pkg_resources.iter_entry_points('test_platform.plugins'):
        plugin = entry_point.load()
        plugins[entry_point.name] = plugin
    return plugins
```

### 2. 自定义命令

```python
# cli/commands/custom.py
import click

@click.group()
def custom():
    """Custom commands"""
    pass

@custom.command()
@click.argument('name')
def hello(name):
    """Say hello to someone"""
    click.echo(f"Hello, {name}!")
```

## 最佳实践

1. **命令设计**: 遵循 Unix 命令行工具的设计原则
2. **错误处理**: 提供清晰的错误信息和退出码
3. **输出格式**: 支持机器可读和人类可读的输出格式
4. **配置管理**: 支持多级配置（系统、用户、项目）
5. **进度显示**: 对长时间运行的操作显示进度条
6. **日志记录**: 记录命令执行历史和结果
