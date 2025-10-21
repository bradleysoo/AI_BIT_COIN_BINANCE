import os
from dotenv import load_dotenv
import pandas as pd
import ccxt

load_dotenv()

print(os.getenv("BINACE_ACCESS_API_KEY"))
print(os.getenv("BINACE_SECRET_API_KEY"))
print(os.getenv("GEMINI_API_KEY"))


exchange = ccxt.binance({"options": {"defaultType": "future"}})  # 선물거래소

ohlcv = exchange.fetch_ohlcv(
    "BTC/USDT", timeframe="1d", limit=96
)  ## BTC/USDT 15분봉 96개 가져옴
df = pd.DataFrame(
    ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"]
)
df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
print(df)
