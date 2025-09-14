
"""MySQL数据库测试脚本"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# 正确的导入语句
from core.db.mysql_handler import MySQLHandler
from core.config.config_loader import ConfigLoader
from core.base_util.logger import get_logger

# 获取日志记录器
logger = get_logger(__name__)

def test_mysql_connection():
    """测试MySQL连接"""
    print("=== 测试MySQL连接 ===")
    
    # 方法1: 使用配置文件
    try:
        # 指定项目根目录下的config目录
        project_root = Path(__file__).parent.parent.parent.parent
        config_dir = project_root / "config"
        
        config_loader = ConfigLoader(config_dir=str(config_dir))
        config = config_loader.get_all_config()
        
        # 从配置文件获取MySQL配置
        mysql_config = None
        
        # 尝试从不同的配置源获取MySQL配置
        if 'DATABASE' in config:
            # 从INI文件的DATABASE section获取
            db_section = config['DATABASE']
            mysql_config = {
                'host': db_section.get('host', 'localhost'),
                'port': int(db_section.get('port', 3306)),
                'user': db_section.get('user', 'root'),
                'password': db_section.get('password', 'password'),
                'database': db_section.get('database', 'test_db'),
                'charset': db_section.get('charset', 'utf8mb4')
            }
            print(f"从DATABASE配置获取MySQL配置: {mysql_config}")
        elif 'db' in config:
            # 从INI文件的db section获取
            db_section = config['db']
            mysql_config = {
                'host': db_section.get('host', 'localhost'),
                'port': int(db_section.get('port', 3306)),
                'user': db_section.get('user', 'root'),
                'password': db_section.get('password', 'password'),
                'database': db_section.get('database', 'test_db'),
                'charset': db_section.get('charset', 'utf8mb4')
            }
            print(f"从db配置获取MySQL配置: {mysql_config}")
        elif config.get('database', {}).get('mysql', {}):
            # 从JSON/YAML配置获取
            mysql_config = config.get('database', {}).get('mysql', {})
            print(f"从database.mysql配置获取MySQL配置: {mysql_config}")
        
        if not mysql_config:
            # 如果配置文件中没有MySQL配置，使用默认配置
            mysql_config = {
                'host': 'localhost',
                'port': 3306,
                'user': 'root',
                'password': 'password',
                'database': 'liuxiong',
                'charset': 'utf8mb4'
            }
            print("使用默认MySQL配置")
        
        print(f"连接配置: {mysql_config}")
        
        # 创建MySQL处理器
        mysql_handler = MySQLHandler(mysql_config)
        
        # 测试连接
        if mysql_handler.is_connected():
            print("✅ MySQL连接成功")
            return mysql_handler
        else:
            mysql_handler.connect()
            print("✅ MySQL连接建立成功")
            return mysql_handler
            
    except Exception as e:
        print(f"❌ MySQL连接失败: {e}")
        logger.error(f"MySQL连接失败: {e}")
        return None

def test_basic_queries(mysql_handler):
    """测试基本查询"""
    if not mysql_handler:
        print("❌ 无法执行查询测试，MySQL连接失败")
        return
    
    print("\n=== 测试基本查询 ===")
    
    try:
        # 测试1: 查看数据库列表
        print("1. 查看数据库列表:")
        databases = mysql_handler.get_databases()
        print(f"   数据库列表: {databases}")
        
        # 测试2: 查看当前数据库的表
        print("\n2. 查看当前数据库的表:")
        tables = mysql_handler.get_tables()
        print(f"   表列表: {tables}")
        
        # 测试3: 执行简单查询
        print("\n3. 执行系统查询:")
        result = mysql_handler.execute_query("SELECT VERSION() as version, NOW() as current_time")
        print(f"   MySQL版本和当前时间: {result}")
        
        # 测试4: 如果有user表，查询用户数据
        if 'user' in tables:
            print("\n4. 查询user表数据:")
            user_count = mysql_handler.execute_query("SELECT COUNT(*) as total FROM user")
            print(f"   用户总数: {user_count}")
            
            # 查询前10个用户
            users = mysql_handler.execute_query("SELECT * FROM user LIMIT 10")
            print(f"   前10个用户: {users}")
        else:
            print("\n4. user表不存在，跳过用户查询测试")
            
    except Exception as e:
        print(f"❌ 查询测试失败: {e}")
        logger.error(f"查询测试失败: {e}")

def test_parameterized_queries(mysql_handler):
    """测试参数化查询"""
    if not mysql_handler:
        return
    
    print("\n=== 测试参数化查询 ===")
    
    try:
        # 使用参数化查询（推荐方式，防止SQL注入）
        query = "SELECT DATABASE() as current_db, USER() as current_user, ? as test_param"
        result = mysql_handler.execute_query(query, ('测试参数',))
        print(f"参数化查询结果: {result}")
        
    except Exception as e:
        print(f"❌ 参数化查询失败: {e}")
        logger.error(f"参数化查询失败: {e}")

def test_sql_file_execution(mysql_handler):
    """测试从SQL文件执行查询"""
    if not mysql_handler:
        return
    
    print("\n=== 测试SQL文件执行 ===")
    
    # 创建测试SQL文件
    sql_file_path = os.path.join(os.path.dirname(__file__), 'test_queries.sql')
    
    # 创建示例SQL文件
    sql_content = """-- 测试SQL文件
SELECT 
    'Hello MySQL' as message,
    VERSION() as mysql_version,
    NOW() as current_time,
    DATABASE() as current_database;
"""
    
    try:
        # 写入SQL文件
        with open(sql_file_path, 'w', encoding='utf-8') as f:
            f.write(sql_content)
        
        # 读取并执行SQL文件
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_from_file = f.read().strip()
        
        result = mysql_handler.execute_query(sql_from_file)
        print(f"SQL文件执行结果: {result}")
        
        # 清理测试文件
        os.remove(sql_file_path)
        print("✅ SQL文件测试完成")
        
    except Exception as e:
        print(f"❌ SQL文件测试失败: {e}")
        logger.error(f"SQL文件测试失败: {e}")
        # 清理可能存在的测试文件
        if os.path.exists(sql_file_path):
            os.remove(sql_file_path)

def test_transaction(mysql_handler):
    """测试事务操作"""
    if not mysql_handler:
        return
    
    print("\n=== 测试事务操作 ===")
    
    try:
        # 使用上下文管理器进行事务操作
        with mysql_handler.connection_context():
            # 在这里可以执行多个相关的数据库操作
            # 如果发生异常，事务会自动回滚
            result = mysql_handler.execute_query("SELECT 'Transaction Test' as message")
            print(f"事务测试结果: {result}")
            print("✅ 事务测试完成")
            
    except Exception as e:
        print(f"❌ 事务测试失败: {e}")
        logger.error(f"事务测试失败: {e}")

def main():
    """主测试函数"""
    print("开始MySQL测试...")
    
    # 1. 测试连接
    mysql_handler = test_mysql_connection()
    
    if mysql_handler:
        # 2. 测试基本查询
        test_basic_queries(mysql_handler)
        
        # 3. 测试参数化查询
        test_parameterized_queries(mysql_handler)
        
        # 4. 测试SQL文件执行
        test_sql_file_execution(mysql_handler)
        
        # 5. 测试事务
        test_transaction(mysql_handler)
        
        # 6. 关闭连接
        mysql_handler.disconnect()
        print("\n✅ 所有测试完成，连接已关闭")
    else:
        print("\n❌ 测试失败，无法建立MySQL连接")

if __name__ == "__main__":

    main()




