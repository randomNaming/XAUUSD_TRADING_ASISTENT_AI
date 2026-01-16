import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate


# ===============================
# Prompt：多周期技术分析（中文）
# ===============================
FEATURE_PROMPT = """你是一名专业的黄金（XAUUSD）交易员，请基于给定的多周期K线与指标进行技术面分析（简体中文）。

【数据输入】
日线 D1：
{daily_data}

4小时 H4：
{h4_data}

1小时 H1：
{h1_data}

30分钟 M30：
{m30_data}

15分钟 M15：
{m15_data}

5分钟 M5：
{m5_data}

【分析要求】
1) 总体市场结构与主导趋势（以D1/H4为主）
2) 关键支撑/阻力（给出具体价位，必须来自数据）
3) 供需区/订单块/FVG/流动性（描述+对应价位必须来自数据）
4) RSI/EMA/ATR 状态解读
5) 多周期共振结论
6) 给出当下偏向：多/空/震荡（并说明原因）

【输出要求】
- 必须使用简体中文
- 不要输出英文，不要中英混合
- 输出尽量简洁、结构化
IMPORTANT：如果输出中出现任何英文，视为无效回答，请重新用简体中文输出完整内容。
"""


# ===============================
# Prompt：交易信号（中文，原策略风格）
# ===============================
TRADING_PROMPT = """你是一名机构级 XAUUSD 交易员。请严格按规则生成交易信号（简体中文）。

【市场上下文（多周期）】
D1：{daily_data}
H4：{h4_data}
H1：{h1_data}
M30：{m30_data}
M15：{m15_data}
M5：{m5_data}

【技术面分析总结】
{technical_features}

【系统计算的预测区间（真实数值，不可改写）】
{forecast_data}

【严格规则（必须执行）】
1) 趋势一致性：D1/H4/H1/M30/M15/M5 至少 4/5 同向才算有效
2) 入场条件（至少满足 3 条，并说明是哪3条）：
   - 关键位附近出现回踩/反弹（支撑阻力/供需区/订单块/FVG，价位必须来自数据）
   - 流动性扫荡（近期摆动高/低附近）
   - 执行周期出现BOS/结构确认（用简洁语言描述）
   - RSI(14) 背离/极值配合（来自数据）
   - M5 出现明确K线形态确认（吞没/针形/内包等）
3) 风控：
   - 最大风险：1%（描述即可）
   - 止损：1.5x ATR 越过结构位（ATR来自数据）
   - 最小RR 1:2（理想1:3）
   - 点差过大则不交易（如无法获取点差则提示“无法确认点差”）

【输出格式（必须严格）】
交易信号：买入/卖出/不交易
理由（要点列表）：
入场区间：xxx ~ xxx
止损SL：xxx
止盈TP1：xxx
止盈TP2：xxx
止盈TP3：xxx（可选）
执行条件：写清楚触发条件（例如“回踩xxx后M5收阳吞没”）
无效条件：写清楚否定条件（例如“H1收盘跌破xxx”）
风险提示：1-3条
置信度：0-100（并说明依据，必须引用上面规则/多周期/ATR区间）

【输出要求】
- 必须使用简体中文
- 不允许编造任何未在数据/预测区间/关键位中出现的价格
IMPORTANT：如果输出中出现任何英文，视为无效回答，请重新用简体中文输出完整内容。
"""


