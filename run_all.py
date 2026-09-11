# -*- coding: utf-8 -*-
"""一键运行入口（跨平台）。用法: python3 run_all.py"""
import os
import subprocess
import sys


def main():
    # 强制 Python 使用 UTF-8 编码，避免中文路径/文件导致的 GBK 解码错误
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"

    cmd = [sys.executable, "-m", "pytest", "-v"]
    print(">>> 运行命令:", " ".join(cmd))
    code = subprocess.call(cmd, env=env)
    print(">>> 测试退出码:", code)
    return code


if __name__ == "__main__":
    sys.exit(main())
