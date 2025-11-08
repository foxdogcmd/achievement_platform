@echo off
chcp 65001 >nul
title 信息网络安全学院学生成果管理系统 - 前端服务

echo ========================================
echo   信息网络安全学院学生成果管理系统
echo   前端服务启动脚本
echo ========================================
echo.

cd /d "%~dp0..\frontend"

echo [1/4] 检查Node.js环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js未安装或未添加到PATH环境变量
    echo [INFO] 请访问 https://nodejs.org 下载安装Node.js
    pause
    exit /b 1
)
echo [SUCCESS] Node.js环境检查通过

echo.
echo [2/4] 检查项目依赖...
if not exist "node_modules" (
    echo [INFO] 依赖包不存在，正在安装...
    call npm install
    if errorlevel 1 (
        echo [ERROR] 依赖包安装失败
        echo [INFO] 请检查网络连接或尝试使用淘宝镜像：
        echo [INFO] npm config set registry https://registry.npmmirror.com
        pause
        exit /b 1
    )
    echo [SUCCESS] 依赖包安装完成
) else (
    echo [INFO] 依赖包已存在，跳过安装...
    echo [SUCCESS] 依赖包检查完成
)

echo.
echo [3/4] 检查后端服务连接...
echo [INFO] 请确保后端服务已在 http://localhost:5000 启动

echo.
echo [4/4] 启动Vue开发服务器...
echo [INFO] 前端服务将在以下地址启动：
echo [INFO]   本地访问: http://localhost:8080
echo [INFO]   局域网访问: http://[本机IP]:8080
echo [INFO] 按 Ctrl+C 停止服务
echo ========================================
call npm run serve

echo.
echo [INFO] 前端服务已停止
pause