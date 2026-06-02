# Toutiao FastAPI Vue

一个基于 FastAPI 和 Vue 3 的仿头条新闻项目，包含新闻分类、新闻列表、新闻详情、用户登录注册、个人资料维护和新闻收藏等功能。仓库同时包含后端 API 服务和前端页面。

## 功能概览

- 新闻分类查询
- 新闻分页列表
- 新闻详情与相关推荐
- 用户注册、登录和 token 鉴权
- 用户资料更新
- 用户密码修改
- 新闻收藏、取消收藏和收藏状态检查
- Vue 3 前端页面与 Vite 本地代理

## 技术栈

后端：

- Python 3.10+
- FastAPI
- SQLAlchemy 2.x async
- aiomysql
- MySQL
- uvicorn

前端：

- Vue 3
- Vite
- npm

## 项目结构

```text
.
├── config/              # 数据库连接与基础配置
├── crud/                # 数据访问逻辑
├── frontend/            # Vue 3 + Vite 前端
├── models/              # SQLAlchemy 数据模型
├── routers/             # FastAPI 路由
├── schemas/             # Pydantic 请求/响应模型
├── utils/               # 鉴权、响应、异常处理等工具
├── main.py              # FastAPI 应用入口
├── pyproject.toml       # 后端依赖配置
└── uv.lock              # uv 锁文件
```

## 环境准备

请先准备：

- Python 3.10 或更高版本
- uv
- Node.js 和 npm
- MySQL 8.x 或兼容版本

数据库连接通过 `DATABASE_URL` 配置，示例见 `.env.example`：

```env
DATABASE_URL=mysql+aiomysql://root:123456@127.0.0.1:3306/toutiao_backend?charset=utf8mb4
DEBUG_MODE=false
```

建议根据本机 MySQL 用户名、密码、端口和数据库名调整 `.env`。

## 后端启动

安装依赖：

```bash
uv sync
```

启动 API 服务：

```bash
uv run uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

启动后可访问：

- API 文档：http://127.0.0.1:8000/docs
- 健康检查：http://127.0.0.1:8000/health

## 前端启动

进入前端目录并安装依赖：

```bash
cd frontend
npm install
```

启动开发服务：

```bash
npm run dev
```

默认访问地址：

```text
http://127.0.0.1:5173
```

前端开发服务已经配置 `/api` 代理，会转发到 `http://127.0.0.1:8000`。

## 数据库说明

当前项目没有内置迁移脚本，运行前需要先创建数据库并准备数据表。模型定义位于 `models/` 目录，核心表包括：

- `news_categories`
- `news_articles`
- `users`
- `tokens`
- `favorites`

示例建库语句：

```sql
CREATE DATABASE IF NOT EXISTS toutiao_backend
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
```

如果后续需要更稳定的团队协作流程，建议补充 Alembic 迁移。

## 主要接口

### 新闻

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| `GET` | `/news/` | 获取新闻分类 |
| `GET` | `/news/list?categoryId=1&page=1&pageSize=10` | 获取新闻列表 |
| `GET` | `/news/detail?id=1` | 获取新闻详情 |

### 用户

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| `POST` | `/users/` | 注册 |
| `POST` | `/users/login` | 登录 |
| `GET` | `/users/info` | 获取当前用户信息 |
| `PATCH` | `/users/info` | 更新当前用户信息 |
| `PUT` | `/users/password` | 修改密码 |

### 收藏

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| `GET` | `/favorites/check?newsId=1` | 检查是否已收藏 |
| `POST` | `/favorites/` | 收藏新闻 |
| `POST` | `/favorites/add` | 收藏新闻兼容接口 |
| `DELETE` | `/favorites/?newsId=1` | 取消收藏 |

需要登录的接口请在请求头中携带：

```text
Authorization: Bearer <token>
```

## 响应格式

接口统一返回类似结构：

```json
{
  "code": 200,
  "message": "成功",
  "data": {}
}
```

异常响应会通过统一异常处理返回对应的 `code`、`message` 和 `data` 字段。

## 常用命令

后端导入检查：

```bash
uv run python -c "import main; print('import main ok')"
```

后端语法编译检查：

```bash
uv run python -m compileall routers crud schemas models utils config main.py
```

前端构建：

```bash
cd frontend
npm run build
```

## 注意事项

- `.env` 中可能包含数据库账号密码，请不要提交真实敏感信息。
- 当前 token 存储在数据库 `tokens` 表中，接口通过 `Authorization` 请求头读取。
- 收藏接口同时保留 `/favorites/` 和 `/favorites/add`，方便兼容不同前端调用方式。
- 当前项目未配置自动化测试；上线前建议补充 API 测试和数据库迁移脚本。
