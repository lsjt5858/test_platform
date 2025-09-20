#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 熊🐻来个🥬
# @Date:  2025/9/17
# @Description: [对文件功能等的简要描述（可自行添加）]

from app.enterprise.user.constants.user_http_api_urls import UserHttpApiUrls
from core.base_util.config_util import ConfigUtil
ConfigUtil.reload()
from core.protocol.app_enum import psm
from core.protocol.http_handler import ERPHttpHandler,HttpHandler
from core.base_util.log_util import LogUtil

@psm('p,s,m')
class UserHttpCaller:
    """HTTP Caller class for User API"""
    def __init__(self,hostname=None):
        if hostname is None:
            hostname = ConfigUtil.get_value('host')
        if ConfigUtil.get_zone() == "onprem":
            self.http_client = ERPHttpHandler(hostname)
        else:
            self.http_client = ERPHttpHandler(hostname)
        self.origin_http_client = HttpHandler(hostname)

    def list_users(self,headers=None):
        """list users API Caller"""
        LogUtil.info("call list users api...")
        code,res_data = self.http_client.get(
            UserHttpApiUrls.USER_LIST_URL,
            headers=headers
        )

        return code,res_data if code==200 and  res_data else None

    def create_user(self,data=None,headers=None):
        """create user API Caller"""
        LogUtil.info("call create user api...")
        code,res_data = self.http_client.post(
            UserHttpApiUrls.CREATE_USER_URL,
            data=data,
            headers=headers
        )
        return code,res_data if code==201 and res_data else None

if __name__ == '__main__':
    user_call = UserHttpCaller()
    # code,res_data = user_call.list_users()
    code,res_data = user_call.create_user()
    print(code,res_data)