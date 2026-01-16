@echo off
chcp 65001 >nul
setlocal

REM 项目目录（按你实际路径）
cd /d C:\Users\hjw12\Desktop\XAUUSD_TRADING_ASISTENT_AI

REM 激活虚拟环境
call venv\Scripts\activate

REM 启动 Streamlit
start "" http://localhost:8501
python -m streamlit run app_openai_zh.py

endlocal
