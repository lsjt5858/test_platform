#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 熊🐻来个🥬
# @Date:  2025/9/17
# @Description: [对文件功能等的简要描述（可自行添加）]


"""Enum class used for http urls"""

from enum import Enum


class HttpApi(Enum):
    """enum class used for http urls"""

    def __init__(self, url, desc=None):
        self._url = url
        self._desc = desc
        self._format_url = None

    @property
    def api(self):
        if self._format_url:
            return self._format_url
        return self._url

    @property
    def desc(self):
        return self._desc

    def format_api(self, *args, **kwargs):
        self._format_url = self._url.format(*args, **kwargs)
        return self


def psm(psm_value):
    """value psm to the class"""

    def app_decorator(cls):
        if not hasattr(cls, 'psm_list'):
            cls.psm_list = []
        cls.psm_list.append(psm_value)
        return cls

    return app_decorator
