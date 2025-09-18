#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 熊🐻来个🥬
# @Date:  2025/9/17
# @Description: [对文件功能等的简要描述（可自行添加）]

import configparser
import os

# botocore/boto3 are optional; avoid hard import to keep this module runnable without them
try:
    from botocore.config import Config  # type: ignore
except Exception:  # pragma: no cover - optional dependency is missing
    class Config:  # minimal placeholder to avoid ImportError in local/test runs
        pass


def get_project_abs_path() -> str:
    """获取项目绝对路径
    
    在CI环境中返回'/home/code'，在本地环境中通过向上查找5层目录获取项目根路径
    
    Returns:
        str: 项目绝对路径
    """
    if os.getenv('CI_HEAD_BRANCH', default=None):
        return '/home/code'
    else:
        invoke_path = os.path.abspath(__file__)
        for _ in range(5):
            invoke_path = os.path.dirname(invoke_path)
        return invoke_path


class ConfigUtil:
    """Config utility used to get config variables"""
    project_abs_path:str = get_project_abs_path()
    log_path :str = os.path.join(project_abs_path, 'test','log')
    config_root_path = os.path.join(project_abs_path, 'config','env')
    base_config_path = os.path.join(config_root_path, 'env.ini')
    config:configparser.ConfigParser = None

    @classmethod
    def get_value(cls, key:str, section:str = 'default') ->str:
        """从指定配置段获取配置值
        
        Args:
            key (str): 配置键名
            section (str): 配置段名，默认为'default'
            
        Returns:
            str: 配置值
        """
        return cls.config.get(section, key)


    @classmethod
    def set_value(cls, key:str, value:str, section:str = 'default') ->None:
        """in-memory setting for runtime usage, will not write to a file"""
        cls.config.set(section, key, value)

    @classmethod
    def has_value(cls, key:str, section:str = 'default') ->bool:
        """检查指定配置段是否存在指定键
        
        Args:
            key (str): 配置键名
            section (str): 配置段名，默认为'default'
            
        Returns:
            bool: 如果存在返回True，否则返回False
        """
        return cls.config.has_option(section, key)

    @classmethod
    def update_base(cls, key: str, value: str):
        """更新基础配置文件env.ini中的配置项
        
        将指定的键值对更新到env.ini文件的base段中
        
        Args:
            key (str): 配置键名
            value (str): 配置值
        """

        base_config = cls.load_base_config()
        base_config.set('base', key, value)
        with open(cls.base_config_path, "w") as base_config_file:
            base_config.write(base_config_file)

    @classmethod
    def load_base_config(cls) -> configparser.ConfigParser:
        """加载基础配置文件
        
        读取并返回env.ini基础配置文件的ConfigParser对象
        
        Returns:
            configparser.ConfigParser: 基础配置对象
        """
        base_config = configparser.ConfigParser()
        base_config.read(cls.base_config_path)
        return base_config

    @classmethod
    def get_config_from_env(cls, env_value: str, config) -> None:
        """
        解析形如 "k1=v1,k2=v2,...,zone_env=section" 的字符串，并将结果写入内存配置。

        行为说明：
        - 如果提供了 `config`（ConfigParser），且存在 `zone_env` 段，则先把该段内容拷贝到 `default` 段；
        - 之后用字符串中的键值对覆盖（不把 `zone_env` 本身写入配置）。
        - 若 `cls.config` 未初始化，则在此处安全初始化一个 ConfigParser，并确保存在 `default` 段。
        """
        # 确保内存配置对象存在且包含 default 段
        if cls.config is None:
            # 关闭插值以避免值中出现 % 时报错
            cls.config = configparser.ConfigParser(interpolation=None)
        if not cls.config.has_section('default'):
            cls.config.add_section('default')

        if not isinstance(env_value, str) or not env_value.strip():
            # 空字符串直接返回，不做修改
            return

        # 拆分 key=value 列表，允许值中包含 '='，只按第一个 '=' 分割
        items = [i.strip() for i in env_value.split(',') if i.strip()]
        kv = {}
        for item in items:
            if '=' not in item:
                # 非法片段跳过（容错处理）
                continue
            k, v = item.split('=', 1)
            k = k.strip()
            v = v.strip()
            if not k:
                continue
            kv[k] = v

        # 读取并移除 zone_env，用于从外部 config 预填充
        zone_env = kv.pop('zone_env', None)

        # 如果外部 config 存在且包含该段，先把该段落的配置拷贝到 default 段
        if isinstance(config, configparser.ConfigParser) and zone_env and config.has_section(zone_env):
            for name, value in config.items(zone_env):
                cls.set_value(name, value, section='default')

        # 写入覆盖项（不包含 zone_env）到 default 段
        for name, value in kv.items():
            cls.set_value(name, value, section='default')

    @classmethod
    def reload(cls):
        """重新加载配置
        
        根据产品和环境构建配置。如果存在产品文件夹，将构建分层配置；
        否则，将加载普通文件。
        
        首先加载基础配置文件，然后根据产品路径是否存在决定使用
        分层加载还是传统加载方式。
        """
        cls.config = configparser.ConfigParser()
        cls.config.read([
            cls.base_config_path,
            os.path.join(cls.config_root_path, "config_default.ini"),
        ])

        product_path = os.path.join(cls.config_root_path, cls.get_product())
        if os.path.exists(product_path):
            cls.hierarchical_load(product_path)
        else:
            cls.legacy_load()

    @classmethod
    def hierarchical_load(cls, product_path: str):
        """分层加载配置文件
        
        按照产品->环境的顺序加载配置文件。
        参考示例: config/env/cdw
        两个级别的common.ini都可以用来存储通用的产品或环境值。
        
        Args:
            product_path (str): 产品配置路径
        """
        zone_path = os.path.join(product_path, cls.get_zone())
        cls.config.read([
            os.path.join(product_path, "common.ini"),
            os.path.join(zone_path, "common.ini"),
            os.path.join(zone_path, f"{cls.get_env()}.ini")
        ])

    @classmethod
    def legacy_load(cls):
        """传统配置加载方式
        
        为旧版本兼容性提供的配置加载方法。
        创建default段，加载产品配置文件，然后根据是否有自定义配置
        来决定使用环境变量配置还是区域环境配置。
        """
        cls.config.add_section('default')
        env_config = configparser.ConfigParser()
        env_config.read([os.path.join(cls.config_root_path, f"config_{cls.get_product()}.ini")])

        if os.environ.get('customized_config'):
            cls.get_config_from_env(os.environ.get('customized_config'), env_config)
        else:
            for name, value in env_config.items(cls.get_zone_env()):
                cls.set_value(name, value, section='default')

    # Base getters

    @classmethod
    def get_zone(cls) -> str:
        """获取区域配置
        
        Returns:
            str: 区域名称
        """
        return cls.config.get('base', 'zone')

    @classmethod
    def get_product(cls) -> str:
        """获取产品配置
        
        Returns:
            str: 产品名称
        """
        return cls.config.get('base', 'product')

    @classmethod
    def get_env(cls) -> str:
        """获取环境配置
        
        Returns:
            str: 环境名称
        """
        return cls.config.get('base', 'env')

    @classmethod
    def get_store(cls) -> str:
        """获取存储配置
        
        Returns:
            str: 存储配置值
        """
        return cls.config.get('base', 'store')

    @classmethod
    def get_zone_env(cls) -> str:
        """获取区域环境组合名称
        
        将区域名和环境名用下划线连接
        
        Returns:
            str: 区域_环境的组合名称
        """
        return cls.get_zone() + '_' + cls.get_env()

    @classmethod
    def get_priority(cls) -> str:
        """获取优先级配置
        
        Returns:
            str: 优先级值
        """
        return cls.config.get('base', 'priority')

    @classmethod
    def get_tesla(cls) -> str:
        """获取Tesla配置
        
        Returns:
            str: Tesla配置值
        """
        return cls.config.get('base', 'tesla')

    @classmethod
    def get_cluster(cls) -> str:
        """获取首选集群ID
        
        Returns:
            str: 首选集群ID
        """
        return cls.config.get('default', 'preferred_cluster_id')

    # TODO: move to general config since it's env specific
    @classmethod
    def get_version(cls) -> str:
        """获取版本配置
        
        Returns:
            str: 版本号
        """
        return cls.config.get('base', 'version')





if __name__ == "__main__":
    path = get_project_abs_path()
    print("项目绝对路径是：", path)
