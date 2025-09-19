#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 熊🐻来个🥬
# @Date:  2025/9/17
# @Description: [对文件功能等的简要描述（可自行添加）]
"""login handler"""

import copy
import base64
import json

import jwt
import requests
import datetime
import time


from core.base_util.log_util import LogUtil
from core.base_util.config_util import ConfigUtil
from core.base_util.singleton import SingletonMeta
from core.base_util.datetime_util import DatetimeUtil


class LoginHandler(metaclass=SingletonMeta):
    """Singleton class of login handler.
    登录处理器的单例类。"""

    login_host = ConfigUtil.get_value('host')
    login_url = ConfigUtil.get_value('login_url')
    refresh_login_url = ConfigUtil.get_value('refresh_login_url')
    refresh_time = ConfigUtil.get_value('refresh_time')
    if not refresh_time:
        refresh_time = 900
    else:
        refresh_time = int(refresh_time)
    user_info = {
        "number":ConfigUtil.get_value('number'),
        'user': ConfigUtil.get_value('user'),
        'password': ConfigUtil.get_value('password')
    }
    # account_name = ConfigUtil.get_value('accountname')
    zone = ConfigUtil.get_value('zone')
    # 缓存访问令牌、刷新令牌和时间戳
    login_cache = {
        'create_time': None,
        'access_token': '',
        'refresh_token': '',
        'csrfToken': ''
    }

    @classmethod
    def update_by_dict(cls, update_info):
        """Updates current user info
        更新当前用户信息

        Args:
            update_info:  target user info, {'user': xxx, 'password': xxx}
                         目标用户信息，格式为 {'user': xxx, 'password': xxx}
        Returns: None

        """
        cls.user_info.update(update_info)

    @classmethod
    def update_key(cls, key, value):
        """Updates the key of user info
        更新用户信息中的指定键值

        Args:
            key: target key in the user info
                 用户信息中的目标键
            value: target value
                   目标值
        Returns:    None

        """
        if key not in cls.user_info.keys():
            LogUtil.warn(f'[update user info] the key value {key} is not recognized')
        cls.user_info[key] = value

    @classmethod
    def get_user_info(cls):
        """Get user information
        获取用户信息

        Returns: a deep copy of the user info
                用户信息的深拷贝

        """
        return copy.deepcopy(cls.user_info)

    @classmethod
    def get_access_token(cls):
        """Gets access token for the user.
        获取用户的访问令牌。

        Returns: access_token
                访问令牌
        """
        token_create_time = cls.login_cache.get('create_time')
        if token_create_time is None:
            access_token = cls.get_login_token(login_type='login')
        elif DatetimeUtil.get_time_delta(token_create_time, datetime.datetime.now()) > cls.refresh_time:
            # refresh access_token when 15min expiration.
            LogUtil.info(f"The auth token is longer than {cls.refresh_time} sec, will be refresh")
            access_token = cls.get_login_token(login_type='refresh')
        else:
            access_token = cls.login_cache.get('access_token')

        return access_token

    def get_erp_login_token(cls, login_type='login'):
        """Gets the login token. Call different API of login or refresh based on login_type.
        获取登录令牌。根据login_type调用不同的登录或刷新API。

        Args:
            login_type(str): login or refresh
                           登录类型：登录或刷新

        Returns:
            access_token(str): user's login access token
                             用户的登录访问令牌
            refresh_token(str): user's refresh token to fresh access token when expired.
                              用户的刷新令牌，用于在访问令牌过期时刷新

        """
        user_password = cls.user_info['user'] + ':' + cls.user_info['password']
        encode_user_info = str(base64.b64encode(user_password.encode('utf-8')), 'utf-8')
        login_auth = f"Basic {encode_user_info}"
        refresh_auth = f"Bearer {cls.login_cache.get('refresh_token')}"
        call_url = cls.refresh_login_url if login_type == 'refresh' else cls.login_url
        auth = refresh_auth if login_type == 'refresh' else login_auth

        headers = {'Authorization': auth, 'X-Account-Name': cls.account_name} if cls.account_name else {
            'Authorization': auth}
        login_url = cls.login_host + call_url
        try:
            res = requests.post(login_url, headers=headers)
        except Exception as e:
            LogUtil.exception(f"Call {login_type} API by user {cls.user_info} exception: {e}.")
            return None
        else:
            if res.status_code != 200:
                LogUtil.warn(f"Call {login_type} API by user {cls.user_info} failed, code: {res.status_code}.")
                return None

        res_data = json.loads(res.text)
        access_token = res_data.get('data').get('signedToken') if cls.account_name else res_data.get('data').get(
            'token').get('access_token')
        refresh_token = res_data.get('data').get('refreshToken') if cls.account_name else res_data.get('data').get(
            'token').get('refresh_token')

        # Todo(wangzifeng): store access_token and refresh_token to redis for 15min expiration.
        cls.login_cache['access_token'] = access_token
        cls.login_cache['refresh_token'] = refresh_token
        cls.login_cache['create_time'] = datetime.datetime.now()

        return access_token


    @classmethod
    def get_login_token(cls, login_type='login'):
        """Gets the login token. Call different API of login or refresh based on login_type.
        获取登录令牌。根据login_type调用不同的登录或刷新API。

        Args:
            login_type(str): login or refresh
                           登录类型：登录或刷新

        Returns:
            access_token(str): user's login access token
                             用户的登录访问令牌
            refresh_token(str): user's refresh token to fresh access token when expired.
                              用户的刷新令牌，用于在访问令牌过期时刷新

        """
        user_password = cls.user_info['user'] + ':' + cls.user_info['password']
        encode_user_info = str(base64.b64encode(user_password.encode('utf-8')), 'utf-8')
        login_auth = f"Basic {encode_user_info}"
        refresh_auth = f"Bearer {cls.login_cache.get('refresh_token')}"
        call_url = cls.refresh_login_url if login_type == 'refresh' else cls.login_url
        auth = refresh_auth if login_type == 'refresh' else login_auth

        headers = {'Authorization': auth, 'X-Account-Name': cls.account_name} if cls.account_name else {
            'Authorization': auth}
        login_url = cls.login_host + call_url
        try:
            res = requests.post(login_url, headers=headers)
        except Exception as e:
            LogUtil.exception(f"Call {login_type} API by user {cls.user_info} exception: {e}.")
            return None
        else:
            if res.status_code != 200:
                LogUtil.warn(f"Call {login_type} API by user {cls.user_info} failed, code: {res.status_code}.")
                return None

        res_data = json.loads(res.text)
        access_token = res_data.get('data').get('signedToken') if cls.account_name else res_data.get('data').get(
            'token').get('access_token')
        refresh_token = res_data.get('data').get('refreshToken') if cls.account_name else res_data.get('data').get(
            'token').get('refresh_token')

        # Todo(wangzifeng): store access_token and refresh_token to redis for 15min expiration.
        cls.login_cache['access_token'] = access_token
        cls.login_cache['refresh_token'] = refresh_token
        cls.login_cache['create_time'] = datetime.datetime.now()

        return access_token

    @classmethod  # todo: to check if volcano has refresh token
    def get_volc_access_token(cls):
        """Gets volc access token for the user.
        获取用户的火山引擎访问令牌。

        Returns: volc_access_token
                火山引擎访问令牌
        """
        token_create_time = cls.login_cache.get('create_time')
        if token_create_time is None:
            access_token, csrfToken = cls.get_volc_login_token(login_type='login')
        elif DatetimeUtil.get_time_delta(token_create_time, datetime.datetime.now()) > 900:
            # refresh access_token when 15min expiration.
            access_token = cls.get_volc_login_token(login_type='refresh')
        else:
            access_token = cls.login_cache.get('access_token')
            csrfToken = cls.login_cache.get('csrfToken')

        return access_token, csrfToken

    @classmethod
    def get_volc_login_token(cls, login_type='login'):
        """Gets the volc login token. Call different API of login or refresh based on login_type.
        获取火山引擎登录令牌。根据login_type调用不同的登录或刷新API。

        Args:
            login_type(str): login type. 'login' means first login; 'refresh' means to refresh token.
                           登录类型。'login'表示首次登录；'refresh'表示刷新令牌。

        Returns:
            access_token(str): user's login access token
                             用户的登录访问令牌
            refresh_token(str): user's refresh token to fresh access token when expired.
                              用户的刷新令牌，用于在访问令牌过期时刷新

        """
        user_password = cls.user_info['user'] + ':' + cls.user_info['password']
        encode_user_info = str(base64.b64encode(user_password.encode('utf-8')), 'utf-8')
        login_auth = f"Basic {encode_user_info}"
        refresh_auth = f"Bearer {cls.login_cache.get('refresh_token')}"
        call_url = cls.refresh_login_url if login_type == 'refresh' else cls.login_url
        auth = refresh_auth if login_type == 'refresh' else login_auth
        login_url = cls.login_host + call_url
        data_set = {'Identity': cls.user_info['user'], 'DataRangersLogin': False, 'Password': cls.user_info['password']}
        try:
            session = requests.Session()
            session.get(login_url)
            cookie = session.cookies

            # Set CSRF-Token
            headers = {'Authorization': auth, 'x-csrf-token': cookie['csrfToken']}

            res = session.post(login_url, cookies=cookie, json=data_set, headers=headers)
            session.get("https://v-vconsole-stable.bytedance.net/home")

        except Exception as e:
            LogUtil.exception(f"Call {login_type} API by user {cls.user_info} exception: {e}.")
            return None
        else:
            if res.status_code != 200:
                LogUtil.warn(f"Call {login_type} API by user {cls.user_info} failed, code: {res.status_code}.")
                return None

        res_data = json.loads(res.text)
        access_token = res_data.get('Result').get('JWT')
        csrfToken = session.cookies['csrfToken']

        cls.login_cache['access_token'] = access_token
        cls.login_cache['create_time'] = datetime.datetime.now()
        cls.login_cache['csrfToken'] = csrfToken

        return access_token, csrfToken

    @classmethod
    def get_volc_bh_access_token(cls):
        """Gets volc bh access token for the user.
        获取用户的火山引擎北海访问令牌。

        Returns: volc_bh_access_token
                火山引擎北海访问令牌
        """
        token_create_time = cls.login_cache.get('create_time')
        if token_create_time is None or DatetimeUtil.get_time_delta(token_create_time, datetime.datetime.now()) > 900:
            access_token = cls.get_volc_bh_login_token()
        else:
            access_token = cls.login_cache.get('access_token')
        return access_token

    @classmethod
    def get_volc_bh_login_token(cls, login_type='login'):
        """Gets the volc bh login token. Call different API of login or refresh based on login_type.
        获取火山引擎北海登录令牌。根据login_type调用不同的登录或刷新API。

        Args:
            login_type(str): login type. 'login' means first login; 'refresh' means to refresh token.
                           登录类型。'login'表示首次登录；'refresh'表示刷新令牌。

        Returns:
            access_token(str): user's login access token
                             用户的登录访问令牌
            refresh_token(str): user's refresh token to fresh access token when expired.
                              用户的刷新令牌，用于在访问令牌过期时刷新

        """
        issuer = "bytehouse"
        key_id_header = "kid"
        private_key = "-----BEGIN RSA PRIVATE KEY-----\nMIIEogIBAAKCAQEAv0K8naX0sfT6WWgkpkARZwKKtLWu2vREmtx3OEQiccRQElB6\ncc7SUP/8kq4W3Tz7qr2WVfDWxiLEeVPpD+ZkSITEy9n2yPwMWS1zSgn3be1cXveR\nK9SzJSHLavdFGVQ8jVljhwWXpIFfDZlvZb+nFc75WREGOwXDGOZcKg3eF9fRqMTy\nAQApyOqQXg88qJFm7dPl45QHA5/5rinuVA7VDZ04smY/DnXfxJjRXoRRlVnTOFGT\n2Zldb7WepenlMmP/McCFcz5ZnZ1veaCcEAFc20G6FqYPS3e9fRPIubYI+oCvagOS\nn/QciSsPsOuOu0Z4LW+6/fERZDHv4vio/n5mVwIDAQABAoIBADISwNrtRgEJSDn8\nIAw+nc/ARJxHLL46UXPR4Iykmff7E5OX6la9dSarvm6QkX/epWzwMdnSMgixtYqm\nQ1BcW0j5KaTNLeU0x+7ZDWQG8/advB9I5YL6LuS70kvw7PBSs3+2NW52MltpW39t\n+lJDOPVmuLVu1ZjCS2/Lb7m647iN3ndZUpTZEMO6u6wBGptGImHumPGJbbVGnYpn\nD1XAgfD0ilmXKuO/dILRZKSHdZzkeH6vHJzUkArZcVEDSCBbUEmyu+vTGerZ7cvw\ne929eapx+Yjzb5eJKgV9S/T92WhNDRj2xIZlIMuSNJVlvDaiBYEE0DCfkYws7pZk\nlVXlN5ECgYEA4426LDcMRj9OvuKWLGHVC0NLGdVtzoAkR20/ARVV5TVfX5lR3coo\n4oaONQG0zUmvIf3Zgkrdfx9zFACDyDsrsZjbtH4eJVnFgYy4rUsiRYkVDeDYJCH8\n4iyqFNKXXT6qu4NjIzVPSXjb+SDgo8nd3BO6AYKCYNKUs5m80d0qMm0CgYEA1yuM\nAxQNK1nubNmMPeWBR4XgN1REupO2JCsvWr8v8dJ5qIu7t5xp/XocheTZ3ocElJgk\nw9MM9hriIAUWe3INDg1YZLfod2BnJziEY2lUykZGCYluqQV7MQka0C/nOLoZIdrP\n2+2thSPmKtSFekpUSVZ1wjvYpm1KmKbij+yQIVMCgYAClG3C6JDcDwWuhlUbhbRr\nn0Svs0q+Z5eBs8xeD8bchWFibROPhyY1gz8DfNR261nv8bfQkVa3hTzBwku8LmeN\naOU8w51F4SGrGVRSqqJl1WsGsEDjD/uU+Nqox8ZtiTNYUuIB2S3f8F3WEjhZwwUf\n5J1cPQWLYXfMHXcVjgNXdQKBgCHOlMQTDXKnQZ/WmoNLIQHU1gK7ecT62l5abqlK\nasUK9dR2h/r0V27dFcgvyc991Ulnkjc2XM36MVcolXy10blIfX/tqVfATNTLu3lH\nHmxdmDl9X2atFssAjDbzn9e43aQFFi2O7XmCx3IpTAOH1DBlpkDrWEHl4BeV+Pj2\nCTtDAoGAWfNkYQXQTEhuS6DwNBP6QrpC4SzU0kllTi319iL/gLmt+y2GJwE61pJ0\nkgAo8XA+qsS04/LdzF9I3rkIYxXxWyBNHrvGhydhNt2HfC13ZcVBs1XINa4aXadn\nrdpfx7cGCzbHEw9mbT3/UCco4f1JEmlWhjJYIXkzNY+a0vhUV3U=\n-----END RSA PRIVATE KEY-----"
        payload = {
            "aud": [issuer],
            "exp": datetime.datetime.now() + datetime.timedelta(minutes=15),
            "isa": datetime.datetime.now().timestamp(),
            "iss": issuer
        }
        headers = {
            key_id_header: "bytehouse"
        }
        access_token = jwt.encode(payload=payload, headers=headers, algorithm="RS256", key=private_key)
        cls.login_cache['access_token'] = access_token
        cls.login_cache['create_time'] = datetime.datetime.now()

        return access_tok
if __name__ == '__main__':
    login_handler = LoginHandler()
    login_handler.get_access_token()
    time.sleep(60)
    print('zifengw debug: already sleep 60')
    login_handler.get_access_token()
    time.sleep(300)
    print('zifengw debug: already sleep 300')
    login_handler.get_access_token()
    time.sleep(1000)
    print('zifengw debug: already sleep 1000')
    login_handler.get_access_token()
