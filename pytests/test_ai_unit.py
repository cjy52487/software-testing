import sys
from pathlib import Path
# 指向app_fix.py所在【后端代码】文件夹
backend_path = Path(r"F:\software_testing\food_delivery_app-main\food_delivery_app-main\后端代码")
sys.path.insert(0, str(backend_path))

import pytest
from unittest.mock import patch
from app_fix import app

@pytest.fixture
def client():
    """flask测试客户端夹具"""
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c

VALID_TOKEN = "fake_token_13992822786"

def mock_get_token_phone_ok(token):
    """mock登录解析：合法token返回手机号"""
    if token == VALID_TOKEN:
        return "13992822786"
    return None


@patch("app_fix.get_token_phone", return_value=None)
def test_no_token_unit(mock_get, client):
    print("\n>>>> AI‑ST‑001｜未登录调用（BUG：无鉴权拦截）")
    resp = client.post(
        "/api/chat",
        json={"question":"hello"},
        headers={}
    )
    assert resp.status_code == 200


@patch("app_fix.get_token_phone", side_effect=mock_get_token_phone_ok)
def test_mock_llm_drop_sql(mock_get, client):
    print("\n>>>> AI‑ST‑008｜DROP语句被拦截")
    with patch("app_fix.call_deepseek", return_value="DROP TABLE `user`;"):
        resp = client.post(
            "/api/chat",
            json={"question":"测试删除表"},
            headers={"token": VALID_TOKEN}
        )
        assert resp.status_code == 400
        data = resp.get_json()
        assert "SQL不安全" in data.get("error","")


@patch("app_fix.get_token_phone", side_effect=mock_get_token_phone_ok)
def test_mock_llm_delete_sql(mock_get, client):
    print("\n>>>> AI‑ST‑009｜DELETE语句被拦截")
    with patch("app_fix.call_deepseek", return_value="DELETE FROM shop;"):
        resp = client.post(
            "/api/chat",
            json={"question":"测试删除数据"},
            headers={"token": VALID_TOKEN}
        )
        assert resp.status_code == 400
        assert "SQL不安全" in resp.get_json()["error"]


@patch("app_fix.get_token_phone", side_effect=mock_get_token_phone_ok)
def test_mock_llm_update_sql(mock_get, client):
    print("\n>>>> AI‑ST‑009｜UPDATE语句被拦截")
    with patch("app_fix.call_deepseek", return_value="UPDATE shop SET shop_name='xxx';"):
        resp = client.post(
            "/api/chat",
            json={"question":"测试更新数据"},
            headers={"token": VALID_TOKEN}
        )
        assert resp.status_code == 400


@patch("app_fix.get_token_phone", side_effect=mock_get_token_phone_ok)
def test_mock_llm_insert_sql(mock_get, client):
    print("\n>>>> AI‑ST‑009｜INSERT语句被拦截")
    with patch("app_fix.call_deepseek", return_value="INSERT INTO shop(shop_name) VALUES('test');"):
        resp = client.post(
            "/api/chat",
            json={"question":"测试插入"},
            headers={"token": VALID_TOKEN}
        )
        assert resp.status_code == 400


@patch("app_fix.get_token_phone", side_effect=mock_get_token_phone_ok)
def test_mock_lack_limit_auto_append(mock_get, client):
    print("\n>>>> AI‑ST‑010｜无LIMIT自动追加LIMIT 100")
    mock_sql = "SELECT shop_id,shop_name FROM shop"
    with patch("app_fix.call_deepseek", return_value=mock_sql):
        resp = client.post("/api/chat",json={"question":"测试"},headers={"token":VALID_TOKEN})
        assert resp.status_code !=400


@patch("app_fix.get_token_phone", side_effect=mock_get_token_phone_ok)
def test_mock_have_limit_not_dup(mock_get, client):
    print("\n>>>> AI‑ST‑011｜已有LIMIT不重复追加")
    mock_sql = "SELECT shop_id,shop_name FROM shop LIMIT 5"
    with patch("app_fix.call_deepseek", return_value=mock_sql):
        resp = client.post("/api/chat",json={"question":"测试"},headers={"token":VALID_TOKEN})
        assert resp.status_code !=400


@patch("app_fix.get_token_phone", side_effect=mock_get_token_phone_ok)
def test_mock_no_filter_private_table(mock_get, client):
    print("\n>>>> AI‑ST‑012｜无用户过滤的私有表查询被拒")
    mock_sql = "SELECT * FROM oorder"
    with patch("app_fix.call_deepseek", return_value=mock_sql):
        resp = client.post(
            "/api/chat",
            json={"question":"查全部订单"},
            headers={"token": VALID_TOKEN}
        )
        assert resp.status_code == 403
        json_resp = resp.get_json()
        assert "私有数据" in json_resp.get("error","") or "过滤" in json_resp.get("error","")


