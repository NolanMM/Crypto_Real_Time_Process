from alpha_vantage.timeseries import TimeSeries
from dotenv import load_dotenv
import os

load_dotenv(override=True)

api_key = os.getenv("ALPHAVANTAGE_API")

ts = TimeSeries(key=api_key, output_format="pandas")

data = ts.get_monthly_adjusted("AAPL")

# Get Intraday data
# data = ts.get_intraday("AAPL", interval="5min", outputsize="full")

# Get The Fundamentals Data
from alpha_vantage.fundamentaldata import FundamentalData

fd = FundamentalData(key=api_key, output_format="pandas")