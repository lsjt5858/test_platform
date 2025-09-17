#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 熊🐻来个🥬
# @Date: 2025/9/17
# @Description: 日期时间工具类，提供日期时间格式转换、计算等功能 / DateTime utility class for format conversion and calculation
"""
日期时间工具模块
DateTime Utility Module

本模块提供了一个DatetimeUtil类，包含了日期时间处理的各种常用方法：
- 时间戳与日期时间对象的相互转换
- 日期时间格式化输出
- 日期时间计算（加减天数、月数、秒数等）
- 获取特定日期（月初、月末、年初、年末等）
- 日期字符串解析

This module provides a DatetimeUtil class with various common methods for date and time processing:
- Mutual conversion between timestamps and datetime objects
- Date and time formatted output
- Date and time calculation (add/subtract days, months, seconds, etc.)
- Get specific dates (beginning of month, end of month, beginning of year, end of year, etc.)
- Date string parsing
"""

import calendar
import random
import re
from datetime import date, datetime, timedelta
from math import copysign
from typing import Optional, Union, Tuple, Any


class DatetimeUtil:
    """
    日期时间工具类
    DateTime Utility Class
    
    提供日期时间处理的各种静态方法和类方法
    Provides various static and class methods for date and time processing
    """
    _datetime_ms_format = '%Y{0}%m{0}%d{1}%H{2}%M{2}%S{3}%f'
    _datetime_format = '%Y{0}%m{0}%d{1}%H{2}%M{2}%S'
    _date_format = '%Y{0}%m{0}%d'
    _month_format = '%Y{0}%m'

    @staticmethod
    def timestamp_to_datetime(timestamp: Union[float, int]) -> datetime:
        """
        将时间戳转换为datetime对象
        Convert timestamp (in seconds or milliseconds) to datetime object
        
        Args:
            timestamp (Union[float, int]): 时间戳（秒或毫秒） / Timestamp in seconds or milliseconds
            
        Returns:
            datetime: datetime对象 / datetime object
        """
        try:
            return datetime.fromtimestamp(timestamp)
        except ValueError:
            return datetime.fromtimestamp(timestamp / 1000)

    @staticmethod
    def datetime_to_timestamp(datetime_obj: datetime) -> float:
        """
        将datetime对象转换为时间戳
        Convert datetime object to timestamp
        
        Args:
            datetime_obj (datetime): datetime对象 / datetime object
            
        Returns:
            float: 时间戳 / timestamp
        """
        return datetime.timestamp(datetime_obj)

    @staticmethod
    def timestamp_to_date(timestamp: Union[float, int]) -> date:
        """
        将时间戳转换为date对象
        Convert timestamp (in seconds or milliseconds) to date object
        
        Args:
            timestamp (Union[float, int]): 时间戳（秒或毫秒） / Timestamp in seconds or milliseconds
            
        Returns:
            date: date对象 / date object
        """
        try:
            return date.fromtimestamp(timestamp)
        except ValueError:
            return date.fromtimestamp(timestamp / 1000)

    @classmethod
    def date_to_timestamp(cls, date_obj: date) -> float:
        """
        将date对象转换为时间戳
        Convert date object to timestamp
        
        Args:
            date_obj (date): date对象 / date object
            
        Returns:
            float: 时间戳 / timestamp
        """
        datetime_obj = cls.date_to_datetime(date_obj)
        return cls.datetime_to_timestamp(datetime_obj)

    @classmethod
    def date_to_datetime(cls, date_obj: date) -> datetime:
        """
        将date对象转换为datetime对象
        Convert date object to datetime object
        
        Args:
            date_obj (date): date对象 / date object
            
        Returns:
            datetime: datetime对象（时间为00:00:00） / datetime object (time set to 00:00:00)
        """
        return datetime(year=date_obj.year, month=date_obj.month, day=date_obj.day)

    @classmethod
    def datetime_to_date(cls, datetime_obj: datetime) -> date:
        """
        将datetime对象转换为date对象
        Convert datetime object to date object
        
        Args:
            datetime_obj (datetime): datetime对象 / datetime object
            
        Returns:
            date: date对象（只保留日期部分） / date object (date part only)
        """
        return date(year=datetime_obj.year, month=datetime_obj.month, day=datetime_obj.day)

    @classmethod
    def get_time_delta(cls, start: Union[datetime, float, int], end: Union[datetime, float, int]) -> float:
        """
        计算两个时间对象之间的时间差（秒）
        Calculate time delta in seconds between two time objects
        
        Args:
            start (Union[datetime, float, int]): 开始时间 / Start time
            end (Union[datetime, float, int]): 结束时间 / End time
            
        Returns:
            float: 时间差（秒），保癕2位小数 / Time difference in seconds with 2 decimal places
        """
        if isinstance(start, (float, int)):
            start = cls.timestamp_to_datetime(start)
        if isinstance(end, (float, int)):
            end = cls.timestamp_to_datetime(end)
        return round((end - start).total_seconds(), 2)

    @classmethod
    def get_date_delta(cls, start: Union[date, datetime, str, float], end: Union[date, datetime, str, float]) -> int:
        """
        计算两个日期对象之间的日期差（天）
        Calculate date delta in days between two date objects
        
        Args:
            start (Union[date, datetime, str, float]): 开始日期 / Start date
            end (Union[date, datetime, str, float]): 结束日期 / End date
            
        Returns:
            int: 日期差（天） / Date difference in days
        """
        start = cls._any_time_obj_to_date(start)
        end = cls._any_time_obj_to_date(end)
        return (end - start).days

    @classmethod
    def get_day_start(cls, time_obj: Optional[Union[datetime, date, float]] = None, 
                      return_type: str = 'TIMESTAMP') -> Union[datetime, str, float]:
        """
        获取某一天的开始时间（00:00:00）
        Get the start time of a day (00:00:00)
        
        Args:
            time_obj (Optional[Union[datetime, date, float]]): 日期时间对象或时间戳，默认为今天 / datetime, date object or timestamp, default is today
            return_type (str): 返回类型：DATETIME/STRING/TIMESTAMP / Return type: DATETIME/STRING/TIMESTAMP
            
        Returns:
            Union[datetime, str, float]: 天开始时间 / Day start time
        """
        date_obj = cls._any_time_obj_to_datetime(cls._any_time_obj_to_date(time_obj))
        if return_type.upper() == 'DATETIME':
            return date_obj
        if return_type.upper() == 'STRING':
            return cls.strf_datetime(date_obj)
        if return_type.upper() == 'TIMESTAMP':
            return cls.datetime_to_timestamp(date_obj)
        raise ValueError(f'[get_day_start/end] return_type: {return_type} invalid')

    @classmethod
    def get_day_end(cls, time_obj: Optional[Union[datetime, date, float]] = None, 
                    return_type: str = 'TIMESTAMP') -> Union[datetime, str, float]:
        """
        获取某一天的结束时间（下一天的00:00:00）
        Get the end time of a day (next day 00:00:00)
        
        Args:
            time_obj (Optional[Union[datetime, date, float]]): 日期时间对象或时间戳，默认为今天 / datetime, date object or timestamp, default is today
            return_type (str): 返回类型：DATETIME/STRING/TIMESTAMP / Return type: DATETIME/STRING/TIMESTAMP
            
        Returns:
            Union[datetime, str, float]: 天结束时间 / Day end time
        """
        date_obj = cls._any_time_obj_to_datetime(cls._any_time_obj_to_date(time_obj))
        return cls.get_day_start(cls.get_specific_date(1, date_obj), return_type)

    @classmethod
    def strf_datetime(cls, time_obj: Union[datetime, float, int], date_mark: str = '-', 
                      connect: str = ' ', time_mark: str = ':', show_ms: bool = False) -> str:
        """
        将时间对象格式化为字符串
        Format time object to string
        
        Args:
            time_obj (Union[datetime, float, int]): datetime对象或时间戳 / datetime object or timestamp
            date_mark (str): 日期连接符，YYYY{}MM{}DD / Date connector, YYYY{}MM{}DD
            connect (str): 日期和时间连接符，YYYY-MM-DD{}HH:MM:SS / Date and time connector, YYYY-MM-DD{}HH:MM:SS
            time_mark (str): 时间连接符，HH{}MM{}SS / Time connector, HH{}MM{}SS
            show_ms (bool): 是否显示毫秒 / Whether to show milliseconds
            
        Returns:
            str: 格式化后的时间字符串，例如：2020-09-20 21:12:38 / Formatted time string, e.g.: 2020-09-20 21:12:38
            
        Examples:
            >>> from datetime import datetime
            >>> time_str = DatetimeUtil.strf_datetime(datetime.now())
            >>>
            >>> import time
            >>> time_str2 = DatetimeUtil.strf_datetime(time.time())
        """
        if isinstance(time_obj, (float, int)):
            time_obj = cls.timestamp_to_datetime(time_obj)
        if show_ms:
            return time_obj.strftime(cls._datetime_ms_format.format(date_mark, connect, time_mark, '.'))
        return time_obj.strftime(cls._datetime_format.format(date_mark, connect, time_mark))

    @classmethod
    def strf_date(cls, time_obj: Union[date, datetime, float, int], date_mark: str = '-') -> str:
        """
        将时间对象格式化为日期字符串
        Format time object to date string
        
        Args:
            time_obj (Union[date, datetime, float, int]): date/datetime对象或时间戳 / date/datetime object or timestamp
            date_mark (str): 日期连接符，YYYY{}MM{}DD / Date connector, YYYY{}MM{}DD
            
        Returns:
            str: 格式化后的日期字符串，例如：2020-09-20 / Formatted date string, e.g.: 2020-09-20
        """
        if isinstance(time_obj, (float, int)):
            time_obj = cls.timestamp_to_date(time_obj)
        return time_obj.strftime(cls._date_format.format(date_mark))

    @classmethod
    def strf_current_datetime(cls, date_mark: str = '-', connect: str = ' ', 
                              time_mark: str = ':', show_ms: bool = False) -> str:
        """
        获取当前时间的格式化字符串
        Get formatted string of current datetime
        
        Args:
            date_mark (str): 日期连接符，YYYY{}MM{}DD / Date connector, YYYY{}MM{}DD
            connect (str): 日期和时间连接符，YYYY-MM-DD{}HH:MM:SS / Date and time connector, YYYY-MM-DD{}HH:MM:SS
            time_mark (str): 时间连接符，HH{}MM{}SS / Time connector, HH{}MM{}SS
            show_ms (bool): 是否显示毫秒 / Whether to show milliseconds
            
        Returns:
            str: 当前时间的格式化字符串，例如：2020-09-20 21:12:38 / Formatted current datetime string, e.g.: 2020-09-20 21:12:38
        """
        if show_ms:
            return datetime.now().strftime(cls._datetime_ms_format.format(date_mark, connect, time_mark, '.'))
        return datetime.now().strftime(cls._datetime_format.format(date_mark, connect, time_mark))

    @classmethod
    def strf_current_date(cls, date_mark: str = '-') -> str:
        """
        获取当前日期的格式化字符串
        Get formatted string of current date
        
        Args:
            date_mark (str): 日期连接符，YYYY{}MM{}DD / Date connector, YYYY{}MM{}DD
            
        Returns:
            str: 当前日期的格式化字符串，例如：2020-09-20 / Formatted current date string, e.g.: 2020-09-20
        """
        return date.today().strftime(cls._date_format.format(date_mark))

    @classmethod
    def strf_current_month(cls, mark: str = '-') -> str:
        """
        获取当前月份的格式化字符串
        Get formatted string of current month
        
        Args:
            mark (str): 日期连接符，YYYY{}MM / Date connector, YYYY{}MM
            
        Returns:
            str: 当前月份的格式化字符串，例如：2020-09 / Formatted current month string, e.g.: 2020-09
        """
        return datetime.strftime(datetime.now(), cls._month_format.format(mark))

    @classmethod
    def str_to_datetime(cls, date_str: str) -> datetime:
        """
        将日期字符串转换为datetime对象
        Convert date string to datetime object
        
        Args:
            date_str (str): 日期字符串，格式为YYYY{}MM{}DD或YYYY{}MM{}DD{}HH{}MM{}SS，连接符可以是任意字符 / 
                      Date string in format YYYY{}MM{}DD or YYYY{}MM{}DD{}HH{}MM{}SS, connectors can be any character
                      
        Returns:
            datetime: 解析后的datetime对象 / Parsed datetime object
        """
        connectives = cls._get_date_connectives(date_str)
        date_mark = connectives.get('date_mark')
        connect = connectives.get('connect')
        time_mark = connectives.get('time_mark')
        ms_mark = connectives.get('ms_mark')
        if ms_mark:
            fmt = cls._datetime_ms_format.format(date_mark, connect, time_mark, ms_mark)
        elif connect:
            fmt = cls._datetime_format.format(date_mark, connect, time_mark)
        else:
            fmt = cls._date_format.format(date_mark)
        return datetime.strptime(date_str, fmt)

    @classmethod
    def get_specific_date(cls, delta: int, original_date: Optional[Union[date, datetime, str, float]] = None, 
                          return_type: str = 'STRING', mark: str = '-') -> Union[str, date, datetime, float]:
        """
        获取指定日期加上指定天数后的日期
        Get the date after adding specified days to original date
        
        Args:
            delta (int): 要加或减的天数 / Number of days to add or subtract
            original_date (Optional[Union[date, datetime, str, float]]): 原始日期，默认为今天 / Original date, default is today
            return_type (str): 返回类型：'STRING'/'DATE'/'DATETIME'/'TIMESTAMP' / Return type: 'STRING'/'DATE'/'DATETIME'/'TIMESTAMP'
            mark (str): 连接符，仅在return_type=='STRING'时使用 / Connector, only used when return_type=='STRING'
            
        Returns:
            Union[str, date, datetime, float]: 计算后的日期 / Calculated date
        """
        original_date = cls._any_time_obj_to_date(original_date)
        result_date = original_date + timedelta(days=delta)
        if return_type.upper() == 'DATE':
            return date(year=result_date.year, month=result_date.month, day=result_date.day)
        if return_type.upper() == 'DATETIME':
            return result_date if isinstance(result_date, datetime) else datetime(
                year=result_date.year, month=result_date.month, day=result_date.day)
        if return_type.upper() == 'STRING':
            return cls.strf_date(result_date, mark)
        if return_type.upper() == 'TIMESTAMP':
            return cls.date_to_timestamp(result_date)
        raise ValueError(f'[get_specific_date] return_type: {return_type} invalid')

    @classmethod
    def get_specific_month(cls, delta: int, original_date: Optional[Union[date, datetime, str, float]] = None, 
                           mark: str = '-') -> str:
        """
        获取指定日期加上指定月数后的月份
        Get the month after adding specified months to original date
        
        Args:
            delta (int): 要加或减的月数 / Number of months to add or subtract
            original_date (Optional[Union[date, datetime, str, float]]): 原始日期，默认为今天 / Original date, default is today
            mark (str): 连接符 / Connector
            
        Returns:
            str: 月份字符串，例如：2020-10 / Month string, e.g.: 2020-10
        """
        original_date = cls._any_time_obj_to_date(original_date)

        sign = int(copysign(1, delta))
        delta_y, delta_m = divmod(delta * sign, 12)
        delta_y = sign * delta_y
        delta_m = sign * delta_m
        month = original_date.month + delta_m
        year = original_date.year + delta_y
        if month > 12:
            year += 1
            month -= 12
        elif month < 1:
            year -= 1
            month += 12

        return date(year, month, 1).strftime(cls._month_format.format(mark))

    @classmethod
    def get_specific_seconds(cls, delta: int, original_date: Optional[Union[datetime, str, float]] = None, 
                             return_type: str = 'STRING') -> Union[str, datetime, float]:
        """
        获取指定时间加上指定秒数后的时间
        Get the time after adding specified seconds to original time
        
        Args:
            delta (int): 要加或减的秒数 / Number of seconds to add or subtract
            original_date (Optional[Union[datetime, str, float]]): 原始时间，默认为当前时间 / Original time, default is current time
            return_type (str): 返回类型：'STRING'/'DATETIME'/'TIMESTAMP' / Return type: 'STRING'/'DATETIME'/'TIMESTAMP'
            
        Returns:
            Union[str, datetime, float]: 计算后的时间 / Calculated time
        """
        original_dt = cls._any_time_obj_to_datetime(original_date)
        result_dt = original_dt + timedelta(seconds=delta)
        if return_type.upper() == 'DATETIME':
            return result_dt
        if return_type.upper() == 'TIMESTAMP':
            return cls.datetime_to_timestamp(result_dt)
        if return_type.upper() == 'STRING':
            return cls.strf_datetime(result_dt)
        raise ValueError(f'[get_specific_seconds] return_type: {return_type} invalid')

    @classmethod
    def get_specific_minutes(cls, delta: int, original_date: Optional[Union[datetime, str, float]] = None, 
                             return_type: str = 'STRING') -> Union[str, datetime, float]:
        """
        获取指定时间加上指定分钟数后的时间
        Get the time after adding specified minutes to original time
        
        Args:
            delta (int): 要加或减的分钟数 / Number of minutes to add or subtract
            original_date (Optional[Union[datetime, str, float]]): 原始时间，默认为当前时间 / Original time, default is current time
            return_type (str): 返回类型：'STRING'/'DATETIME'/'TIMESTAMP' / Return type: 'STRING'/'DATETIME'/'TIMESTAMP'
            
        Returns:
            Union[str, datetime, float]: 计算后的时间 / Calculated time
        """
        return cls.get_specific_seconds(delta * 60, original_date, return_type)

    @classmethod
    def get_two_random_dates_within_a_month(cls, year: Optional[Union[int, str]] = None, 
                                            month: Optional[Union[int, str]] = None, 
                                            return_str: bool = True) -> Union[Tuple[str, str], Tuple[date, date]]:
        """
        获取指定月份内的两个随机日期
        Get two random dates within a specified month
        
        Args:
            year (Optional[Union[int, str]]): 年份，默认为当前年 / Year, default is current year
            month (Optional[Union[int, str]]): 月份，默认为当前月 / Month, default is current month
            return_str (bool): 是否返回字符串格式 / Whether to return string format
            
        Returns:
            Union[Tuple[str, str], Tuple[date, date]]: 两个随机日期 / Two random dates
        """
        year = int(year) if year else date.today().year
        month = int(month) if month else date.today().month
        _, days = calendar.monthrange(year, month)
        month_start_date = date(year, month, day=1)
        delta1 = random.randint(0, days - 2)
        delta2 = random.randint(1, days - delta1 - 1)
        first = month_start_date + timedelta(days=delta1)
        second = first + timedelta(days=delta2)
        return (cls.strf_date(first), cls.strf_date(second)) if return_str else (first, second)

    @classmethod
    def get_this_month_last_date(cls, original_date: Optional[Union[date, datetime, str, float]] = None, 
                                 return_str: bool = True) -> Union[date, str]:
        """
        获取指定日期所在月份的最后一天
        Get the last date of the month for specified date
        
        Args:
            original_date (Optional[Union[date, datetime, str, float]]): 原始日期，默认为今天 / Original date, default is today
            return_str (bool): 是否返回字符串格式 / Whether to return string format
            
        Returns:
            Union[date, str]: 月末日期，例如：date(2020, 10, 31)或'2020-10-31' / Last date of month, e.g.: date(2020, 10, 31) or '2020-10-31'
        """
        original_date = cls._any_time_obj_to_date(original_date)
        _, days = calendar.monthrange(original_date.year, original_date.month)
        result_date = date(year=original_date.year, month=original_date.month, day=days)
        return cls.strf_date(result_date) if return_str else result_date

    @classmethod
    def get_this_month_first_date(cls, original_date: Optional[Union[date, datetime, str, float]] = None, 
                                  return_str: bool = True) -> Union[date, str]:
        """
        获取指定日期所在月份的第一天
        Get the first date of the month for specified date
        
        Args:
            original_date (Optional[Union[date, datetime, str, float]]): 原始日期，默认为今天 / Original date, default is today
            return_str (bool): 是否返回字符串格式 / Whether to return string format
            
        Returns:
            Union[date, str]: 月初日期，例如：date(2020, 10, 1)或'2020-10-01' / First date of month, e.g.: date(2020, 10, 1) or '2020-10-01'
        """
        original_date = cls._any_time_obj_to_date(original_date)
        result_date = date(year=original_date.year, month=original_date.month, day=1)
        return cls.strf_date(result_date) if return_str else result_date

    @classmethod
    def get_next_month_first_date(cls, original_date: Optional[Union[date, datetime, str, float]] = None, 
                                  return_str: bool = True) -> Union[date, str]:
        """
        获取指定日期下个月的第一天
        Get the first date of next month for specified date
        
        Args:
            original_date (Optional[Union[date, datetime, str, float]]): 原始日期，默认为今天 / Original date, default is today
            return_str (bool): 是否返回字符串格式 / Whether to return string format
            
        Returns:
            Union[date, str]: 下月初日期，例如：date(2020, 11, 1)或'2020-11-01' / First date of next month, e.g.: date(2020, 11, 1) or '2020-11-01'
        """
        last_date = cls.get_this_month_last_date(original_date, return_str=False)
        result_date = last_date + timedelta(days=1)
        return cls.strf_date(result_date) if return_str else result_date

    @classmethod
    def get_last_month_last_date(cls, original_date: Optional[Union[date, datetime, str, float]] = None, 
                                 return_str: bool = True) -> Union[date, str]:
        """
        获取指定日期上个月的最后一天
        Get the last date of previous month for specified date
        
        Args:
            original_date (Optional[Union[date, datetime, str, float]]): 原始日期，默认为今天 / Original date, default is today
            return_str (bool): 是否返回字符串格式 / Whether to return string format
            
        Returns:
            Union[date, str]: 上月末日期，例如：date(2020, 9, 30)或'2020-09-30' / Last date of previous month, e.g.: date(2020, 9, 30) or '2020-09-30'
        """
        next_day = cls.get_this_month_first_date(original_date, return_str=False)
        result_date = next_day + timedelta(days=-1)
        return cls.strf_date(result_date) if return_str else result_date

    @classmethod
    def get_this_year_first_date(cls, original_date: Optional[Union[date, datetime, str, float]] = None, 
                                 return_str: bool = True) -> Union[date, str]:
        """
        获取指定日期所在年份的第一天
        Get the first date of the year for specified date
        
        Args:
            original_date (Optional[Union[date, datetime, str, float]]): 原始日期，默认为今天 / Original date, default is today
            return_str (bool): 是否返回字符串格式 / Whether to return string format
            
        Returns:
            Union[date, str]: 年初日期，例如：date(2020, 1, 1)或'2020-01-01' / First date of year, e.g.: date(2020, 1, 1) or '2020-01-01'
        """
        original_date = cls._any_time_obj_to_date(original_date)
        result_date = date(year=original_date.year, month=1, day=1)
        return cls.strf_date(result_date) if return_str else result_date

    @classmethod
    def get_this_year_last_date(cls, original_date: Optional[Union[date, datetime, str, float]] = None, 
                                return_str: bool = True) -> Union[date, str]:
        """
        获取指定日期所在年份的最后一天
        Get the last date of the year for specified date
        
        Args:
            original_date (Optional[Union[date, datetime, str, float]]): 原始日期，默认为今天 / Original date, default is today
            return_str (bool): 是否返回字符串格式 / Whether to return string format
            
        Returns:
            Union[date, str]: 年末日期，例如：date(2020, 12, 31)或'2020-12-31' / Last date of year, e.g.: date(2020, 12, 31) or '2020-12-31'
        """
        original_date = cls._any_time_obj_to_date(original_date)
        result_date = date(year=original_date.year, month=12, day=31)
        return cls.strf_date(result_date) if return_str else result_date

    @classmethod
    def date_str_to_int(cls, date_str: str) -> int:
        """
        将日期字符串转换为整数
        Convert date string to integer
        
        Args:
            date_str (str): 日期字符串，格式为YYYY{}MM{}DD，连接符可以是任意字符 / Date string in format YYYY{}MM{}DD, connector can be any character
            
        Returns:
            int: 日期整数，例如：'2020-10-10' -> 20201010 / Date integer, e.g.: '2020-10-10' -> 20201010
        """
        date_mark = cls._get_date_connectives(date_str).get('date_mark')
        return int(date_str.replace(date_mark, '').strip())

    @classmethod
    def int_to_str(cls, date_int: int) -> str:
        """
        将日期整数转换为字符串
        Convert date integer to string
        
        Args:
            date_int (int): 日期整数 / Date integer
            
        Returns:
            str: 日期字符串，例如：20201001 -> '2020-10-01' / Date string, e.g.: 20201001 -> '2020-10-01'
        """
        datetime_obj = datetime.strptime(str(date_int), cls._date_format.format(''))
        return cls.strf_date(datetime_obj)

    # ========================================
    #            私有方法 / Private Methods            
    # ========================================

    @staticmethod
    def _get_date_connectives(date_str: str) -> dict:
        """
        获取日期字符串中的连接符
        Get connectors in date string
        
        Args:
            date_str (str): 日期字符串 / Date string
            
        Returns:
            dict: 包含各种连接符的字典 / Dictionary containing various connectors
        """
        expr = r'\d+(\D)\d+\D\d+((\D)\d+(\D)\d+\D\d+((\D)\d+){0,1}){0,1}'
        groups = re.match(expr, date_str).groups()
        return {
            'date_mark': groups[0],
            'connect': groups[2],
            'time_mark': groups[3],
            'ms_mark': groups[5]
        }

    @classmethod
    def _any_time_obj_to_date(cls, obj: Optional[Any]) -> date:
        """
        将任意时间对象转换为date对象
        Convert any time object to date object
        
        Args:
            obj (Optional[Any]): 任意时间对象 / Any time object
            
        Returns:
            date: date对象 / date object
        """
        if not obj:
            return date.today()
        if isinstance(obj, float):
            return cls.timestamp_to_date(obj)
        if isinstance(obj, str):
            return cls.str_to_datetime(obj).date()
        if isinstance(obj, datetime):
            return obj.date()
        return obj

    @classmethod
    def _any_time_obj_to_datetime(cls, obj: Optional[Any]) -> datetime:
        """
        将任意时间对象转换为datetime对象
        Convert any time object to datetime object
        
        Args:
            obj (Optional[Any]): 任意时间对象 / Any time object
            
        Returns:
            datetime: datetime对象 / datetime object
        """
        if not obj:
            return datetime.now()
        if isinstance(obj, float):
            return cls.timestamp_to_datetime(obj)
        if isinstance(obj, str):
            return cls.str_to_datetime(obj)
        if isinstance(obj, date):
            return cls.date_to_datetime(obj)
        return obj