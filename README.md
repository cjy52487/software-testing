本项目是针对https://github.com/hui0509/food_delivery_app的测试。

项目部署问题：前端登录/注册时始终报错：`timeout of 10000ms exceeded`（请求超时），错误代码 `ECONNABORTED`。

#### 问题1：前端缺少代理配置

**文件**：`前端代码/sjk/vue.config.js`

原始的 `vue.config.js` 只有基础配置，**没有配置 `proxy` 代理**。导致前端请求无法正确转发到后端 5000 端口。

**修复**：添加代理配置：
```javascript
proxy: {
  '/api': {
    target: 'http://localhost:5000',
    changeOrigin: true
  }
}
```

#### 问题2：MySQL 密码含@

**原因**：在数据库连接字符串中，@是一个有特殊含义的保留字符。标准格式是 `协议://用户名:密码@主机:端口/数据库`，@符号是用来分隔“密码”和“主机地址”的。如果密码本身也包含@，解析器无法准确判断连接字符串的各个部分。

**修复**：在 MySQL 命令行中执行 `ALTER USER` 将密码改为纯英文数字。

#### 问题3：缺少 `.env` 配置文件

**现象**：`后端代码` 目录下**没有 `.env` 文件**（`dir` 命令已证实）

**原因**：项目文档要求创建 `.env` 文件配置数据库连接信息，但该文件缺失。虽然后端最终仍能启动（可能读取了 `config.py` 中的配置），但配置来源不统一。

**修复**：在 `后端代码` 目录下创建 `.env` 文件，内容包含 `DB_HOST`、`DB_PASSWORD`、`DB_NAME` 等。

#### 问题4：前端硬编码了错误的 IP 地址

**文件**：`前端代码/sjk/src/api/index.js`

**现象**：
```
URL: http://192.168.0.100:5000/api/user/register/test
```

**原因**：`getCorrectBaseURL` 函数中硬编码了 `192.168.0.100`，但用 `ipconfig` 查到的实际 IP 是 `10.72.0.249`，导致请求发往一个不存在的地址，自然超时。

**修复**：
- 将 `computerIP` 改为自己电脑的IPv4地址
- 直接使用 `/api`（走代理）或 `http://localhost:5000`（本机开发最简单）



#### 运行项目

* 前端：

  ```
  npm i
  npm run serve
  ```

* 后端：

  1. 修改数据库密码
  2. 修改电脑IP地址

  ```
  python app.py
  ```

* 数据库：创建数据库并导入dba.sql，数据库名与后端代码中一致