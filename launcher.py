# -*- coding: utf-8 -*-
"""
XAUUSD 交易助手 - 启动器
用于检查环境变量、显示错误提示并启动Streamlit应用
"""

import os
import sys
import webbrowser
import time
import threading
import ctypes
from pathlib import Path


def get_base_path():
    """获取程序运行的基础路径（支持打包后和开发环境）"""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    else:
        return Path(__file__).parent


def show_error_dialog(title: str, message: str):
    """显示Windows错误弹窗"""
    MB_OK = 0x0
    MB_ICONERROR = 0x10
    ctypes.windll.user32.MessageBoxW(0, message, title, MB_OK | MB_ICONERROR)


def show_input_dialog(title: str, prompt: str) -> str:
    """显示输入对话框获取用户输入"""
    try:
        import tkinter as tk
        from tkinter import simpledialog
        
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
        result = simpledialog.askstring(title, prompt, parent=root)
        
        root.destroy()
        return result if result else ""
    except Exception as e:
        print(f"无法显示输入对话框: {e}")
        return ""


def load_secrets_toml(secrets_file: Path) -> dict:
    """读取 secrets.toml 文件"""
    secrets = {}
    if secrets_file.exists():
        try:
            with open(secrets_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        secrets[key] = value
        except Exception as e:
            print(f"警告: 读取 secrets.toml 失败: {e}")
    return secrets


def save_secrets_toml(secrets_file: Path, api_key: str):
    """保存 API Key 到 secrets.toml"""
    secrets_file.parent.mkdir(parents=True, exist_ok=True)
    with open(secrets_file, 'w', encoding='utf-8') as f:
        f.write(f'OPENAI_API_KEY = "{api_key}"\n')


def get_api_key(base_path: Path) -> str:
    """获取 OpenAI API Key"""
    api_key = os.environ.get('OPENAI_API_KEY', '').strip()
    if api_key:
        return api_key
    
    secrets_file = base_path / ".streamlit" / "secrets.toml"
    secrets = load_secrets_toml(secrets_file)
    api_key = secrets.get('OPENAI_API_KEY', '').strip()
    if api_key:
        return api_key
    
    return ""


def prompt_for_api_key(base_path: Path) -> str:
    """弹窗提示用户输入 API Key"""
    api_key = show_input_dialog(
        "XAUUSD 交易助手 - 配置",
        "请输入您的 OpenAI API Key:\n\n"
        "(获取地址: https://platform.openai.com/api-keys)\n\n"
        "输入后将自动保存到配置文件"
    )
    
    if api_key and api_key.strip():
        api_key = api_key.strip()
        secrets_file = base_path / ".streamlit" / "secrets.toml"
        save_secrets_toml(secrets_file, api_key)
        return api_key
    
    return ""


def check_and_get_api_key(base_path: Path) -> str:
    """检查并获取 API Key"""
    api_key = get_api_key(base_path)
    
    if not api_key:
        api_key = prompt_for_api_key(base_path)
    
    if not api_key:
        show_error_dialog(
            "XAUUSD 交易助手 - 配置错误",
            "未配置 OpenAI API Key！\n\n"
            "请编辑 .streamlit\\secrets.toml 文件\n"
            "添加：OPENAI_API_KEY = \"您的API密钥\"\n\n"
            "获取 API Key: https://platform.openai.com/api-keys"
        )
        return ""
    
    return api_key


def open_browser_delayed(url: str, delay: float = 2.0):
    """延迟打开浏览器"""
    time.sleep(delay)
    webbrowser.open(url)


def create_streamlit_config(base_path: Path):
    """创建 Streamlit 配置文件"""
    config_dir = base_path / ".streamlit"
    config_dir.mkdir(exist_ok=True)
    
    config_file = config_dir / "config.toml"
    config_content = """[global]
developmentMode = false

[server]
port = 8501
headless = true
enableCORS = false
enableXsrfProtection = true
runOnSave = false

[browser]
gatherUsageStats = false
serverAddress = "localhost"
"""
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(config_content)


def run_streamlit_directly(app_file: str, api_key: str, base_path: Path):
    """直接运行 Streamlit"""
    # 设置环境变量
    os.environ['OPENAI_API_KEY'] = api_key
    
    # 创建配置文件
    create_streamlit_config(base_path)
    
    url = "http://localhost:8501"
    
    # 延迟打开浏览器
    browser_thread = threading.Thread(target=open_browser_delayed, args=(url, 2.0))
    browser_thread.daemon = True
    browser_thread.start()
    
    print(f"正在启动 XAUUSD 交易助手...")
    print(f"浏览器将自动打开: {url}")
    print(f"如果浏览器未自动打开，请手动访问上述地址")
    print("-" * 50)
    
    # 使用最简单的方式：直接调用 streamlit.web.cli 的内部函数
    import streamlit.web.cli as cli
    
    # 修改 sys.argv 来模拟命令行调用
    sys.argv = [
        "streamlit",
        "run",
        app_file,
        "--server.port=8501",
        "--server.headless=true",
        "--browser.gatherUsageStats=false",
        "--global.developmentMode=false",
    ]
    
    # 调用 streamlit 的主入口
    cli.main()


def main():
    """主入口"""
    print("=" * 50)
    print("    XAUUSD 交易助手 - 启动中...")
    print("=" * 50)
    
    base_path = get_base_path()
    
    # 设置工作目录
    os.chdir(base_path)
    
    # 1. 检查 API Key
    print("[1/2] 检查 API Key 配置...")
    api_key = check_and_get_api_key(base_path)
    if not api_key:
        input("\n按回车键退出...")
        sys.exit(1)
    
    # 保存到 secrets.toml
    secrets_file = base_path / ".streamlit" / "secrets.toml"
    save_secrets_toml(secrets_file, api_key)
    
    print("      ✓ API Key 配置完成")
    
    # 2. 查找应用文件
    print("[2/2] 启动应用程序...")
    app_file = base_path / "app_openai_zh.py"
    if not app_file.exists():
        app_file = base_path / "_internal" / "app_openai_zh.py"
    
    if not app_file.exists():
        show_error_dialog(
            "XAUUSD 交易助手 - 错误",
            f"找不到应用程序文件！\n"
            f"请确保 app_openai_zh.py 存在于程序目录中。"
        )
        input("\n按回车键退出...")
        sys.exit(1)
    
    # 3. 运行 Streamlit
    try:
        run_streamlit_directly(str(app_file), api_key, base_path)
    except SystemExit:
        # Streamlit 正常退出
        pass
    except Exception as e:
        show_error_dialog(
            "XAUUSD 交易助手 - 错误",
            f"启动失败！\n\n错误详情: {e}"
        )
        import traceback
        traceback.print_exc()
        input("\n按回车键退出...")
        sys.exit(1)


if __name__ == "__main__":
    main()
