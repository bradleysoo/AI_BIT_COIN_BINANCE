import os
from dotenv import load_dotenv
import pandas as pd
import ccxt
import pprint

load_dotenv()

# print(os.getenv("BINACE_ACCESS_API_KEY"))
# print(os.getenv("BINACE_SECRET_API_KEY"))
# print(os.getenv("GEMINI_API_KEY"))


# 바이 낸스 셋팅
access = os.getenv("BINANCE_ACCESS_API_KEY")
secret = os.getenv("BINANCE_SECRET_API_KEY")
exchange = ccxt.binance(
    {
        "apiKey": access,
        "secret": secret,
        "enableRateLimit": True,
        "options": {"defaultType": "future", "adjustForTimeDifference": True},
    }
)


symbol = "BTC/USDT"
positions = exchange.fetch_positions(symbols=[symbol])
pprint.pprint(positions)
