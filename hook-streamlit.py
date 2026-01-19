# -*- coding: utf-8 -*-
"""
PyInstaller hook for Streamlit
确保 Streamlit 的所有资源文件都被正确打包
"""

from PyInstaller.utils.hooks import (
    collect_data_files,
    collect_submodules,
    copy_metadata,
)

# 收集 Streamlit 的所有子模块
hiddenimports = collect_submodules('streamlit')

# 收集 Streamlit 的数据文件（HTML/CSS/JS 等）
datas = collect_data_files('streamlit')

# 收集元数据
datas += copy_metadata('streamlit')

# 添加额外的隐藏导入
hiddenimports += [
    'streamlit.runtime.scriptrunner.magic_funcs',
    'streamlit.runtime.scriptrunner.script_runner',
    'streamlit.runtime.scriptrunner.script_run_context',
    'streamlit.web.server.server',
    'streamlit.web.server.server_util',
    'streamlit.web.server.routes',
    'streamlit.web.server.browser_websocket_handler',
    'streamlit.web.server.component_request_handler',
    'streamlit.web.server.media_file_handler',
    'streamlit.web.server.upload_file_request_handler',
    'streamlit.web.bootstrap',
    'streamlit.web.cli',
    'streamlit.components.v1',
    'streamlit.components.v1.components',
    'streamlit.elements',
    'streamlit.elements.image',
    'streamlit.elements.media',
    'streamlit.elements.utils',
    'streamlit.runtime.caching',
    'streamlit.runtime.caching.cache_data_api',
    'streamlit.runtime.caching.cache_resource_api',
    'streamlit.runtime.legacy_caching',
    'streamlit.runtime.legacy_caching.caching',
    'streamlit.runtime.state',
    'streamlit.runtime.state.session_state',
    'streamlit.runtime.uploaded_file_manager',
    'streamlit.runtime.memory_uploaded_file_manager',
    'streamlit.config',
    'streamlit.config_option',
    'streamlit.secrets',
    'streamlit.logger',
    'streamlit.watcher',
    'streamlit.watcher.local_sources_watcher',
    'validators',
    'tornado',
    'tornado.web',
    'tornado.websocket',
    'tornado.httpserver',
    'tornado.ioloop',
    'tornado.routing',
]
