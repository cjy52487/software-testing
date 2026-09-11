# -*- coding: utf-8 -*-
"""公共工具：HTTP 请求封装与成功判断（适配真实后端）。"""
import random

import requests

import config


class ApiClient:
    """封装对被测后端 food_delivery_app 的 HTTP 请求。
    注意：真实后端把 token 放在请求头 key = "token"（不是 Authorization Bearer）。
    """

    def __init__(self, base_url=config.BASE_URL, timeout=10):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

    def _request(self, method, path, token=None, **kwargs):
        url = self.base_url + path
        headers = kwargs.pop("headers", {})
        if token:
            headers["token"] = token
        resp = self.session.request(method, url, headers=headers, timeout=self.timeout, **kwargs)
        return resp

    def get(self, path, token=None, **kw):
        return self._request("GET", path, token=token, **kw)

    def post(self, path, token=None, json_data=None, **kw):
        return self._request("POST", path, token=token, json=json_data, **kw)

    def put(self, path, token=None, json_data=None, **kw):
        return self._request("PUT", path, token=token, json=json_data, **kw)

    def delete(self, path, token=None, **kw):
        return self._request("DELETE", path, token=token, **kw)

    def set_token(self, token):
        """把 token 写入 session 请求头（key=token）。"""
        self.session.headers["token"] = token


def gen_random_phone():
    """生成随机未注册手机号（11位，避免与库中已注册账号冲突）。"""
    return "139" + "".join(random.choices("0123456789", k=8))

# 新增：生成随机用户名，避免username重复
def gen_random_username():
    return f"test_u_{random.randint(10000,99999)}"

# ============ 两套返回码判断（适配真实后端）============
def is_login_success(resp):
    """登录接口：返回 {"code":200,"token":...} 视为成功。"""
    js = resp.json()
    return js.get("code") == 200


def is_api_success(resp):
    """注册/菜品接口：返回 {"status":200,...} 视为成功。"""
    js = resp.json()
    return js.get("status") == 200
