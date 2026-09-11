# -*- coding: utf-8 -*-
"""pytest 公共 fixtures（组员A：注册/登录/菜品管理）。"""
import pytest

from config import (BASE_URL, MERCHANT_PHONE, MERCHANT_PWD,
                    NORMAL_USER_PHONE, NORMAL_USER_PWD)
from utils import ApiClient, is_login_success

LOGIN_PATH = "/api/user/login"


@pytest.fixture(scope="session")
def api():
    """被测后端客户端。"""
    return ApiClient(BASE_URL)


def _login_get_token(api, phone, password):
    resp = api.post(LOGIN_PATH, json_data={"userortel": phone, "password": password})
    assert is_login_success(resp), f"登录失败: {resp.status_code} {resp.text}"
    token = resp.json().get("token")
    assert token, f"响应中无 token: {resp.text}"
    return token


@pytest.fixture(scope="session")
def merchant_token(api):
    """商家账号 token（菜品管理）。"""
    return _login_get_token(api, MERCHANT_PHONE, MERCHANT_PWD)


@pytest.fixture(scope="session")
def normal_user_token(api):
    """普通用户 token（用于权限拒绝用例）。"""
    return _login_get_token(api, NORMAL_USER_PHONE, NORMAL_USER_PWD)