# ===============================
# Prompt：当日行情分析（含入场点位，中文，价格不可编造）
# ===============================
DAILY_BRIEF_PROMPT = """你是一名专业的黄金（XAUUSD）日内交易员，请基于【给定真实数据】生成“当天行情分析 + 入场点位 + 技术面分析”的中文报告。

【硬性规则（必须执行）】
- 只能使用我提供的数据里的价格数字（今日/昨日/摆动高低/支撑阻力/ATR预测区间/当前价），不得编造任何价格。
- 入场点位必须落在：关键位附近 或 预测区间内，并说明触发条件。
- 若条件不足：必须输出“不交易”，并指出具体缺失项（例如趋势不一致、缺少结构确认等）。
- 必须使用简体中文，不要输出英文，不要中英混合。

【输入数据】
1) 今日行情快照：
{today_snapshot}

2) 昨日关键位：
{yesterday_levels}

3) H1摆动高低（真实数值）：
{h1_swings}

4) 多周期最后状态（真实数值，含 RSI/EMA/ATR）：
{tf_last_state}

5) 预测区间（ATR计算，真实数值）：
{forecast_data}

【输出格式（必须严格按此结构）】
一、今日概览
- 当前价格：xxx（上涨/下跌x%）
- 今日：开xxx / 高xxx / 低xxx / 现xxx；今日振幅xxx；点差xxx（如有）

二、技术面分析（简明）
- D1：趋势/结构 + EMA/RSI结论
- H4：结构/关键区
- H1：当前段走势 + 是否超买超卖
- M15/M5：入场时机（是否出现反转/延续条件）

三、关键价位（必须给数字）
- 今日高/低：xxx / xxx
- 昨日高/低/收：xxx / xxx / xxx
- H1最近摆动高/低：xxx / xxx
- 关键阻力：xxx、xxx
- 关键支撑：xxx、xxx

四、交易计划（必须给 2 套方案）
方案A（回踩/反弹）
- 方向：做多/做空/不交易
- 入场区间：xxx ~ xxx
- 止损SL：xxx
- 止盈TP1/TP2：xxx / xxx
- 触发条件：
- 无效条件：

方案B（突破/破位）
- 方向：做多/做空/不交易
- 入场：xxx
- SL/TP：xxx / xxx
- 触发条件：
- 无效条件：

五、风险提示（1-3条）

最后：置信度（0-100）+ 依据（必须引用多周期一致性、关键位、ATR区间、结构确认等）
IMPORTANT：如果输出中出现任何英文，视为无效回答，请重新用简体中文输出完整内容。
"""


# ===============================
# 计算工具
# ===============================
def forecast_range(close: float, atr: float, k: float):
    if atr is None or atr <= 0 or np.isnan(atr):
        return None
    return round(close - k * atr, 2), round(close + k * atr, 2)


def _today_start_local() -> datetime:
    now = datetime.now()
    return now.replace(hour=0, minute=0, second=0, microsecond=0)


def _safe_float(x, nd=2):
    try:
        v = float(x)
        if np.isnan(v):
            return None
        return round(v, nd)
    except Exception:
        return None


