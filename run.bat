@echo off
echo �������� V2Ray ������...
echo.

REM ���Python�Ƿ�װ
python --version > nul 2>&1
if errorlevel 1 (
    echo [����] δ��⵽Python����ȷ���Ѱ�װPython����ӵ�ϵͳ��������
    pause
    exit /b
)

REM ��������Ƿ��Ѱ�װ
if not exist "%~dp0\requirements.txt" (
    echo [����] δ�ҵ�requirements.txt�ļ�
    pause
    exit /b
)

echo ���ڼ�鲢��װ����...
pip install -r requirements.txt

echo.
echo ��������������...
echo ����������з���: http://localhost:8501
echo.

streamlit run app.py

pause
