# CI/CD - 持续集成和部署

## 概述

CI/CD 模块提供完整的持续集成和持续部署解决方案，支持自动化构建、测试、部署流程，确保代码质量和交付效率。

## 技术栈

- **GitHub Actions**: 主要的 CI/CD 平台
- **Docker**: 容器化部署
- **pytest**: 自动化测试执行
- **SonarQube**: 代码质量分析（可选）
- **Kubernetes**: 生产环境部署（可选）

## 核心功能

### 1. 持续集成 (CI)

#### GitHub Actions Workflow

```yaml
# .github/workflows/ci.yml
name: CI Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: root
          MYSQL_DATABASE: test_db
        ports:
          - 3306:3306
        options: --health-cmd="mysqladmin ping" --health-interval=10s --health-timeout=5s --health-retries=3
      
      redis:
        image: redis:6
        ports:
          - 6379:6379
        options: --health-cmd "redis-cli ping" --health-interval 10s --health-timeout 5s --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: '3.9'
    
    - name: Cache dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
        restore-keys: |
          ${{ runner.os }}-pip-
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest-cov pytest-xdist
    
    - name: Lint with flake8
      run: |
        pip install flake8
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
    
    - name: Run tests with pytest
      run: |
        pytest tests/ -v --cov=core --cov=app --cov=biz --cov-report=xml --cov-report=html -n auto
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
        fail_ci_if_error: true
```

### 2. 代码质量检查

#### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
  
  - repo: https://github.com/psf/black
    rev: 22.10.0
    hooks:
      - id: black
        language_version: python3
  
  - repo: https://github.com/PyCQA/flake8
    rev: 5.0.4
    hooks:
      - id: flake8
  
  - repo: https://github.com/PyCQA/isort
    rev: 5.11.4
    hooks:
      - id: isort
```

#### 代码质量配置

```ini
# setup.cfg
[flake8]
max-line-length = 127
exclude = .git,__pycache__,build,dist,nut_venv
ignore = E203,W503,F401

[isort]
profile = black
multi_line_output = 3
line_length = 127
known_first_party = core,app,biz,utils
known_third_party = pytest,requests,redis,pymysql

[tool:pytest]
testpaths = tests
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
```

### 3. 持续部署 (CD)

#### 部署 Pipeline

```yaml
# .github/workflows/cd.yml
name: CD Pipeline

on:
  push:
    branches: [ main ]
    tags: [ 'v*' ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    needs: test
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Login to Container Registry
      uses: docker/login-action@v2
      with:
        registry: ghcr.io
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Build and push Docker image
      uses: docker/build-push-action@v3
      with:
        context: .
        push: true
        tags: |
          ghcr.io/${{ github.repository }}/test-platform:latest
          ghcr.io/${{ github.repository }}/test-platform:${{ github.sha }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
    
    - name: Deploy to staging
      if: github.ref == 'refs/heads/main'
      run: |
        # 部署到预发布环境的脚本
        echo "Deploying to staging environment"
    
    - name: Deploy to production
      if: startsWith(github.ref, 'refs/tags/v')
      run: |
        # 部署到生产环境的脚本
        echo "Deploying to production environment"
```

### 4. Docker 化

#### Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 应用代码
COPY . .

# 创建非 root 用户
RUN groupadd -r testuser && useradd -r -g testuser testuser
RUN chown -R testuser:testuser /app
USER testuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# 启动命令
CMD ["python", "-m", "pytest", "tests/"]
```

#### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  test-platform:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENV=production
      - DATABASE_URL=mysql://user:password@mysql:3306/testdb
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - mysql
      - redis
    networks:
      - test-network
    volumes:
      - ./logs:/app/logs
      - ./results:/app/results
    restart: unless-stopped

  mysql:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=rootpassword
      - MYSQL_DATABASE=testdb
      - MYSQL_USER=user
      - MYSQL_PASSWORD=password
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./config/mysql:/etc/mysql/conf.d
    networks:
      - test-network
    restart: unless-stopped

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
      - ./config/redis.conf:/usr/local/etc/redis/redis.conf
    command: redis-server /usr/local/etc/redis/redis.conf
    networks:
      - test-network
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./config/nginx:/etc/nginx/conf.d
      - ./ssl:/etc/ssl/certs
    depends_on:
      - test-platform
    networks:
      - test-network
    restart: unless-stopped

volumes:
  mysql_data:
  redis_data:

networks:
  test-network:
    driver: bridge
```

## 环境管理

### 1. 多环境配置

```bash
# 开发环境
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# 测试环境
docker-compose -f docker-compose.yml -f docker-compose.test.yml up

# 生产环境
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
```

### 2. 环境变量管理

```bash
# .env.example
ENV=development
DEBUG=true

# Database
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_USER=root
DATABASE_PASSWORD=password
DATABASE_NAME=test_platform

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# API Configuration
API_BASE_URL=http://localhost:8000
API_TIMEOUT=30

# Logging
LOG_LEVEL=INFO
LOG_FILE=/app/logs/app.log

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret-here

# Feature Flags
ENABLE_PERFORMANCE_MONITORING=true
ENABLE_DETAILED_LOGGING=false
```

### 3. Kubernetes 部署

```yaml
# k8s/deployment.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: test-platform
  labels:
    app: test-platform
spec:
  replicas: 3
  selector:
    matchLabels:
      app: test-platform
  template:
    metadata:
      labels:
        app: test-platform
    spec:
      containers:
      - name: test-platform
        image: ghcr.io/your-org/test-platform:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENV
          value: "production"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: test-platform-secrets
              key: database-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: test-platform-service
spec:
  selector:
    app: test-platform
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
```

## 部署脚本

### 1. 自动化部署脚本

```bash
#!/bin/bash
# deploy.sh

set -e

ENV=${1:-staging}
VERSION=${2:-latest}

echo "Deploying test-platform to $ENV environment with version $VERSION"

# 构建镜像
docker build -t test-platform:$VERSION .

# 标记镜像
docker tag test-platform:$VERSION ghcr.io/your-org/test-platform:$VERSION

# 推送镜像
docker push ghcr.io/your-org/test-platform:$VERSION

# 部署到不同环境
case $ENV in
  "staging")
    kubectl apply -f k8s/staging/
    kubectl set image deployment/test-platform test-platform=ghcr.io/your-org/test-platform:$VERSION -n staging
    ;;
  "production")
    kubectl apply -f k8s/production/
    kubectl set image deployment/test-platform test-platform=ghcr.io/your-org/test-platform:$VERSION -n production
    ;;
  *)
    echo "Unknown environment: $ENV"
    exit 1
    ;;
