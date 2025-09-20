#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 熊🐻来个🥬
# @Date:  2025/9/19
# @Description: [对文件功能等的简要描述（可自行添加）]

from app.enterprise.user.caller.user_http_caller import UserHttpCaller
from core.base_util.log_util import LogUtil
from core.data_util.mock_data_util import MockDataUtil

class UserHttpBizOps:

    @staticmethod
    def create_user_onprem():
        username = "auto_user_" + MockDataUtil.random_gen_string(3).lower()
        data={
            "username": username,
            "name": username,
            # 使用本地手机号生成工具，避免 locale 必填参数
            "phone": MockDataUtil.random_gen_mobile_number(),
            "email": f"{MockDataUtil.random_gen_email()}",
            "sex": MockDataUtil.random_gen_sex(),
            "roles": [

            ],
            "is_active": MockDataUtil.true_or_false(),
        }
        # create_user 是实例方法，这里需要先实例化调用，避免把 data 误传给 self
        code,resp = UserHttpCaller().create_user(data)
        assert code == 201
        return resp


if __name__ == '__main__':
    user_call = UserHttpBizOps.create_user_onprem()
    print(user_call)