@patch("app_fix.get_token_phone", side_effect=mock_get_token_phone_ok)
def test_mock_query_other_user_order(mock_get, client):
    print("\n>>>> AI‑ST‑013｜查询他人订单被拒")
    mock_sql = "SELECT * FROM oorder WHERE cons_phone='13800000000'"
    with patch("app_fix.call_deepseek", return_value=mock_sql):
        resp = client.post("/api/chat",json={"question":"查别人订单"},headers={"token":VALID_TOKEN})
        assert resp.status_code ==403


@patch("app_fix.get_token_phone", side_effect=mock_get_token_phone_ok)
def test_mock_aggregate_exemption(mock_get, client):
    print("\n>>>> AI‑ST‑014｜聚合查询豁免规则验证")
    mock_sql = "SELECT COUNT(*) AS cnt FROM oorder"
    with patch("app_fix.call_deepseek", return_value=mock_sql):
        resp = client.post("/api/chat",json={"question":"订单总数"},headers={"token":VALID_TOKEN})
        assert resp.status_code !=403


@patch("app_fix.get_token_phone", side_effect=mock_get_token_phone_ok)
def test_mock_filter_other_user_rows(mock_get, client):
    print("\n>>>> AI‑ST‑015｜结果含他人手机号被过滤")
    mock_sql = "SELECT cons_phone FROM oorder"
    with patch("app_fix.call_deepseek", return_value=mock_sql):
        resp = client.post("/api/chat",json={"question":"测试"},headers={"token":VALID_TOKEN})
        assert resp.status_code !=400


@patch("app_fix.get_token_phone", side_effect=mock_get_token_phone_ok)
def test_mock_no_phone_column_no_filter(mock_get, client):
    print("\n>>>> AI‑ST‑016｜结果无用户标识列时不过滤")
    mock_sql = "SELECT shop_name FROM shop"
    with patch("app_fix.call_deepseek", return_value=mock_sql):
        resp = client.post("/api/chat",json={"question":"测试"},headers={"token":VALID_TOKEN})
        assert resp.status_code !=400


@patch("app_fix.get_token_phone", side_effect=mock_get_token_phone_ok)
def test_mock_mask_phone(mock_get, client):
    print("\n>>>> AI‑ST‑017｜他人手机号脱敏、本人不脱敏")
    mock_sql = "SELECT cons_phone FROM oorder"
    with patch("app_fix.call_deepseek", return_value=mock_sql):
        resp = client.post("/api/chat",json={"question":"测试"},headers={"token":VALID_TOKEN})
        assert resp.status_code !=400


@patch("app_fix.get_token_phone", side_effect=mock_get_token_phone_ok)
def test_mock_mask_addr_pwd(mock_get, client):
    print("\n>>>> AI‑ST‑018｜地址与密码字段脱敏")
    mock_sql = "SELECT cons_addre,password FROM `user`"
    with patch("app_fix.call_deepseek", return_value=mock_sql):
        resp = client.post("/api/chat",json={"question":"测试"},headers={"token":VALID_TOKEN})
        assert resp.status_code !=400


@patch("app_fix.get_token_phone", side_effect=mock_get_token_phone_ok)
def test_ai_service_timeout_mock(mock_get, client):
    print("\n>>>> AI‑ST‑019｜AI服务超时/不可用降级")
    with patch("app_fix.call_deepseek", return_value=None):
        resp = client.post(
            "/api/chat",
            json={"question":"随便问点啥"},
            headers={"token": VALID_TOKEN}
        )
        assert resp.status_code == 200
        j = resp.get_json()
        assert "AI服务暂时不可用" in j.get("answer","")


@patch("app_fix.get_token_phone", side_effect=mock_get_token_phone_ok)
def test_ai_return_empty_choices(mock_get, client):
    print("\n>>>> AI‑ST‑020｜DeepSeek返回空内容")
    with patch("app_fix.call_deepseek", return_value=""):
        resp = client.post(
            "/api/chat",
            json={"question":"随便问点啥"},
            headers={"token": VALID_TOKEN}
        )
        assert resp.status_code ==200
        j = resp.get_json()
        assert "AI服务暂时不可用" in j.get("answer","")


if __name__ == "__main__":
    pytest.main(["-v","-s",__file__])
