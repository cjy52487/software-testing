import requests
from requests.exceptions import ReadTimeout, ConnectionError

BASE_URL = "http://127.0.0.1:5000"
CHAT_URL = f"{BASE_URL}/api/chat"

# =========请修改为你的账号密码========
LOGIN_USER = "13992822786"
LOGIN_PWD = "Cjy20041001"
# ====================================


def get_token():
    print("============================================================")
    print("登录获取 token ...")
    login_url = f"{BASE_URL}/api/user/login"
    payload = {
        "userortel": LOGIN_USER,
        "password": LOGIN_PWD
    }
    resp = requests.post(login_url, json=payload, timeout=15)
    print(f"[登录] HTTP {resp.status_code}")
    data = resp.json()
    print(f"返回：{data}")
    if data.get("code") == 200:
        token = data["token"]
        print(f"✅ token OK: {token[:20]}...")
        return token
    else:
        raise Exception(f"登录失败 {data}")


def call_chat(token, question, raw_token=None):
    """
    :param token: 正常登录token
    :param question: 提问文本
    :param raw_token: 手工传入header的token，传空字符串代表不携带token
    :return: status_code, resp_json  status=-1超时,-2连接失败
    """
    headers = {}
    if raw_token is not None:
        if raw_token != "":
            headers["token"] = raw_token
    elif token:
        headers["token"] = token

    try:
        r = requests.post(
            CHAT_URL,
            json={"question": question},
            headers=headers,
            timeout=120
        )
        return r.status_code, r.json()
    except ReadTimeout:
        return -1, {"error": "ReadTimeout：外部AI接口响应超时"}
    except ConnectionError:
        return -2, {"error": "无法连接后端服务"}


