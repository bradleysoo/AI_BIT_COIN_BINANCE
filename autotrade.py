import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
import google.generativeai as genai
from ai_analysis import *
import time


def execute_trading():
    # conn=init_db()## DB연결

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

    # 레버리지 셋팅 난 무조건 저배율
    symbol = "BTC/USDT"
    leverage = 2
    margin = "ISOLATED"
    exchange.set_leverage(leverage, symbol)
    exchange.set_margin_mode(margin, symbol)
    print(f"{symbol} 레버리지 {leverage}배 설정")

    while True:
        try:
            # 현재 시간 및 가격 조회
            current_time = datetime.now().strftime("%H:%M:%S")
            current_btc_price = exchange.fetch_ticker("BTC/USDT")[
                "last"
            ]  ##현재 BTC/USDT 가격 알아옴

            tradeable_btc = current_btc_price * 0.001  # 거래 가능 변수량

            print(f"\n[{current_time}] Current BTC Price: ${current_btc_price:,.2f}")

            # 포지션 확인
            current_side = None  ##현재 포지션 방향을 저장 (long, short, None)
            current_amount = 0
            amt = 0
            positions = exchange.fetch_positions([symbol])  ## 포지션 가져오기
            for position in positions:
                if position["symbol"] == "BTC/USDT:USDT":
                    pnl = float(position["unrealizedPnl"])
                    amt = float(position["info"]["positionAmt"])
                    if amt > 0:
                        current_side = "long"
                        current_amount = amt
                    elif amt < 0:
                        current_side = "short"

            if amt > 0:
                current_side = "long"
                current_amount = amt
            elif amt < 0:
                current_side = "short"
                current_amount = abs(amt)

            # 현재 포지션 출력
            if current_side:
                print(f"Current Position: {current_side.upper()} {current_amount} BTC")
                print(f"Current PNL: {pnl} USDT")

            else:
                # 포지션이 없을 경우, 남아있는 미체결 주문 취소
                try:
                    open_orders = exchange.fetch_open_orders(
                        symbol
                    )  ## 미체결 주문(이전 거래 sl tp) 목록 가져옴
                    if open_orders:
                        for order in open_orders:
                            exchange.cancel_order(order["id"], symbol)
                        print("Cancelled remaining open orders for", symbol)
                    else:
                        print("No remaining open orders to cancel.")
                except Exception as e:
                    print("Error cancelling orders:", e)
                time.sleep(5)
                print("No position. Analyzing market...")

                # # ai 분석 결과 가져오기
                result = ai_analysis()
                # 결과(매수,매도,홀드)
                decision = result["decision"].upper()
                # decision = "LONG"
                # # 이유
                reason = result["reason"]

                current_btc_price = exchange.fetch_ticker("BTC/USDT")[
                    "last"
                ]  ##현재 BTC/USDT 가격 알아옴
                tradeable_btc = current_btc_price * 0.001  # 거래 가능 변수량

                # 사용 가능한 USDT 확인
                balance = exchange.fetch_balance()
                usdt_available = balance["free"]["USDT"]

                # 매수
                if decision == "LONG":

                    # 잔액이 0.001BTC 이상 일때 거래 가능
                    if usdt_available > tradeable_btc:

                        amount = (usdt_available * leverage * 0.995) / current_btc_price
                        # 익절/손절 가격 계산
                        take_profit_price = round(current_btc_price * 1.03, 2)  # +3%
                        stop_loss_price = round(current_btc_price * 0.97, 2)  # -3%

                        # LONG 포지션 진입 실행
                        print("### LONG 포지션 진입 실행 ###")

                        # 시장가 매수
                        order = exchange.create_market_buy_order(
                            symbol=symbol,
                            amount=amount,
                        )

                        # Take Profit 주문 (롱 포지션 청산을 위한 TAKE_PROFIT_MARKET 매도 주문)
                        tp_order = exchange.create_order(
                            symbol=symbol,
                            type="TAKE_PROFIT_MARKET",
                            side="sell",
                            amount=amount,
                            price=None,
                            params={
                                "stopPrice": take_profit_price,
                            },
                        )

                        # Stop Loss 주문 (롱 포지션 청산을 위한 STOP_MARKET 매도 주문)
                        sl_order = exchange.create_order(
                            symbol=symbol,
                            type="STOP_MARKET",
                            side="sell",
                            amount=amount,
                            price=None,
                            params={
                                "stopPrice": stop_loss_price,
                            },
                        )

                        print("## Position LONG ##")
                        print(f"현재가: {current_btc_price} USDT")
                        print(f"익절가(TP): {take_profit_price} USDT (+3%)")
                        print(f"손절가(SL): {stop_loss_price} USDT (-3%)")
                        print("## Position LONG ##")
                    else:
                        print("잔액(USDT)가 0.001BTC 미만 입니다.")
                        print("현재 0.001 BTC : ", tradeable_btc)
                        print("보유 USDT  : ", usdt_available)

                # 매도
                elif decision == "SHORT":

                    # BTC 원화 가치 계산
                    if usdt_available > tradeable_btc:

                        amount = (usdt_available * leverage * 0.995) / current_btc_price

                        # 손익절 계산
                        take_profit_price = round(current_btc_price * 0.97, 2)  # -3%
                        stop_loss_price = round(current_btc_price * 1.03, 2)  # +3%

                        print(f"현재가: {current_btc_price} USDT")
                        print(f"익절가(TP): {take_profit_price} USDT")
                        print(f"손절가(SL): {stop_loss_price} USDT")

                        # Short 포지션 진입
                        print("### SHORT 포지션 진입 실행 ###")
                        order = exchange.create_market_sell_order(
                            symbol=symbol,
                            amount=amount,
                        )

                        # Take Profit 주문 (숏 포지션 청산을 위한 TAKE_PROFIT_MARKET 매수 주문)
                        tp_order = exchange.create_order(
                            symbol=symbol,
                            type="TAKE_PROFIT_MARKET",
                            side="buy",
                            amount=amount,
                            params={
                                "stopPrice": take_profit_price,
                            },
                        )

                        # Stop Loss 주문 (숏 포지션 청산을 위한 STOP_MARKET 매수 주문)
                        sl_order = exchange.create_order(
                            symbol=symbol,
                            type="STOP_MARKET",
                            side="buy",
                            amount=amount,
                            params={
                                "stopPrice": stop_loss_price,
                            },
                        )
                        print("## Position SHORT ##")
                        print(f"현재가: {current_btc_price} USDT")
                        print(f"익절가(TP): {take_profit_price} USDT (-3%)")
                        print(f"손절가(SL): {stop_loss_price} USDT (+3%)")
                        print("## Position SHORT ##")
                    else:
                        print("잔액(USDT)가 0.001BTC 미만 입니다.")
                        print("현재 0.001 BTC : ", tradeable_btc)
                        print("보유 USDT  : ", usdt_available)

                # 홀드
                elif decision == "HOLD":
                    print("## Position HOLD ##")
                    print("       NOTING      ")
                    print("## Position HOLD ##")
                    time.sleep(1800)
                else:
                    print("ai 결정에 문제가 있습니다.")

            time.sleep(2)

        except Exception as e:
            print(f"\n Error: {e}")
            time.sleep(5)


#   time.sleep(1)

#   updated_my_btc = upbit.get_balance("KRW-BTC")
#   updated_my_krw = upbit.get_balance("KRW")
#   updated_current_price = pyupbit.get_current_price("KRW-BTC")

#   #거래 정보 로깅
#   log_trade(
#     conn,
#     result["decision"],
#     result["reason"],
#     updated_my_btc,
#     updated_my_krw,
#     updated_current_price
#   )
#   conn.close()

execute_trading()