esac

# 等待部署完成
kubectl rollout status deployment/test-platform -n $ENV

echo "Deployment completed successfully!"
```

### 2. 回滚脚本

```bash
#!/bin/bash
# rollback.sh

ENV=${1:-staging}

echo "Rolling back test-platform in $ENV environment"

# 回滚到上一个版本
kubectl rollout undo deployment/test-platform -n $ENV

# 等待回滚完成
kubectl rollout status deployment/test-platform -n $ENV

echo "Rollback completed successfully!"
```

## 监控和告警

### 1. 健康检查

```python
# health_check.py
from flask import Flask, jsonify
import redis
import pymysql
from datetime import datetime

app = Flask(__name__)

@app.route('/health')
def health():
    """健康检查端点"""
    status = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'checks': {}
    }
    
    # 数据库连接检查
    try:
        # MySQL 检查
        conn = pymysql.connect(host='mysql', user='user', password='password', database='testdb')
        conn.ping()
        conn.close()
        status['checks']['database'] = 'healthy'
    except Exception as e:
        status['checks']['database'] = f'unhealthy: {str(e)}'
        status['status'] = 'unhealthy'
    
    # Redis 连接检查
    try:
        r = redis.Redis(host='redis', port=6379, db=0)
        r.ping()
        status['checks']['redis'] = 'healthy'
    except Exception as e:
        status['checks']['redis'] = f'unhealthy: {str(e)}'
        status['status'] = 'unhealthy'
    
    return jsonify(status), 200 if status['status'] == 'healthy' else 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
```

### 2. 监控配置

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'test-platform'
    static_configs:
      - targets: ['test-platform:8000']
    metrics_path: /metrics
    scrape_interval: 30s

  - job_name: 'mysql'
    static_configs:
      - targets: ['mysql-exporter:9104']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
```

## 最佳实践

### 1. 版本管理

- 使用语义化版本控制 (Semantic Versioning)
- 为每个发布创建 Git 标签
- 维护详细的变更日志

### 2. 分支策略

```
main (生产)
  ├── develop (开发)
  │   ├── feature/new-feature
  │   └── bugfix/fix-issue
  └── hotfix/critical-fix
```

### 3. 部署策略

- **蓝绿部署**: 减少停机时间
- **金丝雀发布**: 逐步推出新版本
- **滚动更新**: Kubernetes 默认策略

### 4. 安全实践

- 使用镜像扫描工具检查漏洞
- 定期更新基础镜像
- 使用非 root 用户运行容器
- 管理敏感信息使用 Secrets

## 故障排除

### 常见问题

1. **构建失败**: 检查依赖版本和构建环境
2. **测试失败**: 确保测试环境配置正确
3. **部署超时**: 检查资源限制和网络连接
4. **健康检查失败**: 验证依赖服务状态

### 调试命令

```bash
# 查看 Pod 日志
kubectl logs -f deployment/test-platform -n staging

# 进入容器调试
kubectl exec -it deployment/test-platform -n staging -- /bin/bash

# 查看部署状态
kubectl describe deployment test-platform -n staging

# 查看服务状态
kubectl get svc test-platform-service -n staging
```
