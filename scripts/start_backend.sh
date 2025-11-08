#!/bin/bash

# 设置脚本在遇到错误时退出
set -e

# 设置UTF-8编码
export LANG=zh_CN.UTF-8
export LC_ALL=zh_CN.UTF-8

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

echo "========================================"
echo "  信息网络安全学院学生成果管理系统"
echo "  后端服务启动脚本 (UV版本)"
echo "========================================"
echo

# 获取脚本所在目录的父目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_DIR/backend"

# 切换到后端目录
cd "$BACKEND_DIR"

print_info "[1/5] 检查uv安装..."
if ! command -v uv &> /dev/null; then
    print_error "uv未安装，请先安装uv包管理器"
    print_info "安装命令: pip3 install uv"
    print_info "或访问: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi
print_success "uv已安装 ($(uv --version))"

echo
print_info "[2/5] 同步项目依赖..."
print_info "使用uv同步依赖包..."
if ! uv sync; then
    print_error "依赖同步失败"
    exit 1
fi
print_success "依赖同步完成"

echo
print_info "[3/5] 设置环境变量..."
export FLASK_APP=src/app/run.py
export FLASK_ENV=development
print_success "环境变量设置完成"

echo
print_info "[4/5] 检查数据库连接..."
print_info "如果首次运行，请确保已初始化数据库"
print_info "初始化命令: uv run python src/scripts/init_database.py"

echo
print_info "[5/5] 启动Flask应用..."
print_info "后端服务将在以下地址启动："
print_info "  本地访问: http://localhost:5000"
print_info "  局域网访问: http://[本机IP]:5000"
print_info "按 Ctrl+C 停止服务"
echo "========================================"

# 启动应用
uv run python -m app.run