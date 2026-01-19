@echo off
chcp 65001 >nul
setlocal

set CONDA_ENV=xta_ai
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo ============================================================
echo    XAUUSD Trading AI - PyInstaller Build Script
echo ============================================================
echo.

REM Find Conda
set "CONDA_BASE="
if exist "%USERPROFILE%\miniconda3\Scripts\activate.bat" set "CONDA_BASE=%USERPROFILE%\miniconda3"
if exist "%USERPROFILE%\anaconda3\Scripts\activate.bat" set "CONDA_BASE=%USERPROFILE%\anaconda3"

if "%CONDA_BASE%"=="" (
    echo ERROR: Conda not found!
    pause
    exit /b 1
)

echo Conda: %CONDA_BASE%
echo Activating: %CONDA_ENV%

call "%CONDA_BASE%\Scripts\activate.bat" %CONDA_ENV%

echo.
echo Cleaning old build...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

echo.
echo Running PyInstaller...
pyinstaller XAUUSD_Trading_AI.spec --noconfirm

if errorlevel 1 (
    echo.
    echo ERROR: PyInstaller failed!
    pause
    exit /b 1
)

echo.
echo Copying files...
if not exist "dist\XAUUSD_AI\.streamlit" mkdir "dist\XAUUSD_AI\.streamlit"
copy /y "README.txt" "dist\XAUUSD_AI\" >nul 2>&1
copy /y "app_openai_zh.py" "dist\XAUUSD_AI\" >nul 2>&1
copy /y "XAUSD_AI_openai_zh.py" "dist\XAUUSD_AI\" >nul 2>&1
if exist ".streamlit\secrets.toml" copy /y ".streamlit\secrets.toml" "dist\XAUUSD_AI\.streamlit\" >nul 2>&1

echo.
echo ============================================================
echo    Build Complete!
echo ============================================================
echo.
echo Output: %SCRIPT_DIR%dist\XAUUSD_AI\
echo.

explorer "dist\XAUUSD_AI"

pause
