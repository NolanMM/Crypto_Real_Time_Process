import streamlit as st
import pandas as pd
import numpy as np
import re
from dotenv import load_dotenv
import os
from alpha_vantage.fundamentaldata import FundamentalData
from stocknews import StockNews
import yfinance as yf
import plotly.express as px

load_dotenv(override=True)

alpha_vantage_api = os.getenv("ALPHAVANTAGE_API")

st.set_page_config(
    page_title="Streamlit App",
    page_icon=":shark:",
    layout="wide",
)

st.markdown("""
    <style>
    .main {
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    .block-container {
        text-align: center;
        width: 100%;
        max-width: 1800px;
        margin: 0 auto;
    }
    .chart-container {
        width: 100%;
        display: flex;
        justify-content: flex-start;
    }
    h1 {
        text-align: center;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("Streamlit App")

text_input = st.sidebar.text_input("Ticker")

pattern = re.compile(r"^[A-Z]{1,5}$")

startdate = st.sidebar.date_input("Select start date")
enddate = st.sidebar.date_input("Select end date")

if st.sidebar.button("Submit"):
    if re.match(pattern, text_input):
        data = yf.download(text_input, start=startdate, end=enddate)

        realtime_data, summary_stats, pricing, fundamentals_data, news = st.tabs(["Real Time Data","Summary Statistic","Pricing", "Fundamentals", "Top News"])

        with realtime_data:
            st.header("Real Time Data")
            st.write(data.tail())

        with summary_stats:
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Adj Close Price Over Time")
                fig = px.line(data, x=data.index, y=data["Adj Close"], title=text_input)
                #fig.update_layout(width=1000, height=500)
                st.plotly_chart(fig)
            
            with col2:
                st.subheader("Volume Over Time")
                fig = px.line(data, x=data.index, y=data["Volume"], title=text_input)
                #fig.update_layout(width=1000, height=500)
                st.plotly_chart(fig)
            
            st.subheader("Moving Average")
            num_days = st.slider("Select number of days", min_value=5, max_value=200)

            Moving_Average_Chart = st.empty()
            ## Fixing Later
            Moving_Average_Chart.line_chart(data["Adj Close"].rolling(window=num_days).mean())


        with pricing:
            st.header("Price Movement")
            data_ = data.copy()
            
            data_["% Change"] = data_["Adj Close"] / data_["Adj Close"].shift(1) - 1
            data_.dropna(inplace=True)
            st.write(data_)
            annual_returns = data_["% Change"].mean() * 252 * 100
            st.write(f"Annual Returns: {annual_returns:.2f}%")
            std_ = np.std(data_["% Change"]) * np.sqrt(252) * 100
            st.write(f"Standard Deviation: {std_:.2f} %")
            st.write("Risk Adjusted Returns: ", annual_returns / std_)


        with fundamentals_data:
            fd = FundamentalData(key=alpha_vantage_api, output_format="pandas")
            st.subheader("Balance Sheet")
            balance_sheet = fd.get_balance_sheet_annual(text_input)[0]
            balance_sheet_ = balance_sheet.T[2:]
            balance_sheet_.columns = list(balance_sheet_.iloc[0])
            st.write(balance_sheet_)

            st.subheader("Income Statement")
            income_statement = fd.get_income_statement_annual(text_input)[0]
            income_statement_ = income_statement.T[2:]
            income_statement_.columns = list(income_statement_.iloc[0])
            st.write(income_statement_)

            st.subheader("Cash Flow")
            cash_flow = fd.get_cash_flow_annual(text_input)[0]
            cash_flow_ = cash_flow.T[2:]
            cash_flow_.columns = list(cash_flow_.iloc[0])
            st.write(cash_flow_)    


        with news:
            st.header("Top News")
            sn = StockNews(text_input, save_news=False)
            df_news = sn.read_rss()
            for i in range(10):
                st.subheader(df_news["title"][i])
                st.write(df_news["published"][i])
                st.write(df_news["summary"][i])
                title_sentiment = df_news["sentiment_title"][i]
                st.write(f"Title Sentiment: {title_sentiment}")
                news_sentiment = df_news["sentiment_summary"][i]
                st.write(f"News Sentiment: {news_sentiment}")

    else:
        st.error("Text input does not match the required format (AAPL)")




    