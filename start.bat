@echo off
REM 启动脚本 for Windows
chcp 65001 >nul

echo ================================
echo 灵辑 (Smart Clip) API 服务器启动脚本
echo ================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到 Python。请先安装 Python 3.8+
    pause
    exit /b 1
)

REM 检查依赖是否安装
echo 检查依赖...
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo 依赖未安装，正在安装...
    pip install -r requirements.txt
)

REM 检查配置
if not exist "config_local.py" (
    if "%DASHSCOPE_API_KEY%"=="" (
        echo.
        echo 警告：未找到配置文件 config_local.py，且未设置环境变量。
        echo 请执行以下步骤之一：
        echo   1. 复制 config_local.py.example 为 config_local.py 并填入 API 密钥
        echo   2. 设置环境变量：
        echo      set DASHSCOPE_API_KEY=your_key
        echo      set APP_ID=your_app_id
        echo.
        pause
    )
)

REM 启动服务
echo.
echo 启动服务中...
python api_server.py

pause


