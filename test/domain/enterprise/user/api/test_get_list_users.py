#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 熊🐻来个🥬
# @Date:  2025/9/17
# @Description: [对文件功能等的简要描述（可自行添加）]

import pytest
from app.enterprise.user.caller.user_http_caller import UserHttpCaller
from core.base_util.log_util import LogUtil
from core.pytest_util.caseinfo import CaseInfo
from core.data_util.mock_data_util import MockDataUtil
from core.base_util.config_util import ConfigUtil
from core.data_util.json_validator import jsonschema_validator
from test.domain.enterprise.user.api import USER_SCHEMA_LOADER

@pytest.mark.xdist_group(name="User")
class TestGetListUsers:
    """test class for get user list api"""
    @CaseInfo.title("这是测试用户列表的happy path 在本地")
    @CaseInfo.owner("miss_xiong")
    @CaseInfo.priority("P0")
    @CaseInfo.zone("onprem")
    def test_get_list_users(self):
        # 需要实例化后再调用实例方法
        code,resp = UserHttpCaller().list_users()
        assert code == 200
        schema = USER_SCHEMA_LOADER.get_schema("test_get_list_users")
        assert schema is not None
