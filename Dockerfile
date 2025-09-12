# 基于官方多架构镜像，支持 arm64 (M2)
FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100

WORKDIR /app

# 优先安装依赖，利用缓存
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# 拷贝项目所有代码
COPY . /app

# 确保脚本有执行权限（如果用 run_test.sh 执行）
RUN chmod +x /app/run_test.sh || true

# 如需直接跑 pytest，可改成：["pytest", "-q"]
CMD ["bash", "run_test.sh"]