# Utils - 工具集

## 概述

Utils 模块提供了一系列通用工具和辅助函数，用于支持整个测试平台的各种功能需求。这些工具独立于具体的业务逻辑，可以在不同的层次和模块中复用。

## 核心功能

### 1. 数据生成工具

生成各种类型的测试数据，支持自动化测试的数据需求。

```python
# utils/data_generator.py
import random
import string
from datetime import datetime, timedelta

class DataGenerator:
    @staticmethod
    def generate_user_data(count=1):
        """生成用户测试数据"""
        users = []
        for i in range(count):
            user = {
                "username": f"testuser_{random.randint(1000, 9999)}",
                "email": f"test{random.randint(100, 999)}@example.com",
                "phone": f"1{random.randint(3000000000, 9999999999)}",
                "age": random.randint(18, 65),
                "created_at": datetime.now().isoformat()
            }
            users.append(user)
        return users[0] if count == 1 else users
    
    @staticmethod
    def generate_order_data():
        """生成订单测试数据"""
        return {
            "product_id": f"P{random.randint(1000, 9999)}",
            "quantity": random.randint(1, 10),
            "unit_price": round(random.uniform(10.0, 1000.0), 2),
            "order_date": datetime.now().isoformat()
        }
    
    @staticmethod
    def generate_random_string(length=10, chars=string.ascii_letters):
        """生成随机字符串"""
        return ''.join(random.choice(chars) for _ in range(length))
```

### 2. 文件处理工具

处理各种文件格式的读写操作。

```python
# utils/file_handler.py
import json
import csv
import yaml
import os

class FileHandler:
    @staticmethod
    def read_json(file_path):
        """读取 JSON 文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def write_json(data, file_path):
        """写入 JSON 文件"""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    @staticmethod
    def read_csv(file_path):
        """读取 CSV 文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)
    
    @staticmethod
    def write_csv(data, file_path, fieldnames=None):
        """写入 CSV 文件"""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        if not fieldnames and data:
            fieldnames = data[0].keys()
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
    
    @staticmethod
    def read_yaml(file_path):
        """读取 YAML 文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
```

### 3. 日期时间工具

处理日期时间相关的操作。

```python
# utils/datetime_helper.py
from datetime import datetime, timedelta
import time

class DateTimeHelper:
    @staticmethod
    def get_current_timestamp():
        """获取当前时间戳"""
        return int(time.time())
    
    @staticmethod
    def get_current_datetime(format="%Y-%m-%d %H:%M:%S"):
        """获取格式化的当前时间"""
        return datetime.now().strftime(format)
    
    @staticmethod
    def add_days(date_str, days, date_format="%Y-%m-%d"):
        """日期加天数"""
        date_obj = datetime.strptime(date_str, date_format)
        new_date = date_obj + timedelta(days=days)
        return new_date.strftime(date_format)
    
    @staticmethod
    def get_date_range(start_date, end_date, date_format="%Y-%m-%d"):
        """获取日期范围"""
        start = datetime.strptime(start_date, date_format)
        end = datetime.strptime(end_date, date_format)
        
        dates = []
        current = start
        while current <= end:
            dates.append(current.strftime(date_format))
            current += timedelta(days=1)
        
        return dates
```

### 4. 加密解密工具

提供常用的加密解密功能。

```python
# utils/crypto_helper.py
import hashlib
import base64
import hmac

class CryptoHelper:
    @staticmethod
    def md5_hash(text):
        """MD5 哈希"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    @staticmethod
    def sha256_hash(text):
        """SHA256 哈希"""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    @staticmethod
    def base64_encode(text):
        """Base64 编码"""
        return base64.b64encode(text.encode('utf-8')).decode('utf-8')
    
    @staticmethod
    def base64_decode(encoded_text):
        """Base64 解码"""
        return base64.b64decode(encoded_text).decode('utf-8')
    
    @staticmethod
    def hmac_sha256(key, message):
        """HMAC-SHA256 签名"""
        return hmac.new(
            key.encode('utf-8'), 
            message.encode('utf-8'), 
            hashlib.sha256
        ).hexdigest()
```

### 5. HTTP 工具

HTTP 相关的辅助工具。

```python
# utils/http_helper.py
import requests
from urllib.parse import urljoin, urlparse

class HttpHelper:
    @staticmethod
    def is_valid_url(url):
        """验证 URL 是否有效"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    @staticmethod
    def join_url(base_url, path):
        """拼接 URL"""
        return urljoin(base_url, path)
    
    @staticmethod
    def get_response_size(response):
        """获取响应大小（字节）"""
        return len(response.content)
    
    @staticmethod
    def extract_headers(response, header_names):
        """提取指定的响应头"""
        headers = {}
        for name in header_names:
            headers[name] = response.headers.get(name)
        return headers
```

### 6. 日志工具

统一的日志处理工具。

```python
# utils/logger.py
import logging
import os
from datetime import datetime

class Logger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.logger = logging.getLogger('test_platform')
        self.logger.setLevel(logging.INFO)
        
        # 创建日志目录
        log_dir = 'logs'
        os.makedirs(log_dir, exist_ok=True)
        
        # 文件处理器
        log_file = os.path.join(log_dir, f"test_{datetime.now().strftime('%Y%m%d')}.log")
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self._initialized = True
    
    def info(self, message):
        self.logger.info(message)
    
    def error(self, message):
        self.logger.error(message)
    
    def warning(self, message):
        self.logger.warning(message)
    
    def debug(self, message):
        self.logger.debug(message)
```

