# -*- mode: python ; coding: utf-8 -*-
"""
XAUUSD 交易助手 - PyInstaller 打包配置文件
使用方法: pyinstaller XAUUSD_Trading_AI.spec
"""

import sys
import os
from pathlib import Path

# 增加递归限制以处理深度嵌套的导入
sys.setrecursionlimit(sys.getrecursionlimit() * 10)

# 获取项目根目录
project_root = Path(SPECPATH)

# 收集所有需要的数据文件
datas = [
    # 主应用文件
    (str(project_root / 'app_openai_zh.py'), '.'),
    (str(project_root / 'XAUSD_AI_openai_zh.py'), '.'),
    # 说明文件
    (str(project_root / 'README.txt'), '.'),
    # secrets.toml 模板
    (str(project_root / '.streamlit' / 'secrets.toml'), '.streamlit'),
]

# 隐藏导入（确保所有依赖被正确包含）
hiddenimports = [
    # Tkinter（输入弹窗需要）
    'tkinter',
    'tkinter.simpledialog',
    'tkinter.messagebox',
    
    # Streamlit 相关
    'streamlit',
    'streamlit.runtime.scriptrunner',
    'streamlit.runtime.scriptrunner.script_run_context',
    'streamlit.web.cli',
    'streamlit.web.bootstrap',
    'streamlit.runtime.caching',
    'streamlit.runtime.legacy_caching',
    'streamlit.elements',
    'streamlit.components',
    'streamlit.components.v1',
    
    # 数据处理
    'pandas',
    'pandas._libs',
    'pandas.io.formats.style',
    'numpy',
    'numpy.core._methods',
    'numpy.lib.format',
    
    # MetaTrader5
    'MetaTrader5',
    
    # LangChain 和 OpenAI
    'langchain_openai',
    'langchain_core',
    'langchain_core.prompts',
    'langchain_core.messages',
    'openai',
    'httpx',
    'httpcore',
    'anyio',
    'sniffio',
    'certifi',
    'h11',
    
    # 其他常用依赖
    'PIL',
    'PIL._tkinter_finder',
    'packaging',
    'packaging.version',
    'packaging.specifiers',
    'packaging.requirements',
    'pkg_resources',
    'altair',
    'pyarrow',
    'pydeck',
    'toml',
    'validators',
    'watchdog',
    'click',
    'rich',
    'markdown',
    'pympler',
    'tornado',
    'protobuf',
    'typing_extensions',
    'cachetools',
    'gitpython',
]

# 排除不需要的模块（减小体积）
# 注意：不要排除 tkinter，因为输入弹窗需要用到
excludes = [
    'unittest',
    'test',
    'tests',
    # 排除大型深度学习库（此项目不需要）
    'torch',
    'torchvision',
    'torchaudio',
    'tensorflow',
    'keras',
    'transformers',
    'scipy.spatial.transform._rotation_groups',
    # 排除其他不需要的模块
    'IPython',
    'jupyter',
    'notebook',
    'matplotlib.backends.backend_qt5agg',
    'matplotlib.backends.backend_tkagg',
    'PyQt5',
    'PyQt6',
    'PySide2',
    'PySide6',
]

block_cipher = None

a = Analysis(
    [str(project_root / 'launcher.py')],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[str(project_root)],  # 添加自定义 hook 目录
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='XAUUSD_AI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # 保留控制台窗口以显示日志
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 可以添加图标: icon='icon.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='XAUUSD_AI',
)
