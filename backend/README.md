# 成果管理系统后端（Flask）

本后端使用 uv 进行现代化的依赖与运行管理。

## 快速开始

1. 安装 uv（一次性）

   ```shell
   pip install uv
   ```

2. 同步依赖并运行

   ```shell
   cd backend
   uv sync
   uv pip install -e .
   uv run backend
   ```

## 环境变量

创建 `backend/.env`（或在系统环境变量中设置）：

```text
DATABASE_URL=postgresql://postgres:password@localhost:5432/achievement_platform
SECRET_KEY=dev-secret
JWT_SECRET_KEY=dev-jwt
PORT=5000
FLASK_ENV=development
```

## 数据初始化

在根目录执行：

```shell
uv run init_db
```
