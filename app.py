import streamlit as st
import pandas as pd
import finnhub
import time

# ✅ 页面设置必须放最前
st.set_page_config(page_title="纳斯达克 AI 股票评分系统", layout="wide")

# 🔑 你的 API Key
API_KEY = "d0cd9phr01ql2j3cdddgd0cd9phr01ql2j3cdde0"
client = finnhub.Client(api_key=API_KEY)

# 🧠 定义 AI 打分函数（你可以自定义逻辑）
def compute_score(quote):
    # 简单评分模型（仅作示范）：当前价格跌幅越大、成交额越大，得分越高
    score = 100
    if quote["dp"] is not None:
        score += -quote["dp"]  # 跌幅越大得分越高
    if quote["c"] is not None and quote["o"] is not None:
        change = quote["c"] - quote["o"]
        score += change * 2
    return round(score, 2)

# 🚀 页面 UI
st.title("📈 纳斯达克 AI 股票评分系统（实时数据）")
tickers_input = st.text_input("请输入股票代码（英文逗号分隔，例如 AAPL,TSLA,NVDA）", "AAPL,TSLA,NVDA,AMZN,MSFT,META")

tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]

rows = []
for ticker in tickers:
    try:
        quote = client.quote(ticker)
        score = compute_score(quote)
        recommend = "Buy" if score >= 75 else "Hold" if score >= 50 else "Sell"

        rows.append({
            "ticker": ticker,
            "score": score,
            "recommend": recommend,
            "current_price": quote["c"],
            "open": quote["o"],
            "high": quote["h"],
            "low": quote["l"],
            "prev_close": quote["pc"],
            "change(%)": quote["dp"]
        })

    except Exception as e:
        st.warning(f"❌ {ticker} 数据获取失败：{e}")

# 📊 显示表格
if rows:
    df = pd.DataFrame(rows)
    
    # ✅ 可选过滤器
    filter_buy = st.checkbox("✅ 只显示推荐为 Buy 的股票")
    if filter_buy:
        df = df[df["recommend"] == "Buy"]

    st.dataframe(df.sort_values("score", ascending=False), use_container_width=True)
else:
    st.warning("未获取到有效数据，请检查股票代码是否正确。")
