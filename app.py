st.write(client.quote("AAPL"))
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import finnhub
import pandas as pd
import time

# ----------------------------
# 页面配置
# ----------------------------
st.set_page_config(page_title="纳斯达克AI评分仪表盘", layout="wide")
st_autorefresh(interval=60000, key="realtime_refresh")  # 每60秒自动刷新一次页面

# ----------------------------
# 用户设置
# ----------------------------
API_KEY = "d0q0or1r01qmj4nhbb7gd0q0or1r01qmj4nhbb80"  # ←←← 改成你自己的 Finnhub API Key
client = finnhub.Client(api_key=API_KEY)

tickers = st.text_input("请输入股票代码（英文逗号分隔，例如 AAPL,TSLA,NVDA）", value="AAPL,TSLA,NVDA,AMZN,MSFT,META").upper()
tickers = [t.strip() for t in tickers.split(",") if t.strip()]

# ----------------------------
# 数据处理函数
# ----------------------------
def get_data(ticker):
    try:
        quote = client.quote(ticker)
        sentiment = client.news_sentiment(ticker)
        basic = client.company_basic_financials(ticker, 'all')

        price = quote.get("c", 0)
        moneyflow = quote.get("v", 0) * price  # 成交额

        pe = basic['metric'].get("peInclExtraTTM", None)
        ps = basic['metric'].get("psTTM", None)
        eps_growth = basic['metric'].get("epsGrowth", None)
        news_score = sentiment.get("companyNewsScore", None)

        score = 0
        if price > 0:
            score += (1 / pe) * 20 if pe else 0
            score += (1 / ps) * 10 if ps else 0
            score += eps_growth * 30 if eps_growth else 0
            score += news_score * 40 if news_score else 0

        recommend = "Buy" if score >= 75 else "Hold" if score >= 50 else "Sell"

        return {
            "ticker": ticker,
            "score": round(score, 2),
            "recommend": recommend,
            "pe": round(pe, 4) if pe else None,
            "ps": round(ps, 4) if ps else None,
            "rsi": None,
            "eps_growth": round(eps_growth, 3) if eps_growth else None,
            "moneyflow": moneyflow,
            "news_sentiment": round(news_score, 4) if news_score else None
        }
    except Exception as e:
        return None

# ----------------------------
# 实时显示
# ----------------------------
rows = []
for t in tickers:
    row = get_data(t)
    if row:
        rows.append(row)

if rows:
    df = pd.DataFrame(rows)
    df = df.sort_values("score", ascending=False)

    st.checkbox("✅ 只显示推荐为 Buy 的股票", value=False, key="filter_buy", help="仅显示推荐买入的股票")
    if st.session_state.filter_buy:
        df = df[df["recommend"] == "Buy"]

    st.dataframe(df, use_container_width=True)
else:
    st.warning("未获取到有效数据，请检查股票代码是否正确。")
