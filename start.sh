#!/bin/bash
# 启动脚本 for Unix/Linux/Mac

echo "================================"
echo "灵辑 (Smart Clip) API 服务器启动脚本"
echo "================================"
echo ""

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误：未找到 Python 3。请先安装 Python 3.8+"
    exit 1
fi

# 检查依赖是否安装
echo "检查依赖..."
if ! python3 -c "import fastapi" &> /dev/null; then
    echo "依赖未安装，正在安装..."
    pip3 install -r requirements.txt
fi

# 检查配置
if [ ! -f "config_local.py" ] && [ -z "$DASHSCOPE_API_KEY" ]; then
    echo ""
    echo "警告：未找到配置文件 config_local.py，且未设置环境变量。"
    echo "请执行以下步骤之一："
    echo "  1. 复制 config_local.py.example 为 config_local.py 并填入 API 密钥"
    echo "  2. 设置环境变量："
    echo "     export DASHSCOPE_API_KEY='your_key'"
    echo "     export APP_ID='your_app_id'"
    echo ""
    read -p "按回车键继续（将使用默认配置，可能无法正常工作）..."
fi

# 启动服务
echo ""
echo "启动服务中..."
python3 api_server.py


