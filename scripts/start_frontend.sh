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
echo "  中国人民公安大学学生成果管理系统"
echo "  前端服务启动脚本"
echo "========================================"
echo

# 获取脚本所在目录的父目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
FRONTEND_DIR="$PROJECT_DIR/frontend"

# 切换到前端目录
cd "$FRONTEND_DIR"

print_info "[1/4] 检查Node.js环境..."
if ! command -v node &> /dev/null; then
    print_error "Node.js未安装或未添加到PATH环境变量"
    print_info "请访问 https://nodejs.org 下载安装Node.js"
    print_info "或使用包管理器安装："
    print_info "  Ubuntu/Debian: sudo apt install nodejs npm"
    print_info "  CentOS/RHEL: sudo yum install nodejs npm"
    print_info "  Arch Linux: sudo pacman -S nodejs npm"
    exit 1
fi

NODE_VERSION=$(node --version)
print_success "Node.js环境检查通过 ($NODE_VERSION)"

print_info "[2/4] 检查npm环境..."
if ! command -v npm &> /dev/null; then
    print_error "npm未安装"
    print_info "请安装npm包管理器"
    exit 1
fi

NPM_VERSION=$(npm --version)
print_success "npm环境检查通过 (v$NPM_VERSION)"

echo
print_info "[3/4] 检查项目依赖..."
if [ ! -d "node_modules" ]; then
    print_info "依赖包不存在，正在安装..."
    if ! npm install; then
        print_error "依赖包安装失败"
        print_info "请检查网络连接或尝试使用淘宝镜像："
        print_info "npm config set registry https://registry.npmmirror.com"
        exit 1
    fi
    print_success "依赖包安装完成"
else
    print_info "依赖包已存在，跳过安装..."
    print_success "依赖包检查完成"
fi

echo
print_info "[4/4] 检查后端服务连接..."
print_info "请确保后端服务已在 http://localhost:5000 启动"
print_warning "如果后端未启动，请先运行: ./scripts/start_backend.sh"

echo
print_info "启动Vue开发服务器..."
print_info "前端服务将在以下地址启动："
print_info "  本地访问: http://localhost:8080"
print_info "  局域网访问: http://[本机IP]:8080"
print_info "按 Ctrl+C 停止服务"
echo "========================================"

# 启动前端开发服务器
npm run serve