class XAUUSDTradingBot:
    def __init__(self, api_key: str):
        self.llm = ChatOpenAI(
            model="gpt-4.1",
            temperature=0.05,
            api_key=api_key,
        )

        self.feature_chain = PromptTemplate(
            template=FEATURE_PROMPT,
            input_variables=["daily_data", "h4_data", "h1_data", "m30_data", "m15_data", "m5_data"],
        ) | self.llm

        self.trading_chain = PromptTemplate(
            template=TRADING_PROMPT,
            input_variables=["daily_data", "h4_data", "h1_data", "m30_data", "m15_data", "m5_data", "technical_features", "forecast_data"],
        ) | self.llm

        self.daily_chain = PromptTemplate(
            template=DAILY_BRIEF_PROMPT,
            input_variables=["today_snapshot", "yesterday_levels", "h1_swings", "tf_last_state", "forecast_data"],
        ) | self.llm

        self.timeframes = {
            "D1": mt5.TIMEFRAME_D1,
            "H4": mt5.TIMEFRAME_H4,
            "H1": mt5.TIMEFRAME_H1,
            "M30": mt5.TIMEFRAME_M30,
            "M15": mt5.TIMEFRAME_M15,
            "M5": mt5.TIMEFRAME_M5,
        }

        # ATR区间系数（短线+波段）
        self.k_map = {
            "M5": 1.0,   # ~30分钟参考
            "M15": 1.2,  # ~2小时参考
            "M30": 1.5,
            "H1": 2.0,   # ~4小时参考
            "H4": 2.5,
            "D1": 3.0,   # ~1天参考
        }

    # ===== MT5 =====
    def initialize_mt5(self):
        if not mt5.initialize():
            raise RuntimeError(f"MT5 初始化失败：{mt5.last_error()}")

    def shutdown_mt5(self):
        mt5.shutdown()

    # ===== 指标 =====
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        df["ema_20"] = df["close"].ewm(span=20, adjust=False).mean()
        df["ema_50"] = df["close"].ewm(span=50, adjust=False).mean()
        df["ema_200"] = df["close"].ewm(span=200, adjust=False).mean()

        delta = df["close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        rs = gain.rolling(14).mean() / loss.rolling(14).mean()
        df["rsi"] = 100 - (100 / (1 + rs))

        prev_close = df["close"].shift(1)
        tr = pd.concat(
            [
                (df["high"] - df["low"]),
                (df["high"] - prev_close).abs(),
                (df["low"] - prev_close).abs(),
            ],
            axis=1,
        ).max(axis=1)
        df["atr"] = tr.rolling(14).mean()

        return df

    # ===== 数据拉取 =====
    def fetch_rates_range(self, symbol: str, timeframe, start: datetime, end: datetime) -> pd.DataFrame | None:
        rates = mt5.copy_rates_range(symbol, timeframe, start, end)
        if rates is None or len(rates) == 0:
            return None
        df = pd.DataFrame(rates)
        df["time"] = pd.to_datetime(df["time"], unit="s")
        return df

    def get_df(self, symbol: str, tf_name: str, days_back: int = 60) -> pd.DataFrame | None:
        end = datetime.now()
        start = end - timedelta(days=days_back)
        df = self.fetch_rates_range(symbol, self.timeframes[tf_name], start, end)
        if df is None or df.empty:
            return None
        return self.calculate_indicators(df)

    # ===== 文本格式化 =====
    def prepare_data_string(self, df: pd.DataFrame, tf_name: str, n: int = 10) -> str:
        recent = df.tail(n)
        lines = [f"最近{n}根 {tf_name} K线（含指标）："]
        for _, row in recent.iterrows():
            lines.append(
                f"时间:{row['time']} "
                f"O:{row['open']:.2f} H:{row['high']:.2f} L:{row['low']:.2f} C:{row['close']:.2f} "
                f"RSI:{row.get('rsi', np.nan):.2f} EMA20:{row.get('ema_20', np.nan):.2f} EMA50:{row.get('ema_50', np.nan):.2f} "
                f"EMA200:{row.get('ema_200', np.nan):.2f} ATR:{row.get('atr', np.nan):.2f}"
            )
        return "\n".join(lines)

    # ===== 今日快照 =====
    def get_today_snapshot(self, symbol: str) -> dict | None:
        start = _today_start_local()
        end = datetime.now()
        df = self.fetch_rates_range(symbol, mt5.TIMEFRAME_M5, start, end)
        if df is None or df.empty:
            return None
        o = float(df.iloc[0]["open"])
        h = float(df["high"].max())
        l = float(df["low"].min())
        last = float(df.iloc[-1]["close"])
        chg_pct = (last - o) / o * 100 if o else 0.0
        amp = h - l
        return {
            "date": start.strftime("%Y-%m-%d"),
            "open": round(o, 2),
            "high": round(h, 2),
            "low": round(l, 2),
            "last": round(last, 2),
            "change_pct": round(chg_pct, 2),
            "range": round(amp, 2),
        }

    def get_yesterday_levels(self, symbol: str) -> dict | None:
        rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_D1, 0, 5)
        if rates is None or len(rates) < 2:
            return None
        df = pd.DataFrame(rates)
        # 通常最后一根为今天未收盘日线，倒数第二根为昨天
        y = df.iloc[-2]
        return {
            "y_high": round(float(y["high"]), 2),
            "y_low": round(float(y["low"]), 2),
            "y_close": round(float(y["close"]), 2),
        }

    def get_current_spread(self, symbol: str) -> int | None:
        info = mt5.symbol_info(symbol)
        if info is None:
            return None
        return int(info.spread)

    def get_h1_swings(self, df_h1: pd.DataFrame, lookback: int = 80) -> tuple[float, float]:
        d = df_h1.tail(lookback)
        return round(float(d["high"].max()), 2), round(float(d["low"].min()), 2)

    def last_state_line(self, df: pd.DataFrame, name: str) -> str:
        last = df.iloc[-1]
        return (
            f"{name}: close={last['close']:.2f}, RSI={_safe_float(last.get('rsi'),1)}, "
            f"EMA20={_safe_float(last.get('ema_20'))}, EMA50={_safe_float(last.get('ema_50'))}, EMA200={_safe_float(last.get('ema_200'))}, "
            f"ATR={_safe_float(last.get('atr'))}"
        )

    # ===== 主流程 =====
    def run_analysis(self, symbol: str = "XAUUSD") -> dict:
        self.initialize_mt5()
        try:
            # 1) 拉取多周期
            dfs: dict[str, pd.DataFrame] = {}
            market_data_str: dict[str, str] = {}

            for tf_name in ["D1", "H4", "H1", "M30", "M15", "M5"]:
                df = self.get_df(symbol, tf_name, days_back=120)
                if df is None or df.empty:
                    raise RuntimeError(f"{tf_name} 获取数据失败（请确认MT5已登录且品种可用）")
                dfs[tf_name] = df
                market_data_str[tf_name] = self.prepare_data_string(df, tf_name, n=10)

            # 2) 系统预测区间（真实数值）
            forecast_lines = []
            for tf_name, df in dfs.items():
                last = df.iloc[-1]
                fr = forecast_range(float(last["close"]), float(last["atr"]), self.k_map.get(tf_name, 1.0))
                if fr:
                    forecast_lines.append(f"{tf_name} 预测区间：{fr[0]} ~ {fr[1]}（ATR={float(last['atr']):.2f}，k={self.k_map.get(tf_name,1.0)}）")
            forecast_text = "\n".join(forecast_lines) if forecast_lines else "预测区间：暂无（ATR不足或数据不足）"

            # 3) 特征分析（LLM）
            features = self.feature_chain.invoke({
                "daily_data": market_data_str["D1"],
                "h4_data": market_data_str["H4"],
                "h1_data": market_data_str["H1"],
                "m30_data": market_data_str["M30"],
                "m15_data": market_data_str["M15"],
                "m5_data": market_data_str["M5"],
            })
            technical_features = features.content if hasattr(features, "content") else str(features)

            # 4) 交易信号（LLM）
            signal = self.trading_chain.invoke({
                "daily_data": market_data_str["D1"],
                "h4_data": market_data_str["H4"],
                "h1_data": market_data_str["H1"],
                "m30_data": market_data_str["M30"],
                "m15_data": market_data_str["M15"],
                "m5_data": market_data_str["M5"],
                "technical_features": technical_features,
                "forecast_data": forecast_text,
            })
            trading_signal = signal.content if hasattr(signal, "content") else str(signal)

            # 5) 当日快照 + 昨日关键位 + H1摆动
            today = self.get_today_snapshot(symbol)
            y = self.get_yesterday_levels(symbol)
            spread = self.get_current_spread(symbol)

            h1_swing_high, h1_swing_low = self.get_h1_swings(dfs["H1"], lookback=80)

            today_snapshot_text = "今日快照：无法获取"
            if today:
                direction = "上涨" if today["change_pct"] >= 0 else "下跌"
                today_snapshot_text = (
                    f"日期：{today['date']}\n"
                    f"当前价格：{today['last']}（{direction}{abs(today['change_pct'])}%）\n"
                    f"今日开/高/低/现：{today['open']} / {today['high']} / {today['low']} / {today['last']}\n"
                    f"今日振幅：{today['range']}\n"
                    f"点差：{spread if spread is not None else '无法获取'}"
                )

            yesterday_text = "昨日关键位：无法获取"
            if y:
                yesterday_text = f"昨日高/低/收：{y['y_high']} / {y['y_low']} / {y['y_close']}"

            h1_swings_text = f"H1最近摆动高/低：{h1_swing_high} / {h1_swing_low}"

            tf_last_state = "\n".join([
                self.last_state_line(dfs["D1"], "D1"),
                self.last_state_line(dfs["H4"], "H4"),
                self.last_state_line(dfs["H1"], "H1"),
                self.last_state_line(dfs["M30"], "M30"),
                self.last_state_line(dfs["M15"], "M15"),
                self.last_state_line(dfs["M5"], "M5"),
            ])

            # 6) 当日行情分析（LLM：含入场点位）
            daily = self.daily_chain.invoke({
                "today_snapshot": today_snapshot_text,
                "yesterday_levels": yesterday_text,
                "h1_swings": h1_swings_text,
                "tf_last_state": tf_last_state,
                "forecast_data": forecast_text,
            })
            daily_brief = daily.content if hasattr(daily, "content") else str(daily)

            return {
                "timestamp": datetime.now().isoformat(),
                "symbol": symbol,
                "current_spread": spread,
                "today_snapshot": today,
                "forecast": forecast_text,
                "market_data": market_data_str,           # 各周期最近10根K线文本
                "technical_features": technical_features, # LLM技术分析
                "trading_signal": trading_signal,         # LLM交易信号
                "daily_brief": daily_brief,               # LLM当日行情分析+入场
            }

        finally:
            self.shutdown_mt5()
