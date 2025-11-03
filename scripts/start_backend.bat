@echo off
chcp 65001 >nul
title 中国人民公安大学学生成果管理系统 - 后端服务

echo ========================================
echo   中国人民公安大学学生成果管理系统
echo   后端服务启动脚本 (UV版本)
echo ========================================
echo.

cd /d "%~dp0..\backend"

echo [1/5] 检查uv安装...
uv --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] uv未安装，请先安装uv包管理器
    echo [INFO] 安装命令: pip install uv
    echo [INFO] 或访问: https://docs.astral.sh/uv/getting-started/installation/
    pause
    exit /b 1
)
echo [SUCCESS] uv已安装

echo.
echo [2/5] 同步项目依赖...
echo [INFO] 使用uv同步依赖包...
uv sync
if errorlevel 1 (
    echo [ERROR] 依赖同步失败
    pause
    exit /b 1
)
echo [SUCCESS] 依赖同步完成

echo.
echo [3/5] 设置环境变量...
set FLASK_APP=src/app/run.py
set FLASK_ENV=development
echo [SUCCESS] 环境变量设置完成

echo.
echo [4/5] 检查数据库连接...
echo [INFO] 如果首次运行，请确保已初始化数据库
echo [INFO] 初始化命令: uv run python src/scripts/init_database.py

echo.
echo [5/5] 启动Flask应用...
echo [INFO] 后端服务将在以下地址启动：
echo [INFO]   本地访问: http://localhost:5000
echo [INFO]   局域网访问: http://[本机IP]:5000
echo [INFO] 按 Ctrl+C 停止服务
echo ========================================
uv run python src/app/run.py

echo.
echo [INFO] 后端服务已停止
pause