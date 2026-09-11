# -*- coding: utf-8 -*-
"""
用户注册模块 自动化用例（组员A）
覆盖用例：TC-001 ~ TC-012（用户注册模块）
测试方法：等价类划分、边界值分析法
被测接口：POST /api/user/register/test  （返回 status=200 视为成功）
"""
import pytest
from config import TEST_PWD_VALID, TEST_PHONE_EXIST
from utils import gen_random_phone, gen_random_username, is_api_success

REGISTER_PATH = "/api/user/register/test"

def _register(api, telephone, password):
    # 每次调用自动生成随机username，避免用户名重复冲突
    return api.post(REGISTER_PATH, json_data={
        "username": gen_random_username(),
        "password": password,
        "telephone": telephone,
        "role": 0,
    })

# ================= TC-001 有效等价类：正常注册 =================
def test_TC_001_register_normal(api):
    """TC-001：合法手机号 + 合法密码 -> 注册成功"""
    phone = gen_random_phone()
    resp = _register(api, phone, TEST_PWD_VALID)
    assert is_api_success(resp), f"[TC-001] 预期注册成功，实际: {resp.status_code} {resp.text}"

# ================= TC-002 / TC-003 边界值：手机号位数 =================
@pytest.mark.parametrize("case_id,phone", [
    ("TC-002", "1381234567"),     # 10位
    ("TC-003", "138123456789"),   # 12位
])
def test_TC_002_003_phone_length_boundary(api, case_id, phone):
    """手机号非11位 -> 注册失败"""
    resp = _register(api, phone, TEST_PWD_VALID)
    assert not is_api_success(resp), f"[{case_id}] 预期注册失败，实际成功: {resp.text}"

# ================= TC-004 无效等价类：手机号已注册 =================
def test_TC_004_phone_exists(api):
    """已注册手机号 -> 注册失败"""
    resp = _register(api, TEST_PHONE_EXIST, TEST_PWD_VALID)
    assert not is_api_success(resp), f"[TC-004] 预期失败(手机号已注册)，实际成功: {resp.text}"

# ================= TC-005 无效等价类：密码长度不足 =================
def test_TC_005_pwd_too_short(api):
    """密码5位(<6) -> 应注册失败（真实后端无该校验，将FAILED记为缺陷）"""
    resp = _register(api, gen_random_phone(), "Abc12")
    assert not is_api_success(resp), f"[TC-005] 预期失败(密码不足6位)，实际成功: {resp.text}"

# ============ TC-006~008 密码缺字符类型（真实后端无校验，记为缺陷）============
@pytest.mark.parametrize("case_id,password", [
    ("TC-006", "abc12345"),    # 缺大写字母
    ("TC-007", "ABC12345"),    # 缺小写字母
    ("TC-008", "Abcdefgh"),    # 缺数字
])
def test_TC_006_007_008_pwd_missing_char(api, case_id, password):
    """密码缺少大写/小写/数字 -> 应注册失败"""
    resp = _register(api, gen_random_phone(), password)
    assert not is_api_success(resp), f"[{case_id}] 预期失败(密码缺字符类型)，实际成功: {resp.text}"

# ============ TC-009~011 边界值：密码长度上下界 ============
@pytest.mark.parametrize("case_id,password,should_ok", [
    ("TC-009", "Abc123", True),             # 6位，下界合法
    ("TC-010", "Abcdefgh1234", True),       # 12位，上界合法
    ("TC-011", "Abcdefgh12345", False),     # 13位，超上界
])
def test_TC_009_010_011_pwd_len_boundary(api, case_id, password, should_ok):
    """密码长度边界（6/12/13位）"""
    resp = _register(api, gen_random_phone(), password)
    if should_ok:
        assert is_api_success(resp), f"[{case_id}] 预期注册成功，实际失败: {resp.text}"
    else:
        assert not is_api_success(resp), f"[{case_id}] 预期注册失败(超长)，实际成功: {resp.text}"

# ================= TC-012 无效等价类：手机号为空 =================
def test_TC_012_phone_empty(api):
    """手机号为空 -> 注册失败"""
    resp = _register(api, "", TEST_PWD_VALID)
    assert not is_api_success(resp), f"[TC-012] 预期失败(手机号为空)，实际成功: {resp.text}"
