import streamlit as st
import finnhub
import pandas as pd
import time

# ⚙️ 页面设置（必须放在最前面）
st.set_page_config(page_title="纳斯达克AI评分仪表盘", layout="wide")

# 📡 初始化客户端（API Key 记得替换）
api_key = "d0cd9phr01ql2j3cdddgd0cd9phr01ql2j3cdde0"
client = finnhub.Client(api_key=api_key)

# 🎯 打分模型
def compute_score(pe, ps, rsi, eps_growth, moneyflow, sentiment):
    score = 0
    if pe and pe < 25: score += 15
    if ps and ps < 5: score += 10
    if rsi and rsi < 40: score += 10
    if eps_growth and eps_growth > 0: score += 15
    if moneyflow and moneyflow > 1e9: score += 15
    if sentiment and sentiment > 0.3: score += 10
    return round(score, 2)

def get_recommendation(score):
    if score >= 70:
        return "Buy"
    elif score >= 50:
        return "Hold"
    else:
        return "Sell"

# 📝 用户输入
st.title("📉 纳斯达克 AI 股票评分系统（实时数据）")
tickers_input = st.text_input("请输入股票代码（英文逗号分隔，例如 AAPL,TSLA,NVDA）", "AAPL,TSLA,NVDA,AMZN,MSFT,META")
ticker_list = [x.strip().upper() for x in tickers_input.split(",") if x.strip()]

# ✅ 只看 Buy 股票
show_buy_only = st.checkbox("✅ 只显示推荐为 Buy 的股票", value=True)

# 📊 数据准备
data = []

for ticker in ticker_list:
    try:
        q = client.quote(ticker)
        m = client.company_basic_financials(ticker, 'all')
        s = client.stock_social_sentiment(ticker, _from='2024-01-01', to='2025-12-31')

        pe = m['metric'].get('peInclExtraTTM')
        ps = m['metric'].get('psTTM')
        eps_growth = m['metric'].get('epsGrowth')
        rsi = m['metric'].get('rsi')
        sentiment = s['reddit'][0]['score'] if s.get('reddit') else 0
        moneyflow = q['c'] * q['v'] if q.get('c') and q.get('v') else 0

        score = compute_score(pe, ps, rsi, eps_growth, moneyflow, sentiment)
        recommendation = get_recommendation(score)

        row = {
            "ticker": ticker,
            "score": score,
            "recommend": recommendation,
            "pe": pe,
            "ps": ps,
            "rsi": rsi,
            "eps_growth": eps_growth,
            "moneyflow": round(moneyflow, 2),
            "news_sentiment": sentiment
        }
        data.append(row)

    except Exception as e:
        st.warning(f"❌ 无法获取 {ticker} 的数据，错误: {e}")

# 📈 表格展示
df = pd.DataFrame(data)

if show_buy_only:
    df = df[df["recommend"] == "Buy"]

st.dataframe(df, use_container_width=True)
