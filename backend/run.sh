#!/bin/bash
# 徽派家私数字管理平台 - 后端启动脚本

echo "========================================"
echo "徽派家私数字管理平台 - 后端启动"
echo "========================================"
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请确保已安装Python"
    exit 1
fi

echo "已检测到Python..."
echo ""

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    echo "正在创建虚拟环境..."
    python3 -m venv venv
    echo "虚拟环境创建完成"
    echo ""
fi

# 激活虚拟环境
echo "正在激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "正在安装依赖..."
pip install -r requirements.txt -q

# 启动应用
echo ""
echo "========================================"
echo "启动 Flask 应用..."
echo "========================================"
echo "服务地址: http://localhost:5000"
echo "按 Ctrl+C 停止服务"
echo "========================================"
echo ""

python app.py