### 7. 数据库工具

数据库连接和操作的辅助工具。

```python
# utils/db_helper.py
import pymysql
from contextlib import contextmanager

class DatabaseHelper:
    def __init__(self, host, port, user, password, database):
        self.config = {
            'host': host,
            'port': port,
            'user': user,
            'password': password,
            'database': database,
            'charset': 'utf8mb4'
        }
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接"""
        conn = None
        try:
            conn = pymysql.connect(**self.config)
            yield conn
        finally:
            if conn:
                conn.close()
    
    def execute_query(self, sql, params=None):
        """执行查询"""
        with self.get_connection() as conn:
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute(sql, params)
            return cursor.fetchall()
    
    def execute_update(self, sql, params=None):
        """执行更新"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            affected_rows = cursor.execute(sql, params)
            conn.commit()
            return affected_rows
```

## 使用示例

### 数据生成示例

```python
from utils.data_generator import DataGenerator

# 生成单个用户数据
user_data = DataGenerator.generate_user_data()
print(user_data)

# 生成多个用户数据
users = DataGenerator.generate_user_data(count=5)
for user in users:
    print(user['username'])

# 生成订单数据
order_data = DataGenerator.generate_order_data()
print(f"Order: {order_data}")
```

### 文件处理示例

```python
from utils.file_handler import FileHandler

# 处理 JSON 文件
test_data = {"users": [{"name": "test", "age": 25}]}
FileHandler.write_json(test_data, "test_data/users.json")
loaded_data = FileHandler.read_json("test_data/users.json")

# 处理 CSV 文件
csv_data = [
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 25}
]
FileHandler.write_csv(csv_data, "test_data/users.csv")
loaded_csv = FileHandler.read_csv("test_data/users.csv")
```

### 日志使用示例

```python
from utils.logger import Logger

logger = Logger()
logger.info("测试开始执行")
logger.warning("这是一个警告信息")
logger.error("测试执行失败")
```

### 加密工具示例

```python
from utils.crypto_helper import CryptoHelper

# 哈希处理
text = "test_password"
md5_result = CryptoHelper.md5_hash(text)
sha256_result = CryptoHelper.sha256_hash(text)

# Base64 编码
encoded = CryptoHelper.base64_encode(text)
decoded = CryptoHelper.base64_decode(encoded)

# HMAC 签名
signature = CryptoHelper.hmac_sha256("secret_key", "message")
```

## 配置管理

### 工具配置文件

```yaml
# utils/config/utils_config.yml
data_generator:
  default_user_count: 10
  email_domain: "test.example.com"
  phone_prefix: "1"

file_handler:
  default_encoding: "utf-8"
  backup_enabled: true
  max_file_size: "100MB"

logger:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file_rotation: "daily"
  max_files: 30

crypto:
  default_hash_algorithm: "sha256"
  encoding: "utf-8"
```

## 最佳实践

### 1. 工具类设计

```python
class UtilityBase:
    """工具类基类"""
    
    @classmethod
    def validate_input(cls, *args, **kwargs):
        """输入验证"""
        pass
    
    @classmethod
    def handle_error(cls, error, default_return=None):
        """错误处理"""
        logger = Logger()
        logger.error(f"工具执行错误: {str(error)}")
        return default_return
```

### 2. 异常处理

```python
from utils.logger import Logger

def safe_execute(func):
    """安全执行装饰器"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger = Logger()
            logger.error(f"函数 {func.__name__} 执行失败: {str(e)}")
            raise
    return wrapper

@safe_execute
def risky_operation():
    # 可能出错的操作
    pass
```

### 3. 缓存机制

```python
# utils/cache_helper.py
import functools
import time

def cache_result(expire_time=3600):
    """结果缓存装饰器"""
    cache = {}
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = str(args) + str(sorted(kwargs.items()))
            current_time = time.time()
            
            if key in cache:
                result, timestamp = cache[key]
                if current_time - timestamp < expire_time:
                    return result
            
            result = func(*args, **kwargs)
            cache[key] = (result, current_time)
            return result
        return wrapper
    return decorator
```

## 扩展指南

### 添加新的工具类

1. 创建新的工具文件：

```python
# utils/new_helper.py
class NewHelper:
    @staticmethod
    def new_function():
        """新功能描述"""
        pass
```

2. 在 `__init__.py` 中导入：

```python
# utils/__init__.py
from .data_generator import DataGenerator
from .file_handler import FileHandler
from .new_helper import NewHelper

__all__ = ['DataGenerator', 'FileHandler', 'NewHelper']
```

### 集成第三方库

```python
# utils/third_party_helper.py
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

class DataFrameHelper:
    @staticmethod
    def is_available():
        return PANDAS_AVAILABLE
    
    @staticmethod
    def create_dataframe(data):
        if not PANDAS_AVAILABLE:
            raise ImportError("pandas 未安装")
        return pd.DataFrame(data)
```

## 目录结构

```
utils/
├── __init__.py
├── data_generator.py       # 数据生成工具
├── file_handler.py         # 文件处理工具
├── datetime_helper.py      # 日期时间工具
├── crypto_helper.py        # 加密解密工具
├── http_helper.py          # HTTP 工具
├── logger.py               # 日志工具
├── db_helper.py           # 数据库工具
├── cache_helper.py        # 缓存工具
└── config/
    └── utils_config.yml   # 工具配置文件
```
