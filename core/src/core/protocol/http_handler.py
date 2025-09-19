#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 熊🐻来个🥬
# @Date:  2025/9/17
# @Description: HTTP请求处理器 - 封装requests模块，提供更便捷的HTTP请求功能，包含日志记录

"""HTTP请求处理器 / HTTP Handler"""
import base64
import datetime
import json
import textwrap
import time
import urllib
import requests
from json import JSONDecodeError
import re

from core.base_util.config_util import ConfigUtil
from core.base_util.datetime_util import DatetimeUtil
from core.base_util.log_util import LogUtil
from core.protocol.app_enum import HttpApi
from core.protocol.login_handler import LoginHandler

class HttpHandler:
    """封装requests模块以便更容易使用，包含日志信息。
    Encapsulates requests module for easier usage, log info included.

    Args:
        host(str): 此对象发出的所有请求的主机地址 / host for all the request made by this object
        env(str): boe标签。如果未提供，将首先尝试从env.ini中获取[env]的值，否则使用'prod'
                 / boe tag. if not given, will try to get value of [env] in env.ini first, otherwise use 'prod'
        headers(dict): 与此对象发出的所有请求一起发送的请求头 / headers to send with all the request made by this object
        cookies(dict): 与self.cookies一起发送的cookies / cookies to send together with self.cookies

    Example:
        >>> from core.protocol.http_handler import HttpHandler
        >>> handler = HttpHandler(host='host')
        >>> handler.post(api='api', data={}, headers={}, files={})
    """
    _print_log = True
    _use_boe = True

    def __init__(self, host, env=None, headers=None, cookie=None):
        self.host = host.rstrip('/')
        if not env:
            env = ConfigUtil.get_env() or 'prod'
        self.env = env

        # headers and cookies and auth(could be None)
        zone = ConfigUtil.get_zone().lower()
        self._use_boe = 'boe' in zone
        if self._use_boe:
            boe_headers = {
                'x-use-boe': '1',
                'X-TT-ENV': self.env
            }
            self.headers = {**headers, **boe_headers} if headers else boe_headers
        else:
            self.headers = headers
        self.cookies = cookie

    @property
    def print_log(self):
        return self._print_log

    @print_log.setter
    def print_log(self, flag):
        self._print_log = flag

    @property
    def use_boe(self):
        return self._use_boe

    @use_boe.setter
    def use_boe(self, flag):
        if flag is False and 'x-use-boe' in self.headers.keys():
            del self.headers['x-use-boe']
            del self.headers['X-TT-ENV']
        self._use_boe = flag

    def request(self, method, api, params=None, data=None, is_json=True, files=None,
                headers=None, cookies=None, auto_retry=False, retry_times=5,
                interval=1, checker=None, timeout=30):
        """make a http request

        Args:
            method(str): 'POST', 'GET', 'PUT', 'DELETE', etc.
            api(HttpApi or str): api string or HttpApi object of the request
            params(dict or list[tuple] or bytes): send in the query string for the request
            data(dict): dict to send in the body of the request
            is_json(bool): if the data to send is in json format
            files(dict): dict of files to send, key: filename, value: file object
            headers(dict): headers to send together with self.headers
                (replace duplicate keys of self.headers)
            cookies(dict): cookies to send together with self.cookies
                (replace duplicate keys of self.cookies)
            auto_retry(bool): if allow auto retry
            retry_times(int): retry times, works only when auto_retry=True
            interval(int): wait interval during retry, in seconds, works only when
                auto_retry=True
            checker(function or any): check(code, msg) if request has expected return values,
                default to check code==200, works only when auto_retry=True
            timeout(int or float): request timeout, in second, default 30s

        Returns:
            tuple: (code, msg) -- msg is a dict if response.text is json serializable
        """
        if isinstance(api, HttpApi):
            end_point = api.api
            desc = api.desc
        else:
            end_point = api
            desc = ''

        url = '/'.join([self.host, end_point.lstrip('/')])

        if self.headers:
            headers = {**self.headers, **headers} if headers else self.headers
        if self.cookies:
            cookies = {**self.cookies, **cookies} if cookies else self.cookies

        # 处理json格式的数据 / process data in json form
        if is_json:
            content_type = {'Content-Type': 'application/json'}
            headers = {**headers, **content_type} if headers else content_type
            data = json.dumps(data)

        return self._request_inner(desc=desc, auto_retry=auto_retry, retry_times=retry_times,
                                   interval=interval, checker=checker, method=method, url=url,
                                   params=params, data=data, files=files, headers=headers,
                                   cookies=cookies, timeout=timeout)

    def post(self, api, params=None, data=None, is_json=True, files=None, headers=None,
             cookies=None, auto_retry=False, retry_times=5, interval=1,
             checker=None, timeout=30):
        """发起POST请求 / make a post request

        Args:
            api(HttpApi or str): 请求的API字符串或HttpApi对象 / api string or HttpApi object of the request
            params(dict or list[tuple] or bytes): 在查询字符串中发送的参数 / send in the query string for the request
            data(dict): 在请求体中发送的数据字典 / dict to send in the body of the request
            is_json(bool): 发送的数据是否为json格式 / if the data to send is in json form
            files(dict): 要发送的文件字典，键：文件名，值：文件对象 / dict of files to send, key: filename, value: file object
            headers(dict): 与self.headers一起发送的请求头（替换self.headers的重复键）
                          / headers to send together with self.headers (replace duplicate keys of self.headers)
            cookies(dict): 与self.cookies一起发送的cookies（替换self.cookies的重复键）
                          / cookies to send together with self.cookies (replace duplicate keys of self.cookies)
            auto_retry(bool): 是否允许自动重试 / if allow auto retry
            retry_times(int): 重试次数，仅在auto_retry=True时有效 / retry times, works only when auto_retry=True
            interval(int): 重试期间的等待间隔，单位秒，仅在auto_retry=True时有效
                          / wait interval during retry, in seconds, works only when auto_retry=True
            checker: 检查(code, msg)请求是否有预期的返回值，默认检查code==200，仅在auto_retry=True时有效
                    / check(code, msg) if request has expected return values, default to check code==200, works only when auto_retry=True
            timeout(int or float): 请求超时时间，单位秒，默认30秒 / request timeout, in second, default 30s

        Returns:
            tuple: (code, msg) -- 如果response.text可以json序列化，msg是一个字典
                  / (code, msg) -- msg is a dict if response.text is json serializable
        """
        return self.request('POST', api=api, params=params, data=data, is_json=is_json,
                            files=files, headers=headers, cookies=cookies,
                            auto_retry=auto_retry, retry_times=retry_times,
                            interval=interval, checker=checker, timeout=timeout)

    def get(self, api, params=None, headers=None, cookies=None, auto_retry=False,
            retry_times=5, interval=1, checker=None, timeout=30):
        """发起GET请求 / make a get request

        Args:
            api(HttpApi or str): 请求的API字符串或HttpApi对象 / api string or HttpApi object of the request
            params(dict or list[tuple] or bytes): 在查询字符串中发送的参数 / send in the query string for the request
            headers(dict): 与self.headers一起发送的请求头（替换self.headers的重复键）
                          / headers to send together with self.headers (replace duplicate keys of self.headers)
            cookies(dict): 与self.cookies一起发送的cookies（替换self.cookies的重复键）
                          / cookies to send together with self.cookies (replace duplicate keys of self.cookies)
            auto_retry(bool): 是否允许自动重试 / if allow auto retry
            retry_times(int): 重试次数，仅在auto_retry=True时有效 / retry times, works only when auto_retry=True
            interval(int): 重试期间的等待间隔，单位秒，仅在auto_retry=True时有效
                          / wait interval during retry, in seconds, works only when auto_retry=True
            checker(function or any): 检查(code, msg)请求是否有预期的返回值，默认检查code==200，仅在auto_retry=True时有效
                                     / check(code, msg) if request has expected return values, default to check code==200, works only when auto_retry=True
            timeout(int or float): 请求超时时间，单位秒，默认30秒 / request timeout, in second, default 30s

        Returns:
            tuple: (code, msg) -- 如果response.text可以json序列化，msg是一个字典
                  / (code, msg) -- msg is a dict if response.text is json serializable
        """
        return self.request('GET', api=api, params=params, is_json=False, headers=headers,
                            cookies=cookies, auto_retry=auto_retry, retry_times=retry_times,
                            interval=interval, checker=checker, timeout=timeout)

    def put(self, api, params=None, data=None, is_json=True, files=None,
            headers=None, cookies=None, auto_retry=False, retry_times=5,
            interval=1, checker=None, timeout=30):
        """发起PUT请求 / make a put request

        Args:
            api(HttpApi or str): 请求的API字符串或HttpApi对象 / api string or HttpApi object of the request
            params(dict or list[tuple] or bytes): 在查询字符串中发送的参数 / send in the query string for the request
            data(dict): 在请求体中发送的数据字典 / dict to send in the body of the request
            is_json(bool): 发送的数据是否为json格式 / if the data to send is in json form
            files(dict): 要发送的文件字典，键：文件名，值：文件对象 / dict of files to send, key: filename, value: file object
            headers(dict): 与self.headers一起发送的请求头（替换self.headers的重复键）
                          / headers to send together with self.headers (replace duplicate keys of self.headers)
            cookies(dict): 与self.cookies一起发送的cookies（替换self.cookies的重复键）
                          / cookies to send together with self.cookies (replace duplicate keys of self.cookies)
            auto_retry(bool): 是否允许自动重试 / if allow auto retry
            retry_times(int): 重试次数，仅在auto_retry=True时有效 / retry times, works only when auto_retry=True
            interval(int): 重试期间的等待间隔，单位秒，仅在auto_retry=True时有效
                          / wait interval during retry, in seconds, works only when auto_retry=True
            checker(function or any): 检查(code, msg)请求是否有预期的返回值，默认检查code==200，仅在auto_retry=True时有效
                                     / check(code, msg) if request has expected return values, default to check code==200, works only when auto_retry=True
            timeout(int or float): 请求超时时间，单位秒，默认30秒 / request timeout, in second, default 30s

        Returns:
            tuple: (code, msg) -- 如果response.text可以json序列化，msg是一个字典
                  / (code, msg) -- msg is a dict if response.text is json serializable
        """
        return self.request('PUT', api=api, params=params, data=data, is_json=is_json,
                            files=files, headers=headers, cookies=cookies,
                            auto_retry=auto_retry, retry_times=retry_times,
                            interval=interval, checker=checker, timeout=timeout)

    def delete(self, api, params=None, data=None, is_json=True, files=None,
               headers=None, cookies=None, auto_retry=False, retry_times=5,
               interval=1, checker=None, timeout=30):
        """发起DELETE请求 / make a delete request

        Args:
            api(HttpApi or str): 请求的API字符串或HttpApi对象 / api string or HttpApi object of the request
            params(dict or list[tuple] or bytes): 在查询字符串中发送的参数 / send in the query string for the request
            data(dict): 在请求体中发送的数据字典 / dict to send in the body of the request
            is_json(bool): 发送的数据是否为json格式 / if the data to send is in json form
            files(dict): 要发送的文件字典，键：文件名，值：文件对象 / dict of files to send, key: filename, value: file object
            headers(dict): 与self.headers一起发送的请求头（替换self.headers的重复键）
                          / headers to send together with self.headers (replace duplicate keys of self.headers)
            cookies(dict): 与self.cookies一起发送的cookies（替换self.cookies的重复键）
                          / cookies to send together with self.cookies (replace duplicate keys of self.cookies)
            auto_retry(bool): 是否允许自动重试 / if allow auto retry
            retry_times(int): 重试次数，仅在auto_retry=True时有效 / retry times, works only when auto_retry=True
            interval(int): 重试期间的等待间隔，单位秒，仅在auto_retry=True时有效
                          / wait interval during retry, in seconds, works only when auto_retry=True
            checker(function or any): 检查(code, msg)请求是否有预期的返回值，默认检查code==200，仅在auto_retry=True时有效
                                     / check(code, msg) if request has expected return values, default to check code==200, works only when auto_retry=True
            timeout(int or float): 请求超时时间，单位秒，默认30秒 / request timeout, in second, default 30s

        Returns:
            tuple: (code, body) -- 如果response.text可以json序列化，body是一个字典
                  / (code, body) -- body is a dict if response.text is json serializable
        """
        return self.request('DELETE', api=api, params=params, data=data, is_json=is_json,
                            files=files, headers=headers, cookies=cookies,
                            auto_retry=auto_retry, retry_times=retry_times,
                            interval=interval, checker=checker, timeout=timeout)

    def patch(self, api, params=None, data=None, is_json=True, files=None,
              headers=None, cookies=None, auto_retry=False, retry_times=5,
              interval=1, checker=None, timeout=30):
        """发起PATCH请求 / make a patch request

        Args:
            api(HttpApi or str): 请求的API字符串或HttpApi对象 / api string or HttpApi object of the request
            params(dict or list[tuple] or bytes): 在查询字符串中发送的参数 / send in the query string for the request
            data(dict): 在请求体中发送的数据字典 / dict to send in the body of the request
            is_json(bool): 发送的数据是否为json格式 / if the data to send is in json form
            files(dict): 要发送的文件字典，键：文件名，值：文件对象 / dict of files to send, key: filename, value: file object
            headers(dict): 与self.headers一起发送的请求头（替换self.headers的重复键）
                          / headers to send together with self.headers (replace duplicate keys of self.headers)
            cookies(dict): 与self.cookies一起发送的cookies（替换self.cookies的重复键）
                          / cookies to send together with self.cookies (replace duplicate keys of self.cookies)
            auto_retry(bool): 是否允许自动重试 / if allow auto retry
            retry_times(int): 重试次数，仅在auto_retry=True时有效 / retry times, works only when auto_retry=True
            interval(int): 重试期间的等待间隔，单位秒，仅在auto_retry=True时有效
                          / wait interval during retry, in seconds, works only when auto_retry=True
            checker(function or any): 检查(code, msg)请求是否有预期的返回值，默认检查code==200，仅在auto_retry=True时有效
                                     / check(code, msg) if request has expected return values, default to check code==200, works only when auto_retry=True
            timeout(int or float): 请求超时时间，单位秒，默认30秒 / request timeout, in second, default 30s

        Returns:
            tuple: (code, msg) -- 如果response.text可以json序列化，msg是一个字典
                  / (code, msg) -- msg is a dict if response.text is json serializable
        """
        return self.request('PATCH', api=api, params=params, data=data, is_json=is_json,
                            files=files, headers=headers, cookies=cookies,
                            auto_retry=auto_retry, retry_times=retry_times,
                            interval=interval, checker=checker, timeout=timeout)

    # ----------------------------------------
    #            受保护的方法 / protected methods           |
    # ----------------------------------------

    def _request_inner(self, desc, auto_retry, retry_times, interval, checker, **kwargs):
        if not auto_retry:
            retry_times = 1
        elif not checker:
            def default_checker(status_code, _):
                return status_code == 200

            checker = default_checker

        count = 0
        while count < retry_times:
            code, msg = self._request(desc, **kwargs)
            count += 1
            if count < retry_times and not checker(code, msg):
                time.sleep(interval)
                LogUtil.info(f'request check condition failed, retry after {interval} seconds...')
            else:
                break
        return code, msg

    def _request(self, desc, **kwargs):
        try:
            # 发送请求 / send request
            start = datetime.datetime.now()
            response = requests.request(**kwargs)
            end = datetime.datetime.now()

            # 获取日志ID（如果存在）/ get log id if exists
            log_id = None
            for k, v in response.headers.items():
                if 'logid' in k.lower() or 'log_id' in k.lower():
                    log_id = v
                    break

            # 处理返回数据 / process return data
            content_type = response.headers.get('Content-Type', '')
            if 'image' in content_type or 'pdf' in content_type:
                body = response.content
            else:
                body = response.text

            try:
                body = json.loads(body)
            except (JSONDecodeError, UnicodeDecodeError):
                pass

            code = response.status_code

            # 处理日志 / process log
            if self.print_log:
                self._log_prepared_request(
                    response.request, desc, data=kwargs.get('data', {}))
                self._log_response(content_type, body, code,
                                   DatetimeUtil.get_time_delta(start, end), desc, log_id)

        except Exception as e:
            self._log_exception_msg(desc, e, **kwargs)
            return -1, ''
        else:
            if code != 200:
                LogUtil.warning("http response code is not 200!")
            return code, body

    @staticmethod
    def _log_exception_msg(desc, e, **kwargs):
        l_split = '[' if desc else ''
        r_split = ']' if desc else ''
        LogUtil.error(f'{l_split}{desc}{r_split} HTTP request failed! Exception Info: {e}', exc_info=True)

        space = ''.ljust(4)
        url = f'{space}URL: {kwargs.get("method")}  {kwargs.get("url")}\n'
        headers = f'{space}Headers: \n{space}{kwargs.get("headers")}\n' if kwargs.get('headers') else ''
        cookies = f'{space}Cookies: \n{space}{kwargs.get("cookies")}\n' if kwargs.get('cookies') else ''
        params = f'{space}Params: \n{space}{kwargs.get("params")}\n' if kwargs.get('params') else ''
        data = f'{space}Data: \n{space}{kwargs.get("data")}\n' if kwargs.get('data') else ''
        files = f'{space}Files: \n{space}{kwargs.get("files")}\n' if kwargs.get('files') else ''
        LogUtil.error('Request Info:\n' + url + headers + cookies + params + data + files)

    @staticmethod
    def _log_prepared_request(req, desc, data=None):
        redundant_header_keys = ['User-Agent', 'Accept-Encoding', 'Accept', 'Connection',
                                 'x-use-boe', 'Content-Length']
        headers = '\n'.join(f'{k}: {v}' for k, v in req.headers.items()
                            if k not in redundant_header_keys)

        content_type = req.headers.get('Content-Type', '')

        if 'application/json' in content_type:
            try:
                body = json.dumps(json.loads(req.body), indent=4,
                                  ensure_ascii=False).replace('\\', '')
            except (JSONDecodeError, UnicodeDecodeError):
                body = req.body
        else:
            body = req.body

        # 当请求体内有文件时，req.body是以bytes的形式存储，打印出来不可读
        # 用data来代替body的打印内容
        # 仅打印参数部分，不打印文件部分
        # When the request body contains files, req.body is stored in bytes format, which is unreadable when printed
        # Use data to replace the printed content of body
        # Only print the parameter part, not the file part
        if isinstance(body, bytes):
            try:
                body = json.dumps(data, indent=4, ensure_ascii=False).replace('\\', '')
            except (JSONDecodeError, UnicodeDecodeError):
                body = '-'

        if req.method == 'GET':
            format_request = textwrap.dedent("""
            --------------------- REQUEST START {desc}------------------
            endpoint: {method} {url}
            headers:
            {headers}
            ----------------------------- REQUEST END ---------------------------
            """).strip().format(
                desc=desc,
                method=req.method,
                url=urllib.parse.unquote(req.url),
                headers=textwrap.indent(headers, '  ')
            )
        else:
            format_request = textwrap.dedent("""
            --------------------- REQUEST START {desc}------------------
            endpoint: {method} {url}
            headers:
            {headers}
            body:
            {body}
            ----------------------------- REQUEST END ---------------------------
            """).strip().format(
                desc=desc,
                method=req.method,
                url=urllib.parse.unquote(req.url),
                headers=textwrap.indent(headers, '  '),
                body=(textwrap.indent(body, ' ') if body else '  -')
            )
        LogUtil.info('\n' + format_request + '\n')

    @staticmethod
    def _log_response(content_type, body, code, delta, desc, log_id):
        try:
            body = json.dumps(body, indent=4,
                              ensure_ascii=False).replace('\\', '')
        except (JSONDecodeError, UnicodeDecodeError, TypeError):
            pass

        # 目前对于body返回bytes的情况统一按照"utf-8"来转换，
        # 如果有发现新的编码，需要再想办法处理
        # Currently, for the case where body returns bytes, it is uniformly converted according to "utf-8",
        # If new encoding is found, we need to find another way to handle it
        if isinstance(body, bytes):
            try:
                body = str(body, encoding="utf-8")
            except UnicodeDecodeError:
                body = '-'

        format_response = textwrap.dedent("""
                    ----------------------------- RESPONSE START {desc}--------------
                    content_type: {content_type}
                    status_code: {status_code}
                    log_id: {log_id}
                    cost: {delta}s
                    body:
                    {body}
                    ----------------------------- RESPONSE END --------------------------
                    """).strip()

        format_response = format_response.format(
            desc=desc,
            content_type=content_type,
            status_code=code,
            log_id=log_id or '-',
            delta=delta,
            body=textwrap.indent(body, '  '),
        )
        LogUtil.info('\n' + format_response + '\n')


