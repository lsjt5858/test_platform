#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 熊🐻来个🥬
# @Date:  2025/9/17
# @Description: [对文件功能等的简要描述（可自行添加）]

"user API HTTP URLs"

from core.protocol.app_enum import HttpApi

class UserHttpApiUrls(HttpApi):
    """user API HTTP URLs"""

    USER_LIST_URL = ("/api/users/","GET: READY List existing users")
    CREATE_USER_URL = ("/api/users/","POST: CREATE New user")
    

