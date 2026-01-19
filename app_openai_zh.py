import streamlit as st
from datetime import datetime
import time
import os

from XAUSD_AI_openai_zh import XAUUSDTradingBot

# 必须最先调用
st.set_page_config(page_title="XAUUSD 交易助手", page_icon="📈", layout="wide")

# 深色背景 + 白字（清晰）
st.markdown("""
<style>
.stApp { background-color:#0e1117; color:#ffffff; }
html, body, [class*="css"] { color:#ffffff !important; }
.stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown span { color:#ffffff !important; }
h1,h2,h3,h4,h5,h6 { color:#ffffff !important; }
section[data-testid="stSidebar"] { background-color:#111827; }
section[data-testid="stSidebar"] * { color:#ffffff !important; }
</style>
""", unsafe_allow_html=True)

st.title("🤖 XAUUSD 当日行情分析（含入场点位）")

# 优先从环境变量读取API密钥，其次从secrets读取
def get_api_key():
    """获取OpenAI API密钥，优先级：环境变量 > secrets文件"""
    # 1. 尝试从环境变量获取
    api_key = os.environ.get('OPENAI_API_KEY', '').strip()
    if api_key:
        return api_key
    
    # 2. 尝试从secrets获取
    try:
        api_key = st.secrets.get("OPENAI_API_KEY", "").strip()
        if api_key:
            return api_key
    except Exception:
        pass
    
    # 3. 无法获取API密钥
    return None

api_key = get_api_key()
if not api_key:
    st.error("""
    ❌ **缺少 OpenAI API Key！**
    
    请按以下步骤配置：
    1. 打开程序目录下的 `config.bat` 文件
    2. 在 `OPENAI_API_KEY` 后填写您的 API Key
    3. 保存后重新启动程序
    
    如果您还没有 API Key，请访问：https://platform.openai.com/api-keys
    """)
    st.stop()

bot = XAUUSDTradingBot(api_key=api_key)


def display_market_data(data_str, timeframe):
    with st.expander(f"📊 {timeframe} 市场数据（最近10根）", expanded=False):
        for line in data_str.split("\n"):
            if line.strip():
                st.text(line)


def main():
    with st.sidebar:
        st.header("🎛 控制面板")
        auto_refresh = st.toggle("🔄 自动刷新（30分钟）", value=False)

        if st.button("🚀 运行新分析"):
            with st.spinner("分析中（拉取MT5数据 + GPT生成报告）..."):
                st.session_state["analysis_result"] = bot.run_analysis(symbol="XAUUSD")
                st.session_state["last_update"] = datetime.now()

        if "analysis_result" in st.session_state:
            r = st.session_state["analysis_result"]
            if r.get("current_spread") is not None:
                st.metric("当前点差", f"{r['current_spread']} points")

        if "last_update" in st.session_state:
            st.info(f"最后更新时间：{st.session_state['last_update'].strftime('%Y-%m-%d %H:%M:%S')}")

    if "analysis_result" not in st.session_state:
        st.warning("⚠️ 还没有分析结果，请点击左侧「运行新分析」。")
        return

    result = st.session_state["analysis_result"]

    # 顶部：今日快照（真实数据）
    snap = result.get("today_snapshot")
    if snap:
        direction = "上涨" if snap["change_pct"] >= 0 else "下跌"
        st.markdown(
            f"**当前价格：{snap['last']} 美元/盎司，{direction}{abs(snap['change_pct'])}%**  \n"
            f"**今日开盘：{snap['open']}  | 今日最高：{snap['high']}  | 今日最低：{snap['low']}  | 今日振幅：{snap['range']}**"
        )
    else:
        st.warning("未获取到今日快照数据（请确认 MT5 已登录且 XAUUSD 可用）")

    tab0, tab1, tab2, tab3, tab4 = st.tabs(["🗓 今日行情", "🎯 入场点位", "📊 技术分析", "📈 预测区间", "📊 多周期数据"])

    with tab0:
        st.subheader("🗓 当天行情分析（包含技术面结论）")
        st.markdown(result.get("daily_brief", "暂无"))

    with tab1:
        st.subheader("🎯 交易信号（入场/止损/止盈）")
        st.markdown(result.get("trading_signal", "暂无"))

    with tab2:
        st.subheader("📊 多周期技术分析（结构/支撑阻力/供需/指标）")
        st.markdown(result.get("technical_features", "暂无"))

    with tab3:
        st.subheader("📈 预测区间（系统基于ATR计算）")
        st.code(result.get("forecast", "暂无"))

    with tab4:
        st.subheader("📊 各周期最近10根K线（含RSI/EMA/ATR）")
        cols = st.columns(2)
        for idx, (tf, data) in enumerate(result.get("market_data", {}).items()):
            with cols[idx % 2]:
                display_market_data(data, tf)

    # 自动刷新
    with st.sidebar:
        auto_refresh = st.session_state.get("auto_refresh_state", False)

    # 让 toggle 状态可持久化（避免切tab丢）
    # 如果你不需要可以删
    # （这里不强制）
    # auto_refresh 只在 sidebar 中有效，所以我们简单重取一次即可

    # 若开启自动刷新：30分钟 rerun
    if st.sidebar and st.session_state.get("analysis_result") is not None:
        # 重新读取 toggle（Streamlit 每次都会重新执行脚本）
        # 保持跟 sidebar 一致
        pass

    # 这里沿用最简单的：如果用户开启 Auto Refresh，就显示倒计时并到点刷新
    with st.sidebar:
        auto_refresh = st.toggle("🔄 自动刷新（30分钟）", value=False, key="auto_refresh_toggle")

        if auto_refresh:
            current_time = datetime.now()
            if "last_refresh" not in st.session_state:
                st.session_state["last_refresh"] = current_time

            time_diff = (current_time - st.session_state["last_refresh"]).total_seconds()
            remaining_time = 1800 - time_diff

            if remaining_time > 0:
                progress = (1800 - remaining_time) / 1800
                mins = int(remaining_time // 60)
                secs = int(remaining_time % 60)
                st.progress(progress, text=f"下次刷新：{mins:02d}:{secs:02d}")

            if time_diff >= 1800:
                st.session_state["last_refresh"] = current_time
                time.sleep(1)
                st.rerun()


if __name__ == "__main__":
    main()