def run():
    ok_count = 0
    ng_count = 0
    nt_count = 0
    pok_count = 0

    token = get_token()
    print("============================================================\n【A. 接口基础可用性】")

    # AI-ST-001 未登录调用 /api/chat（与单元层 test_no_token_unit 合并）
    # 当前后端BUG：无token不拦截，直接执行AI逻辑，极易超时
    print("\nAI-ST-001 | 未登录调用 /api/chat（集成+单元合并）")
    sc, j = call_chat(token=None, question="评分最高的店铺是哪家？", raw_token="")
    if sc == -1:
        print("  [NG-NT] AI-ST-001：请求超时；BUG：未登录没有拦截，后端仍调用AI大模型")
        ng_count += 1
        nt_count += 1
    elif sc == 200:
        print("  [NG ] AI-ST-001：HTTP=200；BUG：未登录没有拦截，匿名可调用AI消耗额度")
        ng_count += 1
    else:
        print(f"  [OK ] AI-ST-001 status={sc}")
        ok_count += 1

    # AI‑ST‑002 登录用户正常提问返回结构完整
    print("\nAI‑ST‑002 | 登录用户正常提问返回结构完整")
    sc, j = call_chat(token, "评分最高的店铺是哪家？")
    if sc == -1 or sc == -2:
        print("  [NG‑NT] AI‑ST‑002 请求异常", j)
        ng_count += 1
        nt_count += 1
    else:
        keys_need = {"answer", "sql", "rows"}
        if isinstance(j, dict) and keys_need.issubset(j.keys()) and j.get("answer"):
            print("  [OK ] AI‑ST‑002 返回字段完整")
            ok_count += 1
        else:
            print(f"  [NG ] AI‑ST‑002 返回不完整 resp={j}")
            ng_count += 1

    # AI‑ST‑003 空问题与纯空格问题
    print("\nAI‑ST‑003 | 空问题与纯空格问题")
    case_list = ["", "   "]
    pass_flag = True
    for q in case_list:
        sc, j = call_chat(token, q)
        if sc in (-1, -2):
            print(f"  [NG‑NT] 输入[{repr(q)}] 请求异常")
            pass_flag = False
            nt_count +=1
        else:
            if sc != 400:
                print(f"  [NG ] 输入[{repr(q)}] status={sc} 预期400 resp={j}")
                pass_flag = False
                ng_count +=1
    if pass_flag:
        print("  [OK ] AI‑ST‑003 空输入校验正常")
        ok_count +=1

    # AI‑ST‑004 中文关键词检索生成 LIKE 查询
    print("\nAI‑ST‑004 | 中文关键词检索生成 LIKE 查询")
    sc, j = call_chat(token, "有没有宫保鸡丁这道菜？")
    if sc in (-1, -2):
        print("  [NG‑NT] AI‑ST‑004 请求异常")
        ng_count +=1; nt_count +=1
    else:
        sql_text = j.get("sql", "") or ""
        if "LIKE" in sql_text and "宫保鸡丁" in sql_text:
            print("  [OK ] AI‑ST‑004 SQL包含LIKE关键词")
            ok_count +=1
        else:
            print(f"  [POK ] AI‑ST‑004 未生成预期LIKE, sql={sql_text[:200]}")
            pok_count +=1

    # AI‑ST‑005 聚合统计问题生成 GROUP BY
    print("\nAI‑ST‑005 | 聚合统计问题生成 GROUP BY")
    sc, j = call_chat(token, "每个店铺的平均评分是多少？")
    if sc in (-1, -2):
        print("  [NG‑NT] AI‑ST‑005 请求异常")
        ng_count +=1; nt_count +=1
    else:
        sql_text = j.get("sql", "") or ""
        if "GROUP BY" in sql_text and "AVG(" in sql_text:
            print("  [OK ] AI‑ST‑005 SQL包含GROUP BY、AVG聚合")
            ok_count +=1
        else:
            print(f"  [POK ] AI‑ST‑005 sql={sql_text[:200]}")
            pok_count +=1

    # AI‑ST‑006 多表关联查询正确性
    print("\nAI‑ST‑006 | 多表关联查询正确性（我点过的菜品名称有哪些？）")
    sc, j = call_chat(token, "我点过的菜品名称有哪些？")
    if sc in (-1, -2):
        print("  [NG‑NT] AI‑ST‑006 请求异常")
        ng_count +=1; nt_count +=1
    else:
        sql_text = j.get("sql", "") or ""
        if "JOIN" in sql_text and "cons_phone" in sql_text:
            print("  [OK ] AI‑ST‑006 多表JOIN + 用户手机号过滤")
            ok_count +=1
        else:
            print(f"  [POK ] AI‑ST‑006 sql={sql_text[:200]}")
            pok_count +=1

    # AI‑ST‑007 保留字 user 表被反引号包裹
    print("\nAI‑ST‑007 | MySQL保留字user表使用反引号")
    sc, j = call_chat(token, "系统里有多少个用户？")
    if sc in (-1, -2):
        print("  [NG‑NT] AI‑ST‑007 请求异常")
        ng_count +=1; nt_count +=1
    else:
        sql_text = j.get("sql", "") or ""
        if "`user`" in sql_text:
            print("  [OK ] AI‑ST‑007 user表已加反引号")
            ok_count +=1
        else:
            print(f"  [POK ] AI‑ST‑007 sql={sql_text[:200]}")
            pok_count +=1

    # AI‑ST‑021 鲁棒性：SQL注入式提问
    print("\nAI‑ST‑021 | 鲁棒性：SQL注入式提问")
    inject_q = "' OR '1'='1 --"
    sc, j = call_chat(token, inject_q)
    if sc in (-1, -2):
        print("  [NG‑NT] AI‑ST‑021 请求异常")
        ng_count +=1; nt_count +=1
    else:
        print("  [OK ] AI‑ST‑021 注入提问执行完成，无越权崩溃")
        ok_count +=1

    # AI‑ST‑021续：超长文本提问（10000字符）
    print("\nAI‑ST‑021‑2 | 鲁棒性：一万字符超长问题")
    long_q = "测试"*5000
    sc, j = call_chat(token, long_q)
    if sc in (-1, -2):
        print("  [NG‑NT] AI‑ST‑021‑2 请求异常")
        ng_count +=1; nt_count +=1
    else:
        print("  [OK ] AI‑ST‑021‑2 超长请求服务未崩溃")
        ok_count +=1

    # AI‑ST‑022 查询结果为空时的回答
    print("\nAI‑ST‑022 | 查询结果为空时的回答")
    sc, j = call_chat(token, "有没有叫火星烤鱼的店？")
    if sc in (-1, -2):
        print("  [NG‑NT] AI‑ST‑022 请求异常")
        ng_count +=1; nt_count +=1
    else:
        rows = j.get("rows", [])
        if len(rows) == 0:
            print("  [OK ] AI‑ST‑022 查询返回空结果")
            ok_count +=1
        else:
            print(f"  [POK ] AI‑ST‑022 rows长度={len(rows)}")
            pok_count +=1

    print("\n" + "="*60)
    print(f"【测试汇总】 OK={ok_count}  POK={pok_count}  NG={ng_count}  NT={nt_count}")
    total = ok_count + pok_count + ng_count + nt_count
    if total >0:
        print(f"OK率：{ok_count/total*100:.1f}%")
    print("="*60)


if __name__ == "__main__":
    run()
