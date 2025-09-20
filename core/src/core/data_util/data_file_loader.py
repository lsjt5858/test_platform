#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 熊🐻来个🥬
# @Date:  2025/9/20
# @Description: [对文件功能等的简要描述（可自行添加）]
"""file loader, if not json/yaml files, load file string"""

import json
import os
from copy import deepcopy
import yaml

from core.base_util.config_util import ConfigUtil
from core.base_util.log_util import LogUtil


class DataFileLoader:
    """yaml or json file loader

    Args:
        file_path(str): the root path of yaml files, env directory excluded
    """

    def __init__(self, file_path):
        self.file_path = file_path
        self.cache_files = {}

    def get_content(self, file_name):
        """get file content

        Args:
            file_name(str):

        Returns:
            dict or list:
        """
        parameters = self._load_parameters(file_name)
        LogUtil.info(f'获取到数据文件{file_name}')
        return parameters

    def get_parameter(self, file_name, feature_name):
        """get feature_name in file content

        Args:
            file_name(str):
            feature_name(str):

        Returns:
            any:
        """
        postfix = self._get_file_postfix(file_name)
        if postfix not in ('yaml', 'yml', 'json'):
            LogUtil.error(f'{file_name}的文件类型为{postfix or "无"}, 不支持get_parameter, 请修改后缀为json或yaml')
            return None
        params = self.get_content(file_name=file_name)
        if feature_name not in params.keys():
            LogUtil.warning(f'未获取到数据文件{file_name}, key = {feature_name}')
            return []
        param = params.get(feature_name, None)
        LogUtil.info(f'获取到数据文件{file_name}, key = {feature_name}：')
        return param

    # ----------------------------------------
    #            protected methods           |
    # ----------------------------------------
    def _load_parameters(self, file_name):
        # 如果之前加载过，直接返回
        if file_name in self.cache_files:
            return deepcopy(self.cache_files[file_name])
        zone = ConfigUtil.get_zone()
        zone_file_path = os.path.join(self.file_path, f'data_{zone}', file_name)
        #remove data_default
        default_file_path = os.path.join(self.file_path, file_name)
        #default_file_path = os.path.join(self.file_path, 'data_default', file_name)
        full_file_name = zone_file_path if os.path.exists(
            zone_file_path) else default_file_path
        LogUtil.info(f'loading path: {full_file_name}')
        postfix = self._get_file_postfix(file_name)
        if postfix == 'json':
            result = self._load_json_content(full_file_name)
        elif postfix in ('yml', 'yaml'):
            result = self._load_yml_content(full_file_name)
        else:   # 字符串形式读取文本
            result = self._load_string_content(full_file_name)
        # 暂存起来，下次不用重新load
        self.cache_files[file_name] = result
        return deepcopy(result)

    @staticmethod
    def _load_json_content(full_file_name):
        with open(full_file_name) as f:
            try:
                json_obj = json.load(f)
                return json_obj
            except (FileNotFoundError, json.decoder.JSONDecodeError) as e:
                LogUtil.error(f'json load file {full_file_name} failed ')
                LogUtil.exception(e)

    @staticmethod
    def _load_yml_content(full_file_name):
        with open(full_file_name, 'r') as f:
            try:
                yaml_obj = yaml.safe_load(f)
                return yaml_obj
            except (FileNotFoundError, OSError) as e:
                LogUtil.error(f'yaml load file {full_file_name} failed ')
                LogUtil.exception(e)

    @staticmethod
    def _load_string_content(full_file_name):
        with open(full_file_name) as f:
            try:
                return f.read()
            except FileNotFoundError as e:
                LogUtil.error(f'file {full_file_name} load failed')
                LogUtil.exception(e)

    @staticmethod
    def _get_file_postfix(file_name):
        postfix = None
        if '.' in file_name:
            postfix = file_name.split('.')[-1]
        return postfix
