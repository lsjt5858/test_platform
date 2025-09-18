#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 熊🐻来个🥬
# @Date: 2025/9/17
# @Description: 日志工具类，提供统一的日志记录功能 / Log utility class providing unified logging functionality
"""
日志工具模块
Log Utility Module

本模块提供了一个LogUtil类，用于统一管理和记录日志信息。包含以下功能：
- 封装了Python原生的logging模块的所有日志级别方法
- 提供了自定义的日志格式化方法
- 支持步骤化日志记录和数据结构化输出
- 统一配置了日志输出格式和级别

This module provides a LogUtil class for unified management and logging of log information. 
It includes the following features:
- Encapsulates all log level methods from Python's native logging module
- Provides custom log formatting methods
- Supports step-by-step logging and structured data output
- Unified configuration of log output format and levels
"""

import logging
import sys
from typing import Any, Dict, List, Optional, Set, Union

# 配置全局日志格式 / Configure global log format
logging.basicConfig(
    stream=sys.stdout, 
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# 获取全局日志器 / Get global logger
_log = logging.getLogger()

class LogUtil:
    """
    日志工具类
    Log Utility Class
    
    提供统一的日志记录功能，包括所有标准日志级别和自定义日志格式方法。
    Provides unified logging functionality, including all standard log levels and custom log formatting methods.
    
    使用示例 / Examples:
        >>> from core.base_util.log_util import LogUtil
        >>> LogUtil.info('this is a log message')  # 基本日志 / Basic logging
        >>> LogUtil.log_step(1, 'this is step info')  # 步骤日志 / Step logging
        >>> LogUtil.log_dict_in_lines({'key': 'value'})  # 字典日志 / Dictionary logging
    """

    # ========================================
    #     内置日志方法 / Built-in Logging Methods
    # ========================================
    @classmethod
    def debug(cls, msg: str, *args: Any, **kwargs: Any) -> None:
        """
        记录DEBUG级别的日志信息
        Log message with severity 'DEBUG'
        
        Args:
            msg (str): 日志消息 / Log message
            *args: 消息格式化参数 / Message formatting arguments
            **kwargs: 其他参数，如exc_info等 / Other arguments like exc_info
            
        Example:
            >>> LogUtil.debug("Houston, we have a %s", "thorny problem", exc_info=1)
        """
        _log.debug(msg, *args, **kwargs)

    @classmethod
    def info(cls, msg: str, *args: Any, **kwargs: Any) -> None:
        """
        记录INFO级别的日志信息
        Log message with severity 'INFO'
        
        Args:
            msg (str): 日志消息 / Log message
            *args: 消息格式化参数 / Message formatting arguments
            **kwargs: 其他参数，如exc_info等 / Other arguments like exc_info
            
        Example:
            >>> LogUtil.info("Houston, we have a %s", "interesting problem", exc_info=1)
        """
        _log.info(msg, *args, **kwargs)

    @classmethod
    def warning(cls, msg: str, *args: Any, **kwargs: Any) -> None:
        """
        记录WARNING级别的日志信息
        Log message with severity 'WARNING'
        
        Args:
            msg (str): 日志消息 / Log message
            *args: 消息格式化参数 / Message formatting arguments
            **kwargs: 其他参数，如exc_info等 / Other arguments like exc_info
            
        Example:
            >>> LogUtil.warning("Houston, we have a %s", "bit of a problem", exc_info=1)
        """
        _log.warning(msg, *args, **kwargs)

    @classmethod
    def warn(cls, msg: str, *args: Any, **kwargs: Any) -> None:
        """
        warning方法的别名
        Alias for warning method
        
        Args:
            msg (str): 日志消息 / Log message
            *args: 消息格式化参数 / Message formatting arguments
            **kwargs: 其他参数 / Other arguments
        """
        _log.warning(msg, *args, **kwargs)

    @classmethod
    def error(cls, msg: str, *args: Any, **kwargs: Any) -> None:
        """
        记录ERROR级别的日志信息
        Log message with severity 'ERROR'
        
        Args:
            msg (str): 日志消息 / Log message
            *args: 消息格式化参数 / Message formatting arguments
            **kwargs: 其他参数，如exc_info等 / Other arguments like exc_info
            
        Example:
            >>> LogUtil.error("Houston, we have a %s", "major problem", exc_info=1)
        """
        _log.error(msg, *args, **kwargs)

    @classmethod
    def exception(cls, msg: str, *args: Any, **kwargs: Any) -> None:
        """
        记录带有异常信息的ERROR级别日志
        Convenience method for logging an ERROR with exception information
        
        此方法会自动捕获当前异常信息并包含在日志中
        This method automatically captures current exception information and includes it in the log
        
        Args:
            msg (str): 日志消息 / Log message
            *args: 消息格式化参数 / Message formatting arguments
            **kwargs: 其他参数 / Other arguments
            
        Example:
            >>> try:
            ...     1/0
            ... except:
            ...     LogUtil.exception("An error occurred")
        """
        _log.exception(msg, *args, **kwargs)


    @classmethod
    def critical(cls, msg: str, *args: Any, **kwargs: Any) -> None:
        """
        记录CRITICAL级别的日志信息（最高优先级）
        Log message with severity 'CRITICAL' (highest priority)
        
        Args:
            msg (str): 日志消息 / Log message
            *args: 消息格式化参数 / Message formatting arguments
            **kwargs: 其他参数，如exc_info等 / Other arguments like exc_info
            
        Example:
            >>> LogUtil.critical("Houston, we have a %s", "major disaster", exc_info=1)
        """
        _log.critical(msg, *args, **kwargs)

    @classmethod
    def log(cls, level: int, msg: str, *args: Any, **kwargs: Any) -> None:
        """
        使用指定级别记录日志信息
        Log message with user-specified severity level
        
        Args:
            level (int): 日志级别（如logging.DEBUG, logging.INFO等） / Log level (e.g., logging.DEBUG, logging.INFO, etc.)
            msg (str): 日志消息 / Log message
            *args: 消息格式化参数 / Message formatting arguments
            **kwargs: 其他参数，如exc_info等 / Other arguments like exc_info
            
        Example:
            >>> LogUtil.log(logging.CRITICAL, "Houston, we have a %s", "major disaster", exc_info=1)
        """
        _log.log(level, msg, *args, **kwargs)

    # fatal是critical的别名 / fatal is an alias for critical
    fatal = critical

    # ========================================
    #     自定义日志方法 / Custom Logging Methods
    # ========================================
    @classmethod
    def log_step(cls, step_num: int, step_info: str) -> None:
        """
        记录步骤信息，使用特殊格式显示
        Log step information with special formatting
        
        Args:
            step_num (int): 步骤编号 / Step number
            step_info (str): 步骤描述信息 / Step description
            
        Example:
            >>> LogUtil.log_step(1, "初始化数据库连接")
        """
        msg = f'---------------------------step {step_num}: {step_info}------------------------------\n'
        cls.info(msg)

    @classmethod
    def log_sub_step(cls, step_num: int, step_info: str) -> None:
        """
        记录子步骤信息，使用缩进格式显示
        Log sub-step information with indented formatting
        
        Args:
            step_num (int): 子步骤编号 / Sub-step number
            step_info (str): 子步骤描述信息 / Sub-step description
            
        Example:
            >>> LogUtil.log_sub_step(1, "检查数据库连接状态")
        """
        msg = f'                      -----step {step_num}: {step_info}-----                         \n'
        cls.info(msg)

    @classmethod
    def log_dict_in_lines(cls, dic: Dict[str, Any], msg: Optional[str] = None, max_key_length: int = 30) -> None:
        """
        逐行打印字典内容，使用'key: value'的格式
        Print dictionary content line by line in 'key: value' format
        
        将字典的每个键值对按行显示，并且按键名排序，方便查看和调试
        Display each key-value pair of the dictionary by line, sorted by key name for easy viewing and debugging
        
        Args:
            dic (Dict[str, Any]): 要打印的字典对象 / Dictionary object to print
            msg (Optional[str]): 在打印字典前显示的消息 / Message to display before printing dictionary
            max_key_length (int): 最大键名长度，默认为30 / Maximum key length, default is 30
            
        Example:
            >>> data = {'name': 'test', 'age': 25, 'city': 'Beijing'}
            >>> LogUtil.log_dict_in_lines(data, '用户信息')
        """
        if not dic or len(dic) == 0:
            cls.info('-')
            return
        margin = ''.ljust(max_key_length * 3, '-')
        cls.info(f'{margin}\n[print]printing dict detailed data in lines......')
        if msg:
            cls.info(msg)
        keys = list(dic.keys())
        keys.sort()
        for key in keys:
            space_size = max_key_length - len(str(key))
            spaces = ''.ljust(space_size, ' ')
            value = dic[key].replace('\\', '') if isinstance(dic[key], str) else dic[key]
            cls.info(f'    {spaces}{key}  :  {value} ')
        cls.info(f'{margin}\n')

    @classmethod
    def log_list_in_lines(cls, input_list: Union[List[Any], Set[Any]], msg: Optional[str] = None) -> None:
        """
        逐行打印列表或集合的元素
        Print elements of a list or set line by line
        
        将列表或集合中的每个元素按行显示，方便查看和调试
        Display each element in the list or set by line for easy viewing and debugging
        
        Args:
            input_list (Union[List[Any], Set[Any]]): 要打印的列表或集合 / List or set to print
            msg (Optional[str]): 在打印列表前显示的消息 / Message to display before printing list
            
        Example:
            >>> data = ['apple', 'banana', 'cherry']
            >>> LogUtil.log_list_in_lines(data, '水果列表')
        """
        if not input_list or len(input_list) == 0:
            return
        margin = ''.ljust(80, '-')
        cls.info(f'{margin}\n[print]printing list detailed data in lines......')
        if msg:
            cls.info(msg)
        for element in input_list:
            element = str(element).replace('\\', '')
            cls.info(f'   {element} ')
        cls.info(f'{margin}\n')
