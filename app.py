import streamlit as st
import finnhub-python
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# 设置页面布局
st.set_page_config(page_title="纳斯达克AI实时评分仪表盘", layout="wide")

# 每60秒自动刷新页面
st_autorefresh(interval=60 * 1000, key="refresh")

# 设置 Finnhub API
finnhub_client = finnhub.Client(api_key="d0cd9phr01ql2j3cdddgd0cd9phr01ql2j3cdde0")

st.title("📈 纳斯达克 AI 实时股票评分系统")

tickers_input = st.text_input("请输入股票代码（英文逗号分隔）", "AAPL,TSLA,NVDA,AMZN,MSFT,META")
tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]

@st.cache_data(ttl=30)
def get_realtime_quote(ticker):
    try:
        q = finnhub_client.quote(ticker)
        return {
            "ticker": ticker,
            "price": q["c"],
            "prev_close": q["pc"],
            "high": q["h"],
            "low": q["l"],
            "change_pct": round((q["c"] - q["pc"]) / q["pc"] * 100, 2) if q["pc"] else 0
        }
    except:
        return None

def score(row):
    # 简化评分逻辑：涨幅 + 当前价权重
    score = 0
    score += max(min(row['change_pct'], 10), -10) + row['price'] / 10
    return round(score, 2)

rows = []
for t in tickers:
    data = get_realtime_quote(t)
    if data:
        rows.append(data)

if rows:
    df = pd.DataFrame(rows)
    df["score"] = df.apply(score, axis=1)
    df["recommend"] = df["score"].apply(lambda x: "Buy" if x >= 75 else ("Hold" if x >= 50 else "Sell"))

    filter_buy = st.checkbox("✅ 只显示推荐为 Buy 的股票")
    if filter_buy:
        df = df[df["recommend"] == "Buy"]

    st.dataframe(df[["ticker", "price", "change_pct", "score", "recommend"]]
                 .sort_values("score", ascending=False),
                 use_container_width=True)
else:
    st.warning("未获取到实时数据，请检查股票代码或稍后重试。")
    # force redeploy

