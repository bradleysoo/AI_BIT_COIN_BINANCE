import ccxt
import pandas as pd
import json


def get_chart():
    exchange = ccxt.binance({"options": {"defaultType": "future"}})  # 선물거래소

    one_five_min_term = exchange.fetch_ohlcv(
        "BTC/USDT", timeframe="15m", limit=96
    )  ## BTC/USDT 15분봉 96

    one_five_min_df = pd.DataFrame(
        one_five_min_term,
        columns=["timestamp", "open", "high", "low", "close", "volume"],
    )
    one_five_min_df["timestamp"] = pd.to_datetime(
        one_five_min_df["timestamp"], unit="ms"
    )
    one_five_min_df.set_index("timestamp", inplace=True)

    hour_term = exchange.fetch_ohlcv(
        "BTC/USDT", timeframe="1h", limit=24
    )  ## BTC/USDT 1시간봉  24

    hour_df = pd.DataFrame(
        hour_term, columns=["timestamp", "open", "high", "low", "close", "volume"]
    )
    hour_df["timestamp"] = pd.to_datetime(hour_df["timestamp"], unit="ms")
    hour_df.set_index("timestamp", inplace=True)

    data_payload = {
        "15-minute chart": json.loads(one_five_min_df.to_json(orient="index")),
        "1-hour chart": json.loads(hour_df.to_json(orient="index")),
    }  ##데이터 json 화

    data_payload_string = json.dumps(data_payload, indent=2)  ##json -> text

    return data_payload_string
