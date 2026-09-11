# -*- coding: utf-8 -*-
"""被测系统全局配置（组员A：注册/登录/菜品管理模块）。"""
# ---- 被测服务地址 ----
BASE_URL = "http://127.0.0.1:5000"
# ---- 测试账号（请按本地数据库实际数据修改）----
# 用户 cjy，telephone=13992822786 role=0
TEST_PHONE_EXIST = "13992822786"   # 已注册普通用户手机号
TEST_PWD_VALID = "Cjy20041001"     # 合规密码：大小写+数字

# 商家账号 hui，username=hui，拥有 shop_id=1,3,5,6,7
MERCHANT_PHONE = "13772822786"
MERCHANT_PWD = "Gly001"
MERCHANT_SHOP_ID = 1      # shop_id=1【兰州拉面】，属于 hui，不会报403

# 用户 sxh，role=0，真实手机号11位
NORMAL_USER_PHONE = "13882822786"
NORMAL_USER_PWD = "Sxh0112"
