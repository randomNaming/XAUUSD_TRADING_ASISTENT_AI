# XAUUSD AI 交易助手

一个基于 AI 的黄金（XAUUSD）交易分析助手，通过 MetaTrader5 获取实时市场数据，使用 OpenAI GPT-4 进行多周期技术分析和交易信号生成。

## 📋 项目简介

本项目是一个智能化的黄金交易分析工具，结合了：
- **MetaTrader5**：实时获取多周期K线数据和市场信息
- **OpenAI GPT-4**：基于多周期数据进行深度技术分析和交易信号生成
- **Streamlit**：提供现代化的 Web 界面展示分析结果

## ✨ 主要功能

### 1. 多周期技术分析
- 支持 D1、H4、H1、M30、M15、M5 六个时间周期
- 自动计算 RSI、EMA（20/50/200）、ATR 等技术指标
- AI 分析市场结构、支撑阻力、供需区、订单块等

### 2. 智能交易信号
- 基于多周期共振生成交易信号
- 自动计算入场区间、止损、止盈点位
- 提供置信度评估和风险提示

### 3. 当日行情分析
- 实时显示当前价格、涨跌幅、振幅等关键数据
- 提供两套交易方案（回踩/反弹 和 突破/破位）
- 基于 ATR 的预测区间计算

### 4. 自动化功能
- 支持 30 分钟自动刷新分析
- 一键生成完整分析报告

## 🛠 技术栈

- **Python 3.10+**
- **Streamlit**：Web 界面框架
- **MetaTrader5**：交易平台 API
- **LangChain + OpenAI**：AI 分析引擎
- **Pandas + NumPy**：数据处理
- **PyInstaller**：打包工具

## 📦 安装要求

### 前置条件

1. **Python 3.10 或更高版本**
2. **MetaTrader5 客户端**
   - 下载地址：https://www.metatrader5.com/
   - 需要登录交易账户
   - 确保 XAUUSD 品种可用

3. **OpenAI API Key**
   - 访问 https://platform.openai.com/api-keys 获取
   - 确保账户有足够余额

### 安装步骤

1. **克隆或下载项目**
```bash
cd XAUUSD_TRADING_ASISTENT_AI
```

2. **创建虚拟环境（推荐）**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

## ⚙️ 配置说明

### 方式一：使用配置文件（推荐）

1. 在项目根目录创建 `.streamlit` 文件夹
2. 创建 `secrets.toml` 文件，内容如下：
```toml
OPENAI_API_KEY = "your-api-key-here"
```

### 方式二：使用环境变量

设置系统环境变量：
```bash
set OPENAI_API_KEY=your-api-key-here  # Windows CMD
```

或在 PowerShell 中：
```powershell
$env:OPENAI_API_KEY="your-api-key-here"
```

### 方式三：首次运行时输入

程序首次运行时会弹出对话框，可直接输入 API Key，程序会自动保存到配置文件。

## 🚀 使用方法

### 开发模式运行

1. **确保 MetaTrader5 已启动并登录**

2. **运行启动器**
```bash
python launcher.py
```

或直接运行 Streamlit 应用：
```bash
streamlit run app_openai_zh.py
```

3. **访问 Web 界面**
   - 浏览器会自动打开 http://localhost:8501
   - 或手动访问该地址

4. **使用界面**
   - 点击左侧「运行新分析」按钮
   - 等待分析完成（需要几秒到几十秒）
   - 查看各个标签页的分析结果

### 打包版本运行

如果使用打包后的 `.exe` 文件：

1. 双击 `XAUUSD_AI.exe`
2. 首次运行会提示输入 API Key
3. 浏览器自动打开分析界面

## 📁 项目结构

```
XAUUSD_TRADING_ASISTENT_AI/
├── app_openai_zh.py          # Streamlit 主应用界面
├── XAUSD_AI_openai_zh.py     # 核心交易逻辑和 AI 分析
├── launcher.py                # 启动器（处理配置和启动）
├── requirements.txt           # Python 依赖包
├── XAUUSD_Trading_AI.spec    # PyInstaller 打包配置
├── build.bat                  # 构建脚本
├── hook-streamlit.py         # PyInstaller Hook
├── README.md                  # 项目说明文档
├── README.txt                 # 使用说明（打包版）
└── .streamlit/               # Streamlit 配置目录
    ├── config.toml           # Streamlit 配置
    └── secrets.toml          # API Key 配置（需创建）
```

## 🔨 构建可执行文件

### 使用构建脚本（推荐）

```bash
build.bat
```

### 手动构建

1. **安装 PyInstaller**
```bash
pip install pyinstaller
```

2. **运行打包命令**
```bash
pyinstaller XAUUSD_Trading_AI.spec --noconfirm
```

3. **输出位置**
   - 可执行文件位于 `dist/XAUUSD_AI/` 目录
   - 包含所有必要的依赖文件

## 📊 功能说明

### 分析标签页

1. **今日行情**：当日市场快照和 AI 生成的行情分析报告
2. **入场点位**：详细的交易信号，包括入场、止损、止盈点位
3. **技术分析**：多周期技术面分析，包括趋势、结构、指标解读
4. **预测区间**：基于 ATR 计算的各周期预测区间
5. **多周期数据**：各时间周期最近 10 根 K 线数据及指标

### 侧边栏功能

- **自动刷新**：开启后每 30 分钟自动更新分析
- **当前点差**：显示实时点差信息
- **最后更新时间**：显示分析结果的时间戳

## ⚠️ 注意事项

1. **MetaTrader5 连接**
   - 必须确保 MT5 客户端已启动并登录
   - 确保 XAUUSD 品种在您的账户中可用
   - 如果连接失败，检查 MT5 是否正常运行

2. **API Key 安全**
   - 不要将 API Key 提交到版本控制系统
   - 建议使用环境变量或配置文件（已加入 .gitignore）

3. **网络要求**
   - 需要能够访问 OpenAI API（可能需要代理）
   - 确保网络连接稳定

4. **风险提示**
   - 本工具仅提供分析参考，不构成投资建议
   - 交易有风险，请谨慎决策
   - 建议结合自己的交易策略使用

5. **性能说明**
   - 每次分析需要调用 OpenAI API，可能需要几秒到几十秒
   - 建议不要过于频繁地刷新分析（API 有调用限制和费用）

## 🐛 常见问题

### Q: 提示 "MT5 初始化失败"
**A:** 确保 MetaTrader5 客户端已启动并登录账户。

### Q: 提示 "缺少 OpenAI API Key"
**A:** 检查配置文件 `.streamlit/secrets.toml` 或环境变量是否已正确设置。

### Q: 浏览器未自动打开
**A:** 手动访问 http://localhost:8501

### Q: 分析结果为空或错误
**A:** 
- 检查 MT5 数据是否正常
- 检查网络连接（需要访问 OpenAI API）
- 检查 API Key 是否有效且有余额

### Q: 打包后的 exe 无法运行
**A:** 
- 确保所有依赖文件都在 `dist/XAUUSD_AI/` 目录中
- 检查是否有杀毒软件拦截
- 查看控制台错误信息

## 📝 更新日志

### v1.0
- 初始版本发布
- 支持多周期技术分析
- 支持 AI 交易信号生成
- 支持打包为可执行文件

## 📄 许可证

本项目仅供学习和研究使用。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

如有问题或建议，请通过 Issue 反馈。

---

**免责声明**：本工具仅用于技术分析和学习目的，不构成任何投资建议。交易有风险，投资需谨慎。
