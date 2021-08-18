import pyupbit
import pandas as pd
import time

access = "me1YZcgLFyx9akQkx11zYoewBxTUY6Yy7BtXHLiK"
secret = "xCpCZ7d9UkrJC7MmFyXLJ0u5OHswqHDXgIR3rZqJ"

upbit = pyupbit.Upbit(access, secret)

# MACD 정의
def MACD(df, macd_short = 12, macd_long = 26, macd_signal = 9) :
    df = pd.DataFrame(df)
    MACD_short = df['close'].ewm(span = macd_short).mean()
    MACD_long = df['close'].ewm(span = macd_long).mean()
    MACD_macd = MACD_short - MACD_long
    MACD_signal = MACD_macd.ewm(span = macd_signal).mean()
    MACD_oscillator = MACD_macd - MACD_signal

    return MACD_oscillator

# Stochastic Slow 정의

def Stochastic(df, n=5, m=3, t=3) :
    df = pd.DataFrame(df)
    ndays_high = df['high'].rolling(window = n).max()
    ndays_low = df['low'].rolling(window = n).min()
    fast_k = ((df['close'] - ndays_low) / (ndays_high - ndays_low)) * 100
    slow_k = fast_k.ewm(span = m).mean()
    slow_d = slow_k.ewm(span = t).mean() 

    new_df = df.assign(Fast_K = fast_k, Fast_D = slow_k, Slow_K = slow_k, Slow_D = slow_d)
    return new_df

a = 5000
b = 80000
c = 120000

#시장가 매수 함수
def buy(coin) :
    money = upbit.get_balance("KRW")
    if money < a :
        res = upbit.buy_market_order(coin, money * 1)
    elif money < b :
        res = upbit.buy_market_order(coin, money * 0.5)
    elif money < c :
        res = upbit.buy_market_order(coin, money * 0.4)
    else : 
        res = upbit.buy_market_order(coin, money * 0.3)
    return

# 시장가 매도 함수
def sell(coin) :
    amount = upbit.get_balance(coin)
    res = upbit.sell_market_order(coin, amount)
    return

# 이용할 코인리스트
coinlist = ["KRW-BTC", "KRW-ETH", "KRW-ETC", "KRW-QTUM", "KRW-AXS", "KRW-EOS", "KRW-OMG", "KRW-BSV", "KRW-DOT"]

# 매매 스위치 설정
Buy_coin = []
Sell_coin = []

#거래 시작
for i in range(len(coinlist)) :
    Buy_coin.append(False)
    Sell_coin.append(False)

while(True) :
    for i in range(len(coinlist)) :
        df = pyupbit.get_ohlcv(ticker = coinlist[i], interval = "minute30")
        now_Slow_K = Stochastic(df, 5, 3, 3).iloc[-1, -2]
        past_Slow_K = Stochastic(df,5, 3, 3).iloc[-2, -2]
        now_Slow_D = Stochastic(df, 5, 3, 3).iloc[-1, -1]
        MACD_oscillator_1 = MACD(df, 12, 26, 9).iloc[-1]
        MACD_oscillator_2 = MACD(df, 12, 26, 9).iloc[-2]
        MACD_oscillator_3 = MACD(df, 12, 26, 9).iloc[-3]
        print("코인명: ", coinlist[i])
        print("Slow_K: ", now_Slow_K)
        print("Slow_D: ", now_Slow_D)
        print("MACD_OSCILLATOR_past_2: ", MACD_oscillator_3)
        print("MACD_OSCILLATOR_past_1: ", MACD_oscillator_2)
        print("MACD_OSCILLATOR_now: ", MACD_oscillator_1)

        # 매수 조건
        if (Sell_coin[i] == False and Buy_coin[i] == False and MACD_oscillator_3 > 0 and MACD_oscillator_2 < 0 and MACD_oscillator_1 < 0) :
            Buy_coin[i] = True
            print(coinlist[i], ": BUY_WAIT_ON")
            print()

        elif (Sell_coin[i] == False and Buy_coin[i] == False and MACD_oscillator_3 < 0 and MACD_oscillator_2 < 0 and MACD_oscillator_1 < 0 and MACD_oscillator_3 > MACD_oscillator_2) :
            Buy_coin[i] = True
            print(coinlist[i], ": BUY_WAIT_ON")
            print()
            

        elif Buy_coin[i] == True and Sell_coin[i] == False :
            if (MACD_oscillator_1 > MACD_oscillator_2 > MACD_oscillator_3 and now_Slow_K > now_Slow_D and now_Slow_K < 80) :
                buy(coinlist[i])
                Buy_coin[i] = False
                Sell_coin[i] = True
                print(coinlist[i], ": BUY")
                print()

            elif (MACD_oscillator_1 > MACD_oscillator_2 > MACD_oscillator_3 and now_Slow_K > now_Slow_D and now_Slow_K > 80) :
                Buy_coin[i] = False
                print(coinlist[i], ": BUY_HOLD_OFF")
                print()

            else :
                print(coinlist[i], ": BUY_WAIT_ING")
                print()

        # 매도 조건
        elif Buy_coin[i] == False and Sell_coin[i] == True :
            if now_Slow_K + 1 < now_Slow_D :
                sell(coinlist[i])
                Sell_coin[i] = False
                print(coinlist[i], ": SELL")
                print()

            elif (MACD_oscillator_2 > MACD_oscillator_1 and MACD_oscillator_1 < 0 and past_Slow_K > now_Slow_K ):
                sell(coinlist[i])
                Buy_coin[i] = True
                Sell_coin[i] = False
                print(coinlist[i], ": SELL and BUY_WAIT_ING")
                print()

            else :
                print(coinlist[i], ": SELL_WAIT_ING")
                print()

        else :
            print(coinlist[i], ": HOLD_OFF")
            print()

    time.sleep(60)