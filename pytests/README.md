# 自动化测试脚本运行说明

> 项目地址：https://github.com/cjy52487/software-testing 用途：说明本仓库自动化测试脚本环境准备、执行步骤、常见问题，可直接粘贴到项目README.md中

## 自动化测试脚本运行指南

### 1. 项目简介

本仓库为软件测试相关项目，包含自动化测试脚本，支持接口自动化/功能自动化用例执行，下面说明脚本部署与运行流程。

### 2. 环境依赖

#### Python版本

推荐 Python3.8 ~ Python3.11

#### 安装第三方依赖

```
# 克隆代码仓库
git clone https://github.com/cjy52487/software-testing.git
cd software-testing

# 安装依赖包
pip install -r requirements.txt
```

> 如果仓库内没有`requirements.txt`，请根据脚本导入模块手动安装依赖，例如 pytest、requests、selenium、allure‑pytest 等。

### 3. 目录结构参考

```
software-testing/
├── test_case/          # 测试用例脚本目录
├── config/             # 配置文件（接口地址、账号、浏览器配置）
├── common/             # 公共封装工具类
├── reports/            # 测试报告输出目录（运行后自动生成）
├── requirements.txt    # 依赖清单
└── run_test.py         # 测试入口脚本
```

### 4. 运行方式

#### 方式1：直接运行入口脚本

```
python run_test.py
```

#### 方式2：使用pytest执行全部用例

```
# 执行全部测试用例
pytest test_case/ -v

# 执行指定用例文件
pytest test_case/test_api.py -v

# 生成allure测试报告
pytest test_case/ --alluredir=reports/allure-results
allure generate reports/allure-results -o reports/allure-report --clean
# 打开报告
allure open reports/allure-report
```

### 5. 配置修改说明

进入`config`目录，修改配置文件：

- 修改被测服务的请求base_url；
- 修改测试账号、密码、token等测试数据；
- WebUI自动化需要配置浏览器驱动路径。

### 6. 运行结果说明

- 控制台输出：展示每条用例执行结果：PASSED(通过) / FAILED(失败) / SKIPPED(跳过)
- allure报告：在`reports/allure-report/index.html`，浏览器打开查看可视化测试报告，包含失败用例、错误堆栈、请求日志。

### 7. 常见问题排查

1. 模块导入报错 ModuleNotFoundError
   - 确认已执行`pip install -r requirements.txt`；确认当前工作目录是项目根目录。
2. 接口请求连接失败
   - 确认被测服务已经启动，config内base_url地址正确，网络可访问被测服务。
3. Allure命令找不到
   - 需要单独安装allure命令行工具，配置系统环境变量。
4. Web自动化浏览器启动失败
   - 检查浏览器版本与driver驱动版本匹配。

### 8. 其他说明

- 部分用例依赖前置测试数据，运行前需要保证被测系统基础测试数据已准备完成；
- 如果需要持续集成，可以将上述pytest命令配置入GitHub Actions脚本实现自动化执行。