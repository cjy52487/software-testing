# -*- coding: utf-8 -*-
"""
商家菜品管理模块 自动化用例（组员A）
覆盖用例：TC-017 ~ TC-024（菜品管理模块）
测试方法：等价类划分、边界值分析法
被测接口（商家端，@store_owner_required，token 放请求头 key=token）：
  POST   /api/dishes              添加菜品（json）
  PUT    /api/dishes/<dish_id>    更新菜品
  DELETE /api/dishes/<dish_id>    删除菜品
返回 status=200 视为成功。
"""
import pytest

from config import MERCHANT_SHOP_ID
from utils import gen_random_phone, is_api_success

ADD_PATH = "/api/dishes"


def _make_payload(name, price, status=1, description=""):
    return {
        "shop_id": MERCHANT_SHOP_ID,
        "dish_name": name,
        "price": price,
        "description": description,
        "sort_order": 0,
        "status": status,
    }


def _add_dish(api, payload):
    return api.post(ADD_PATH, json_data=payload)


def _dish_id_of(resp):
    js = resp.json()
    data = js.get("data") or {}
    return data.get("dish_id")


# ============ TC-017 有效等价类：新增上架菜品 ============
def test_TC_017_add_dish_normal(api, merchant_token):
    """商家合法参数新增上架菜品 -> 成功"""
    api.set_token(merchant_token)
    resp = _add_dish(api, _make_payload(f"可乐{gen_random_phone()}", 12, status=1))
    assert is_api_success(resp), f"[TC-017] 预期新增成功，实际: {resp.status_code} {resp.text}"


# ============ TC-018 边界值：价格0 + 下架 ============
def test_TC_018_add_dish_zero_price_off(api, merchant_token):
    """价格0、status=0 下架菜品 -> 允许保存"""
    api.set_token(merchant_token)
    resp = _add_dish(api, _make_payload(f"赠品{gen_random_phone()}", 0, status=0))
    assert is_api_success(resp), f"[TC-018] 预期新增成功(边界值)，实际: {resp.status_code} {resp.text}"


# ============ TC-019 无效等价类：价格为负数 ============
def test_TC_019_add_dish_negative_price(api, merchant_token):
    """价格 -5 -> 新增失败（真实后端未做价格非负校验则FAILED，记为缺陷）"""
    api.set_token(merchant_token)
    resp = _add_dish(api, _make_payload(f"负价菜{gen_random_phone()}", -5))
    assert not is_api_success(resp), f"[TC-019] 预期新增失败(负价格)，实际成功: {resp.text}"


# ============ TC-020 无效等价类：普通用户新增菜品 ============
#def test_TC_020_normal_user_add_dish(api, normal_user_token):
#    """普通用户调用新增菜品 -> 无权限"""
#    api.set_token(normal_user_token)
#    resp = _add_dish(api, _make_payload("普通用户添加", 10))
#    assert not is_api_success(resp), f"[TC-020] 预期无权限，实际: {resp.status_code} {resp.text}"


# ============ TC-021 有效等价类：编辑本店菜品 ============
def test_TC_021_edit_own_dish(api, merchant_token):
    """先新增本店菜品，再 PUT 修改 -> 成功"""
    api.set_token(merchant_token)
    add_resp = _add_dish(api, _make_payload(f"待编辑{gen_random_phone()}", 10))
    assert is_api_success(add_resp), f"[TC-021] 前置新增失败: {add_resp.text}"
    dish_id = _dish_id_of(add_resp)
    assert dish_id, f"[TC-021] 新增响应无 dish_id: {add_resp.text}"

    edit_payload = {
        "dish_name": f"已改{gen_random_phone()}",
        "price": 20,
        "description": "修改后",
        "sort_order": 0,
        "status": 1,
    }
    resp = api.put(f"/api/dishes/{dish_id}", json_data=edit_payload)
    assert is_api_success(resp), f"[TC-021] 预期编辑成功，实际: {resp.status_code} {resp.text}"


# ============ TC-022 无效等价类：编辑他店菜品 ============
def test_TC_022_edit_other_merchant_dish(api, merchant_token):
    """编辑不属于自己店铺的 dish_id（9999 模拟他人菜品）-> 无权限"""
    api.set_token(merchant_token)
    edit_payload = {
        "dish_name": "篡改别人菜品",
        "price": 99,
        "description": "",
        "sort_order": 0,
        "status": 1,
    }
    resp = api.put("/api/dishes/9999", json_data=edit_payload)
    assert not is_api_success(resp), f"[TC-022] 预期无权限，实际成功: {resp.text}"


# ============ TC-023 有效等价类：删除本店菜品 ============
def test_TC_023_delete_own_dish(api, merchant_token):
    """先新增本店菜品，再 DELETE -> 成功"""
    api.set_token(merchant_token)
    add_resp = _add_dish(api, _make_payload(f"待删除{gen_random_phone()}", 8))
    assert is_api_success(add_resp), f"[TC-023] 前置新增失败: {add_resp.text}"
    dish_id = _dish_id_of(add_resp)
    assert dish_id, f"[TC-023] 新增响应无 dish_id: {add_resp.text}"

    resp = api.delete(f"/api/dishes/{dish_id}")
    assert is_api_success(resp), f"[TC-023] 预期删除成功，实际: {resp.status_code} {resp.text}"


# ============ TC-024 无效等价类：普通用户删除菜品 ============
#def test_TC_024_normal_user_delete_dish(api, normal_user_token):
#    """普通用户尝试删除菜品 -> 无权限"""
#    api.set_token(normal_user_token)
#    resp = api.delete("/api/dishes/9999")
#    assert not is_api_success(resp), f"[TC-024] 预期无权限，实际成功: {resp.text}"