class ERPHttpHandler(HttpHandler):

    """封装了ERP云企业登录信息的HTTP处理器 / http handler encapsulated with ERP cloud enterprise login info"""
    def request(self, method, api, params=None, data=None, is_json=True, files=None,
                headers=None, cookies=None, login_info=None, auto_retry=False,
                retry_times=5, interval=1, checker=None, timeout=30):
        """使用企业版登录信息发起HTTP请求 / make a http request with ce login info

                Args:
                    method(str): 请求方法 'POST', 'GET', 'PUT', 'DELETE' / 'POST', 'GET', 'PUT', 'DELETE'
                    api(HttpApi or str): 请求的API字符串或HttpApi对象 / api string or HttpApi object of the request
                    params(dict or list[tuple] or bytes): 在查询字符串中发送的参数 / send in the query string for the request
                    data(dict): 在请求体中发送的数据字典 / dict to send in the body of the request
                    is_json(bool): 发送的数据是否为json格式 / if the data to send is in json form
                    files(dict): 要发送的文件字典，键：文件名，值：文件对象 / dict of files to send, key: filename, value: file object
                    headers(dict): 与self.headers一起发送的请求头（替换self.headers的重复键）
                                  / headers to send together with self.headers (replace duplicate keys of self.headers)
                    cookies(dict): 与self.cookies一起发送的cookies（替换self.cookies的重复键）
                                  / cookies to send together with self.cookies (replace duplicate keys of self.cookies)
                    login_info(dict): 如果提供，将发送此信息而不是LoginUtil.get_current_employee_info()的结果
                                     / if given, will send instead of LoginUtil.get_current_employee_info() result
                    auto_retry(bool): 是否允许自动重试 / if allow auto retry
                    retry_times(int): 重试次数，仅在auto_retry=True时有效 / retry times, works only when auto_retry=True
                    interval(int): 重试期间的等待间隔，单位秒，仅在auto_retry=True时有效
                                  / wait interval during retry, in seconds, works only when auto_retry=True
                    checker(function or any): 检查(code, msg)请求是否有预期的返回值，默认检查code==200，仅在auto_retry=True时有效
                                             / check(code, msg) if request has expected return values, default to check code==200, works only when auto_retry=True
                    timeout(int or float): 请求超时时间，单位秒，默认30秒 / request timeout, in second, default 30s

                Returns:
                    tuple: (code, msg) -- 如果response.text可以json序列化，msg是一个字典
                          / (code, msg) -- msg is a dict if response.text is json serializable
                """
        headers = {**self._construct_access_auth(),
                   **headers} if headers else self._construct_access_auth()
        return super().request(method=method, api=api, params=params, data=data, is_json=is_json,
                               files=files, headers=headers, cookies=cookies, auto_retry=auto_retry,
                               retry_times=retry_times, interval=interval, checker=checker, timeout=timeout)

    def post(self, api, params=None, data=None, is_json=True, files=None,
             headers=None, cookies=None, login_info=None, auto_retry=False,
             retry_times=5, interval=1, checker=None, timeout=30):
        """make a post request with ce login info

        Args:
            api(HttpApi or str): api string or HttpApi object of the request
            params(dict or list[tuple] or bytes): send in the query string for the request
            data(dict): dict to send in the body of the request
            is_json(bool): if the data to send is in json form
            files(dict): dict of files to send, key: filename, value: file object
            headers(dict): headers to send together with self.headers
                (replace duplicate keys of self.headers)
            cookies(dict): cookies to send together with self.cookies
                (replace duplicate keys of self.cookies)
            login_info(dict): if given, will send instead of
                LoginUtil.get_current_employee_info() result
            auto_retry(bool): if allow auto retry
            retry_times(int): retry times, works only when auto_retry=True
            interval(int): wait interval during retry, in seconds, works only when
                auto_retry=True
            checker(function or any): check(code, msg) if request has expected return values,
                default to check code==200, works only when auto_retry=True
            timeout(int or float): request timeout, in second, default 30s

        Returns:
            tuple: (code, msg) -- msg is a dict if response.text is json serializable
        """
        headers = {**self._construct_access_auth(),
                   **headers} if headers else self._construct_access_auth()
        return super().post(api=api, params=params, data=data, is_json=is_json,
                            files=files, headers=headers, cookies=cookies,
                            auto_retry=auto_retry, retry_times=retry_times,
                            interval=interval, checker=checker, timeout=timeout)

    def get(self, api, params=None, headers=None, cookies=None, login_info=None,
            auto_retry=False, retry_times=5, interval=1, checker=None, timeout=30):
        """make a get request with ce login info

        Args:
            api(HttpApi or str): api string or HttpApi object of the request
            params(dict or list[tuple] or bytes): send in the query string for the request
            headers(dict): headers to send together with self.headers
                (replace duplicate keys of self.headers)
            cookies(dict): cookies to send together with self.cookies
                (replace duplicate keys of self.cookies)
            login_info(dict): if given, will send instead of
                LoginUtil.get_current_employee_info() result
            auto_retry(bool): if allow auto retry
            retry_times(int): retry times, works only when auto_retry=True
            interval(int): wait interval during retry, in seconds, works only when
                auto_retry=True
            checker(function or any): check(code, msg) if request has expected return values,
                default to check code==200, works only when auto_retry=True
            timeout(int or float): request timeout, in second, default 30s

        Returns:
            tuple: (code, msg) -- msg is a dict if response.text is json serializable
        """
        headers = {**self._construct_access_auth(),
                   **headers} if headers else self._construct_access_auth()
        return super().get(api=api, params=params, headers=headers, cookies=cookies,
                           auto_retry=auto_retry, retry_times=retry_times,
                           interval=interval, checker=checker, timeout=timeout)

    def put(self, api, params=None, data=None, is_json=True, files=None,
            headers=None, cookies=None, login_info=None, auto_retry=False,
            retry_times=5, interval=1, checker=None, timeout=30):
        """make a put request with ce login info

        Args:
            api(HttpApi or str): api string or HttpApi object of the request
            params(dict or list[tuple] or bytes): send in the query string for the request
            data(dict): dict to send in the body of the request
            is_json(bool): if the data to send is in json form
            files(dict): dict of files to send, key: filename, value: file object
            headers(dict): headers to send together with self.headers
                (replace duplicate keys of self.headers)
            cookies(dict): cookies to send together with self.cookies
                (replace duplicate keys of self.cookies)
            login_info(dict): if given, will send instead of
                LoginUtil.get_current_employee_info() result
            auto_retry(bool): if allow auto retry
            retry_times(int): retry times, works only when auto_retry=True
            interval(int): wait interval during retry, in seconds, works only when
                auto_retry=True
            checker(function or any): check(code, msg) if request has expected return values,
                default to check code==200, works only when auto_retry=True
            timeout(int or float): request timeout, in second, default 30s

        Returns:
            tuple: (code, msg) -- msg is a dict if response.text is json serializable
        """
        headers = {**self._construct_access_auth(),
                   **headers} if headers else self._construct_access_auth()
        return super().put(api=api, params=params, data=data, is_json=is_json,
                           files=files, headers=headers, cookies=cookies,
                           auto_retry=auto_retry, retry_times=retry_times,
                           interval=interval, checker=checker, timeout=timeout)

    def delete(self, api, params=None, data=None, is_json=True, files=None,
               headers=None, cookies=None, login_info=None, auto_retry=False,
               retry_times=5, interval=1, checker=None, timeout=30):
        """make a delete request with ce login info

        Args:
            api(HttpApi or str): api string or HttpApi object of the request
            params(dict or list[tuple] or bytes): send in the query string for the request
            data(dict): dict to send in the body of the request
            is_json(bool): if the data to send is in json form
            files(dict): dict of files to send, key: filename, value: file object
            headers(dict): headers to send together with self.headers
                (replace duplicate keys of self.headers)
            cookies(dict): cookies to send together with self.cookies
                (replace duplicate keys of self.cookies)
            login_info(dict): if given, will send instead of
                LoginUtil.get_current_employee_info() result
            auto_retry(bool): if allow auto retry
            retry_times(int): retry times, works only when auto_retry=True
            interval(int): wait interval during retry, in seconds, works only when
                auto_retry=True
            checker(function or any): check(code, msg) if request has expected return values,
                default to check code==200, works only when auto_retry=True
            timeout(int or float): request timeout, in second, default 30s

        Returns:
            tuple: (code, msg) -- msg is a dict if response.text is json serializable
        """
        headers = {**self._construct_access_auth(),
                   **headers} if headers else self._construct_access_auth()
        return super().delete(api=api, params=params, data=data, is_json=is_json,
                              files=files, headers=headers, cookies=cookies,
                              retry_times=retry_times, auto_retry=auto_retry,
                              interval=interval, checker=checker, timeout=timeout)

    # ----------------------------------------
    #            protected methods           |
    # ----------------------------------------

    @staticmethod
    def _construct_access_auth():
        """Constructs access auth of request headers for http client."""
        access_token = LoginHandler.get_access_token()
        access_auth = f"Bearer {access_token}"
        headers = {'Authorization': access_auth}
        return headers