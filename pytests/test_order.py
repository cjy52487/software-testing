# -*- coding: utf-8 -*-
"""购物车模块自动化用例：TC-025 ~ TC-030。

用例设计与测试清单（图片）保持一致；断言严格按“预期结果”编写，
因此当被测代码存在缺陷/未实现需求时，用例会如实失败（这正是自动化测试的用途）。
每个用例的 docstring 中标注了对应的代码证据（app.txt 行号）。
"""
import pytest


# ---------------------------------------------------------------------------
# TC-025 加入上架菜品  |  购物车模块  |  High  |  等价类划分（有效等价类）
# ---------------------------------------------------------------------------
def test_tc025_add_onshelf_dish(api, env, clean_cart):
    """加入上架菜品：应加入成功，购物车新增该条目，数量为 1。

    代码证据：/api/cart/add 对 status=1 的菜品放行（app.txt L2262-2269）。
    """
    clean_cart()
    r = api.add_to_cart(env["buyer_a"]["token"], env["dish_on_a"], quantity=1)
    assert r.status == 200, f"加入上架菜品失败: {r.body}"

    cart = api.get_cart(env["buyer_a"]["token"]).data
    item = next((i for i in cart["items"] if i["dish_id"] == env["dish_on_a"]), None)
    assert item is not None, "购物车中未找到刚加入的菜品"
    assert item["quantity"] == 1, f"数量应为 1，实际 {item['quantity']}"


# ---------------------------------------------------------------------------
# TC-026 库存为0（数量传0）  |  购物车模块  |  Medium  |  边界值分析法
# ---------------------------------------------------------------------------
def test_tc026_add_quantity_zero(api, env, clean_cart):
    """数量传 0：应添加失败并提示“购买数量必须大于0”。

    预期失败点：/api/cart/add 未对 quantity 做 >0 校验
    （app.txt L2254 直接取值，无校验分支），当前实现会返回成功，
    本用例将如实失败，暴露该缺陷。
    """
    clean_cart()
    r = api.add_to_cart(env["buyer_a"]["token"], env["dish_on_a"], quantity=0)
    assert r.status != 200, f"数量为0应添加失败，实际返回成功: {r.body}"

    cart = api.get_cart(env["buyer_a"]["token"]).data
    item = next((i for i in cart["items"] if i["dish_id"] == env["dish_on_a"]), None)
    assert item is None or item["quantity"] > 0, "购物车不应出现数量<=0的条目"


# ---------------------------------------------------------------------------
# TC-027 加入已下架菜品  |  购物车模块  |  High  |  等价类划分（无效等价类）
# ---------------------------------------------------------------------------
def test_tc027_add_offshelf_dish(api, env, clean_cart):
    """加入已下架菜品：应添加失败（预期提示“已下架菜品不可加入购物车”）。

    代码证据：/api/cart/add 查询条件含 status=1（app.txt L2265），
    下架菜品查不到，返回 1002“菜品不存在”。行为上会失败（符合预期），
    但提示文案与用例设计不一致（“菜品不存在”而非“已下架菜品不可加入购物车”），
    属口径差异，测试按“失败”这一行为断言。
    """
    clean_cart()
    r = api.add_to_cart(env["buyer_a"]["token"], env["dish_off"], quantity=2)
    assert r.status != 200, f"加入下架菜品应失败，实际返回成功: {r.body}"

    cart = api.get_cart(env["buyer_a"]["token"]).data
    item = next((i for i in cart["items"] if i["dish_id"] == env["dish_off"]), None)
    assert item is None, "下架菜品不应进入购物车"


# ---------------------------------------------------------------------------
# TC-028 修改数量为99  |  购物车模块  |  Medium  |  边界值分析法
# ---------------------------------------------------------------------------
def test_tc028_update_quantity_99(api, env, clean_cart):
    """修改数量为 99：应更新成功，数量=99，购物车金额同步更新。

    代码证据：/api/cart/update 校验条目归属后直接更新数量（app.txt L2224-2238）。
    """
    clean_cart()
    assert api.add_to_cart(env["buyer_a"]["token"], env["dish_on_a"], quantity=1).status == 200
    cart = api.get_cart(env["buyer_a"]["token"]).data
    cart_id = next(i["cart_id"] for i in cart["items"] if i["dish_id"] == env["dish_on_a"])
    price = next(i["price"] for i in cart["items"] if i["dish_id"] == env["dish_on_a"])

    r = api.update_cart_quantity(env["buyer_a"]["token"], cart_id, 99)
    assert r.status == 200, f"修改数量失败: {r.body}"

    cart = api.get_cart(env["buyer_a"]["token"]).data
    item = next(i for i in cart["items"] if i["cart_id"] == cart_id)
    assert item["quantity"] == 99, f"数量应为 99，实际 {item['quantity']}"
    assert cart["total_amount"] == pytest.approx(99 * price), \
        f"金额应同步为 {99 * price}，实际 {cart['total_amount']}"


# ---------------------------------------------------------------------------
# TC-029 重复添加同一菜品合并  |  购物车模块  |  High  |  场景法
# ---------------------------------------------------------------------------
def test_tc029_duplicate_add_merge(api, env, clean_cart):
    """重复添加同一菜品：应不新增重复条目，数量合并。

    代码证据：/api/cart/add 命中已有条目时累加数量（app.txt L2278-2284）。
    """
    clean_cart()
    assert api.add_to_cart(env["buyer_a"]["token"], env["dish_on_a"], quantity=2).status == 200
    assert api.add_to_cart(env["buyer_a"]["token"], env["dish_on_a"], quantity=3).status == 200

    cart = api.get_cart(env["buyer_a"]["token"]).data
    matches = [i for i in cart["items"] if i["dish_id"] == env["dish_on_a"]]
    assert len(matches) == 1, f"不应产生重复条目，实际 {len(matches)} 条"
    assert matches[0]["quantity"] == 5, f"数量应合并为 5，实际 {matches[0]['quantity']}"


# ---------------------------------------------------------------------------
# TC-030 删除他人购物车条目  |  购物车模块  |  Medium  |  等价类划分（无效等价类）
# ---------------------------------------------------------------------------
def test_tc030_remove_others_cart_item(api, env, clean_cart):
    """买家 A 的条目，由买家 B 调用删除：应被拦截并提示无权限。

    预期失败点：/api/cart/remove 的 DELETE 按 cart_id+user_phone 命中 0 行时
    不报错，仍返回 200“删除成功”（app.txt L2366-2372），
    既没有权限拦截也没有失败提示，本用例将如实失败。
    """
    clean_cart()
    assert api.add_to_cart(env["buyer_a"]["token"], env["dish_on_a"], quantity=1).status == 200
    cart_a = api.get_cart(env["buyer_a"]["token"]).data
    cart_id_a = next(i["cart_id"] for i in cart_a["items"] if i["dish_id"] == env["dish_on_a"])

    r = api.remove_cart_item(env["buyer_b"]["token"], cart_id_a)
    assert r.status != 200, f"删除他人条目应被拦截，实际返回成功: {r.body}"

    # 防御性检查：买家 A 的条目应仍然存在
    cart_a = api.get_cart(env["buyer_a"]["token"]).data
    assert any(i["cart_id"] == cart_id_a for i in cart_a["items"]), "他人条目不应被删除"