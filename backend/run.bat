@echo off
REM 徽派家私数字管理平台 - 后端启动脚本

echo ========================================
echo 徽派家私数字管理平台 - 后端启动
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请确保已安装Python
    pause
    exit /b 1
)

echo 已检测到Python...
echo.

REM 创建虚拟环境（如果不存在）
if not exist "venv" (
    echo 正在创建虚拟环境...
    python -m venv venv
    echo 虚拟环境创建完成
    echo.
)

REM 激活虚拟环境
echo 正在激活虚拟环境...
call venv\Scripts\activate.bat

REM 安装依赖
echo 正在安装依赖...
pip install -r requirements.txt -q

REM 启动应用
echo.
echo ========================================
echo 启动 Flask 应用...
echo ========================================
echo 服务地址: http://localhost:5000
echo 按 Ctrl+C 停止服务
echo ========================================
echo.

python app.py

pause
