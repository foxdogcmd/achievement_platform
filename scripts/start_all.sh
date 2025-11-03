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
PURPLE='\033[0;35m'
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

print_header() {
    echo -e "${PURPLE}[SYSTEM]${NC} $1"
}

# 清理函数
cleanup() {
    print_warning "正在停止所有服务..."
    
    # 杀死后台进程
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
        print_info "后端服务已停止"
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
        print_info "前端服务已停止"
    fi
    
    print_success "所有服务已停止"
    exit 0
}

# 设置信号处理
trap cleanup SIGINT SIGTERM

echo "========================================"
echo "  中国人民公安大学学生成果管理系统"
echo "  一键启动脚本 (前端 + 后端)"
echo "========================================"
echo

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 检查脚本是否存在
if [ ! -f "$SCRIPT_DIR/start_backend.sh" ]; then
    print_error "后端启动脚本不存在: $SCRIPT_DIR/start_backend.sh"
    exit 1
fi

if [ ! -f "$SCRIPT_DIR/start_frontend.sh" ]; then
    print_error "前端启动脚本不存在: $SCRIPT_DIR/start_frontend.sh"
    exit 1
fi

# 确保脚本有执行权限
chmod +x "$SCRIPT_DIR/start_backend.sh"
chmod +x "$SCRIPT_DIR/start_frontend.sh"

print_header "=== 第一阶段：启动后端服务 ==="
print_info "正在启动后端服务..."

# 启动后端服务（后台运行）
"$SCRIPT_DIR/start_backend.sh" &
BACKEND_PID=$!

print_info "后端服务启动中... (PID: $BACKEND_PID)"
print_info "等待后端服务初始化..."

# 等待后端服务启动
sleep 5

# 检查后端服务是否正在运行
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    print_error "后端服务启动失败"
    exit 1
fi

print_success "后端服务启动成功"

echo
print_header "=== 第二阶段：启动前端服务 ==="
print_info "正在启动前端服务..."

# 启动前端服务（后台运行）
"$SCRIPT_DIR/start_frontend.sh" &
FRONTEND_PID=$!

print_info "前端服务启动中... (PID: $FRONTEND_PID)"
print_info "等待前端服务初始化..."

# 等待前端服务启动
sleep 10

# 检查前端服务是否正在运行
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    print_error "前端服务启动失败"
    cleanup
    exit 1
fi

print_success "前端服务启动成功"

echo
print_header "=== 服务启动完成 ==="
print_success "所有服务已成功启动！"
echo
print_info "服务访问地址："
print_info "  前端服务: http://localhost:8080"
print_info "  后端API: http://localhost:5000"
echo
print_info "服务进程信息："
print_info "  后端进程 PID: $BACKEND_PID"
print_info "  前端进程 PID: $FRONTEND_PID"
echo
print_warning "按 Ctrl+C 停止所有服务"
echo "========================================"

# 等待用户中断
while true; do
    sleep 1
    
    # 检查进程是否还在运行
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        print_error "后端服务意外停止"
        cleanup
        exit 1
    fi
    
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        print_error "前端服务意外停止"
        cleanup
        exit 1
    fi
done