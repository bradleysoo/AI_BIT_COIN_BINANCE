import ccxt
import pandas as pd 

exchange = ccxt.binance({
    'options': {
        'defaultType': 'future'  # 선물거래소
    }
})

ohlcv = exchange.fetch_ohlcv('BTC/USDT' , timeframe='1d',limit=96) ## BTC/USDT 15분봉 96개 가져옴 
df=pd.DataFrame(ohlcv,columns=['timestamp','open','high','low','close','volume'])
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
print(df)