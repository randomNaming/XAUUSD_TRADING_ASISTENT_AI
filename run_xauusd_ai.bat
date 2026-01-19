@echo off
chcp 65001 >nul
setlocal

REM ============================================================
REM    XAUUSD 交易助手 - 开发环境启动脚本
REM ============================================================

REM Conda 环境名称（可自定义修改）
set CONDA_ENV=py310

REM 获取脚本所在目录（使用相对路径）
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM 加载配置文件中的环境变量
if exist "config.bat" (
    call "config.bat"
)

REM 检查 OpenAI API Key
if "%OPENAI_API_KEY%"=="" (
    echo [错误] 未设置 OPENAI_API_KEY 环境变量！
    echo        请编辑 config.bat 文件并填写您的 API Key
    pause
    exit /b 1
)

if "%OPENAI_API_KEY%"=="YOUR_API_KEY_HERE" (
    echo [错误] 请在 config.bat 中设置您的 OpenAI API Key！
    echo        将 YOUR_API_KEY_HERE 替换为您的实际 API Key
    pause
    exit /b 1
)

REM 查找 Conda 安装路径
set "CONDA_BASE="
if exist "%USERPROFILE%\miniconda3\Scripts\activate.bat" (
    set "CONDA_BASE=%USERPROFILE%\miniconda3"
) else if exist "%USERPROFILE%\anaconda3\Scripts\activate.bat" (
    set "CONDA_BASE=%USERPROFILE%\anaconda3"
) else if exist "C:\ProgramData\miniconda3\Scripts\activate.bat" (
    set "CONDA_BASE=C:\ProgramData\miniconda3"
) else if exist "C:\ProgramData\anaconda3\Scripts\activate.bat" (
    set "CONDA_BASE=C:\ProgramData\anaconda3"
)

REM 激活 Conda 环境
if not "%CONDA_BASE%"=="" (
    echo 激活 Conda 环境: %CONDA_ENV%
    call "%CONDA_BASE%\Scripts\activate.bat" %CONDA_ENV%
) else (
    REM 尝试激活本地 venv
    if exist "venv\Scripts\activate.bat" (
        echo 激活本地虚拟环境...
        call "venv\Scripts\activate.bat"
    )
)

REM 启动浏览器
start "" http://localhost:8501

REM 启动 Streamlit
echo 正在启动 XAUUSD 交易助手...
python -m streamlit run app_openai_zh.py

endlocal
