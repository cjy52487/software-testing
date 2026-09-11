#!/usr/bin/env bash
# 一键运行组员A全部自动化用例
# 用法: bash run_all.sh
set -e
cd "$(dirname "$0")"

echo "========== 安装依赖 =========="
pip3 install -r requirements.txt -q

echo "========== 运行全部测试 =========="
python3 -m pytest

echo "========== 测试结束 =========="
