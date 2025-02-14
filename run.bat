@echo off
echo 正在启动 V2Ray 监控面板...
echo.

REM 检查Python是否安装
python --version > nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请确保已安装Python并添加到系统环境变量
    pause
    exit /b
)

REM 检查依赖是否已安装
if not exist "%~dp0\requirements.txt" (
    echo [错误] 未找到requirements.txt文件
    pause
    exit /b
)

echo 正在检查并安装依赖...
pip install -r requirements.txt

echo.
echo 正在启动监控面板...
echo 请在浏览器中访问: http://localhost:8501
echo.

streamlit run app.py

pause
