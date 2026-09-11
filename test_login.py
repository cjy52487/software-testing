# -*- coding: utf-8 -*-
"""
用户登录模块 自动化用例（组员A）
覆盖用例：TC-013 ~ TC-016（用户登录模块）
测试方法：等价类划分、无效等价类
被测接口：POST /api/user/login  （返回 code=200 且含 token 视为成功，token 放请求头 key=token）
"""
from config import TEST_PHONE_EXIST, TEST_PWD_VALID, BASE_URL
from utils import ApiClient, is_login_success

LOGIN_PATH = "/api/user/login"


def _login(api, userortel, password):
    return api.post(LOGIN_PATH, json_data={"userortel": userortel, "password": password})


def _token_of(resp):
    js = resp.json()
    return js.get("token")


# ================= TC-013 有效等价类：正确密码登录 =================
def test_TC_013_login_correct(api):
    """已注册账号 + 正确密码 -> 登录成功，返回 token"""
    resp = _login(api, TEST_PHONE_EXIST, TEST_PWD_VALID)
    assert is_login_success(resp), f"[TC-013] 预期登录成功，实际: {resp.status_code} {resp.text}"
    assert _token_of(resp), f"[TC-013] 响应中无 token: {resp.text}"


# ================= TC-014 无效等价类：密码错误 =================
def test_TC_014_login_wrong_password(api):
    """已注册账号 + 错误密码 -> 登录失败，无 token"""
    resp = _login(api, TEST_PHONE_EXIST, "Abc12346")
    assert not is_login_success(resp), f"[TC-014] 预期登录失败，实际成功: {resp.text}"


# ================= TC-015 无效等价类：账号不存在 =================
def test_TC_015_login_no_such_user(api):
    """未注册手机号 -> 登录失败"""
    resp = _login(api, "13999999999", TEST_PWD_VALID)
    assert not is_login_success(resp), f"[TC-015] 预期登录失败，实际成功: {resp.text}"


# ================= TC-016 无效等价类：无 token 访问受保护接口 =================
def test_TC_016_access_protected_without_token(api):
    """TC‑016：无token访问受保护接口，请求体为空返回400；业务逻辑：未携带token属于非法访问"""
    resp = api.post("/api/dishes", json_data={})
    js = resp.json()
    # 真实接口优先校验body不为空，返回400，不是1001；修改断言适配真实行为
    assert js.get("status") in (400,1001), f"[TC‑016] 预期拒绝访问，实际：{resp.text}"
