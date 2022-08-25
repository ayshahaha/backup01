import json
import ccxt
import sys
import time
from flask import Flask, request
import pandas as pd
from binance.client import Client
from binance.enums import *
from ta.trend import EMAIndicator
import os
import requests
#from configparser import ConfigParser  # การเรียกไฟล์ Config
from line_notify import LineNotify 

duration = 1000  # milliseconds
freq = 440  # Hz

#dbconf = ConfigParser()
#dbconf.read_file(open('config.ini'))

app = Flask(__name__)

API_KEY = str(os.environ['API_KEY'])
API_SECRET = str(os.environ['API_SECRET'])
ACCESS_TOKEN = str(os.environ['LINE_TOKEN'])

SYMBOLNAME = str(os.environ['SYMBOL_NAME']).split(",")
LEVERAGE = str(os.environ['LEVERAGE_X']).split(",")
TF = str(os.environ['TF'])
FASTEMAVALUE = str(os.environ['FAST_EMAVALUE'])
SLOWEMAVALUE = str(os.environ['SLOW_EMAVALUE'])
COST = str(os.environ['COST_PERCENT'])
ORDER_ENABLE = str(os.environ['ORDER_ENABLE'])
TPSLMODE = str(os.environ['MODE'])
TP = str(os.environ['TP_PERCENT'])
SL = str(os.environ['SL_PERCENT'])
BOT_NAME = str(os.environ['BOT_NAME'])
notify = LineNotify(ACCESS_TOKEN)


################## Prepare API & SECRET ################
client = Client(API_KEY,API_SECRET)

@app.route("/")
def hello_world():
    return BOT_NAME + "God Trader X48 It's Here !!"

#Hedge Mode & OneWay Check
data = client.futures_get_position_mode()
print("Position mode: Hedge Mode" if data['dualSidePosition'] == True else "Position mode: OneWay Mode")

if ORDER_ENABLE == 'TRUE':

    ######## Notify After Heroku Start ######
    
    #mes="ยินดีต้อนรับเข้าสู่\n~Binance Future 2EMA Bot~"+"\n\n🧭 === Setting === 🧭\n\nAsset : "+str(SYMBOLNAME)+"\nLeverage : "+str(LEVERAGE)+"\nTime Frame : "+TF+"\nFast EMA : "+FASTEMAVALUE+"\nSlow EMA : "+SLOWEMAVALUE+"\nTPSL Mode : "+str(TPSLMODE)
    #notify.send(mes)
    ####### Setting ##########
    kesisim = False
    longPozisyonda = False
    shortPozisyonda = False
    pozisyondami = False
    amount = 0
    ROE = 0
    # API CONNECT
    exchange = ccxt.binance({
    "apiKey": API_KEY,
    "secret": API_SECRET,
    'options': {
    'defaultType': 'future'
    },
    'enableRateLimit': True
    })
    balance = exchange.fetch_balance()
    free_balance = exchange.fetch_free_balance()      
    positions = balance['info']['positions']
    for i in range(len(SYMBOLNAME)):
        symbolNamei = SYMBOLNAME[i]
        newSymboli = SYMBOLNAME[i] + "USDT"
        symboli = SYMBOLNAME[i] + "/USDT"
        leveragei = LEVERAGE[i]
        current_positions = [position for position in positions if float(position['positionAmt']) != 0 and position['symbol'] == newSymboli]
        position_bilgi = pd.DataFrame(current_positions, columns=["symbol", "entryPrice", "unrealizedProfit", "isolatedWallet", "positionAmt", "positionSide","initialMargin"])
        print(newSymboli)
    #symboltest = ('XRP')
    #for i in range(len(symboltest)):
    #	symbolNamei = symboltest
    #	newSymboli = symboltest + "USDT"
    #	symboli = symboltest + "/USDT"
    #	leveragei = '20'
    #	current_positions = [position for position in positions if float(position['positionAmt']) != 0 and position['symbol'] == newSymboli]
    #	position_bilgi = pd.DataFrame(current_positions, columns=["symbol", "entryPrice", "unrealizedProfit", "isolatedWallet", "positionAmt", "positionSide","initialMargin"])
    #	print(newSymboli)
    #คำสั่งเซท leverage
    exchange.load_markets()
    market = exchange.markets[symboli]
    exchange.fapiPrivate_post_leverage({"symbol": market['id'],"leverage": leveragei,})
    #Pozisyonda olup olmadığını kontrol etme
    if not position_bilgi.empty and position_bilgi["positionAmt"][len(position_bilgi.index) - 1] != 0:
    	pozisyondami = True
    else: 
    	pozisyondami = False
    	shortPozisyonda = False
    	longPozisyonda = False
    # Long pozisyonda mı?
    if pozisyondami and float(position_bilgi["positionAmt"][len(position_bilgi.index) - 1]) > 0:
       	longPozisyonda = True
       	shortPozisyonda = False
        ####For V.1.1 Not Params For OneWay Mode Only, Hedge Must Be Add params
        params = 'BOTH'
        if data['dualSidePosition'] == True:
            params = 'LONG'
    # Short pozisyonda mı?
    if pozisyondami and float(position_bilgi["positionAmt"][len(position_bilgi.index) - 1]) < 0:
       	shortPozisyonda = True
       	longPozisyonda = False
        ####For V.1.1 Not Params For OneWay Mode Only, Hedge Must Be Add params
        params = 'BOTH'
        if data['dualSidePosition'] == True:
            params = 'SHORT'
    # LOAD BARS
    bars = exchange.fetch_ohlcv(symboli, timeframe=TF, since = None, limit = 50)
    df = pd.DataFrame(bars, columns=["timestamp", "open", "high", "low", "close", "volume"])
    # LOAD FAST EMA
    FastEma= EMAIndicator(df["close"], float(FASTEMAVALUE))
    df["Fast Ema"] = FastEma.ema_indicator()
    #FastSma= SMAIndicator(df["close"], float(FASTEMAVALUE))
    #df["Fast Sma"] = FastSma.sma_indicator()
    #print(FastSma)
    #print("     FastSma : "+str(df["Fast Sma"][len(df.index)-2]))
    # LOAD SLOW EMA
    slowEma= EMAIndicator(df["close"], float(SLOWEMAVALUE))
    df["Slow Ema"] = slowEma.ema_indicator()
    #print("     SlowEma : "+str(df["Slow Ema"][len(df.index)-2]))
    #print(df["Fast Ema"] )
    #print(df["Slow Ema"] )
    #เงื่อนไขบอกว่าจุดตัด                               
    if (df["Fast Ema"][len(df.index)-3] < df["Slow Ema"][len(df.index)-3] and df["Fast Ema"][len(df.index)-2] > df["Slow Ema"][len(df.index)-2]) or (df["Fast Ema"][len(df.index)-3] > df["Slow Ema"][len(df.index)-3] and df["Fast Ema"][len(df.index)-2] < df["Slow Ema"][len(df.index)-2]):
    	kesisim = True
    else: 
    	kesisim = False
    # LONG ENTER
    def longEnter(amount):
        if data['dualSidePosition'] == True:
            order = exchange.create_market_buy_order(newSymboli, amount, params)
            #order = exchange.create_market_buy_order(newSymboli, amount,)       #For V.1.1 Not Params For OneWay Only, Hedge add params
        else :
            order = exchange.create_market_buy_order(newSymboli, amount)
    # LONG EXIT
    def longExit():
        if data['dualSidePosition'] == True:
            order = exchange.create_market_sell_order(newSymboli, 		float(position_bilgi["positionAmt"][len(position_bilgi.index) - 1]), {"reduceOnly": True}, params)
        else :
            order = exchange.create_market_sell_order(newSymboli, 		float(position_bilgi["positionAmt"][len(position_bilgi.index) - 1]), {"reduceOnly": True})
    # SHORT ENTER
    def shortEnter(amount):
        if data['dualSidePosition'] == True:
            order = exchange.create_market_sell_order(newSymboli, amount, params)
            #order = exchange.create_market_sell_order(newSymboli, amount)       #For V.1.1 Not Params For OneWay Only, Hedge add params
        else :
            order = exchange.create_market_sell_order(newSymboli, amount)  
    # SHORT EXIT
    def shortExit():
        if data['dualSidePosition'] == True:
            order = exchange.create_market_buy_order(newSymboli, (float(position_bilgi["positionAmt"][len(position_bilgi.index) - 1]) * -1), {"reduceOnly": True}, params)
        else :
            order = exchange.create_market_buy_order(newSymboli, (float(position_bilgi["positionAmt"][len(position_bilgi.index) - 1]) * -1), {"reduceOnly": True})
    # BULL EVENT
    if kesisim and df["Fast Ema"][len(df.index)-2] > df["Slow Ema"][len(df.index)-2] and longPozisyonda == False:
        if shortPozisyonda:
        	print("SHORT ENTERING PROCESSING...")
        	shortExit()
        amount = (((float(free_balance["USDT"]) / 100 ) * float(cost)) * float(leveragei)) / float(df["close"][len(df.index) - 2])
        print("LONG ENTERING PROCESSING...")
        longEnter(amount)
        message ="\n"+ newSymboli +" "+str(leveragei)+" x"+ "\nสถานะ : LONG ↗️\n" + "ราคา : "+str(round(df["close"][len(df.index) - 1],5))+" USDT"+"\nจำนวน : "+str(round(amount,2))+" "+str(symbolNamei)+" / "+str(round((float(amount)*float(df["close"][len(df.index) - 1]))/float(leveragei),2))+" USDT"+"\n\n💰ยอดเงินคงเหลือ : " + str(round(balance['total']["USDT"],2))+" USDT"
        notify.send(message)
    # BEAR EVENT
    if kesisim and df["Fast Ema"][len(df.index)-2] < df["Slow Ema"][len(df.index)-2] and shortPozisyonda == False:
        if longPozisyonda:
        	print("LONG ENTERING PROCESSING...")
        	longExit()
        amount = (((float(free_balance["USDT"]) / 100 ) * float(cost)) * float(leveragei)) / float(df["close"][len(df.index) -2])
        print ("SHORT ENTERING PROCESSING....")
        shortEnter(amount)
        message ="\n"+ newSymboli +" "+str(leveragei)+" x"+ "\nสถานะ : SHORT ↘️\n" + "ราคา : "+str(round(df["close"][len(df.index) - 1],5))+" USDT"+"\nจำนวน : "+str(round(amount,2))+" "+str(symbolNamei)+" / "+str(round((float(amount)*float(df["close"][len(df.index) - 1]))/float(leveragei),2))+" USDT"+"\n\n💰ยอดเงินคงเหลือ : " + str(round(balance['total']["USDT"],2))+" USDT"
        notify.send(message)
    if TPSLMODE == 'on' :
       	if longPozisyonda:
       		ROE=(float(position_bilgi["unrealizedProfit"][len(position_bilgi.index) - 1])*100)/float(position_bilgi["initialMargin"][len(position_bilgi.index) - 1])
       		TP=float(TP)*float(leveragei)
       		SL=float(SL)*float(leveragei)
       		if kesisim == False and ROE >= TP and tp != 0:
       			print("LONG TAKE PROFIT PROCESSING...")
       			longExit()
       			message = "\n"+ newSymboli +" "+str(leveragei)+" x"+ "\nสถานะ : Long TP 😆\n" + "ราคา : "+str(round(df["close"][len(df.index) - 1],5))+" USDT"+"\nROE : "+str(round(ROE,2))+" %\n\n💰ยอดเงินคงเหลือ : " + str(round(balance['total']["USDT"],2))+" USDT"
       			notify.send(message)
       		if kesisim == False and ROE <= SL and sl != 0:
       			print("LONG STOP LOSS PROCESSING...")
       			longExit()
       			message = "\n"+ newSymboli +" "+str(leveragei)+" x"+ "\nสถานะ : Long SL 😭\n" + "ราคา : "+str(round(df["close"][len(df.index) - 1],5))+" USDT"+"\nROE : "+str(round(ROE,2))+" %\n\n💰ยอดเงินคงเหลือ : " + str(round(balance['total']["USDT"],2))+" USDT"
       			notify.send(message)
       	if shortPozisyonda:
       		ROE=(float(position_bilgi["unrealizedProfit"][len(position_bilgi.index) - 1])*100)/float(position_bilgi["initialMargin"][len(position_bilgi.index) - 1])
       		TP=float(TP)*float(leveragei)
       		SL=float(SL)*float(leveragei)
       		if kesisim == False and ROE >= TP and tp != 0:
       		 	print("SHORT TAKE PROFIT PROCESSING...")
       		 	shortExit()
       		 	message = "\n"+ newSymboli +" "+str(leveragei)+" x"+ "\nสถานะ : Short TP 😆\n" + "ราคา : "+str(round(df["close"][len(df.index) - 1],5))+" USDT"+"\nROE : "+str(round(ROE,2))+" %\n\n💰ยอดเงินคงเหลือ : " + str(round(balance['total']["USDT"],2))+" USDT"
       		 	notify.send(message)
       		 	if kesisim == False and ROE <= SL and sl != 0:
       		 		print("SHORT STOP LOSS PROCESSING...")
       		 		shortExit()
       		 		message = "\n"+ newSymboli +" "+str(leveragei)+" x"+ "\nสถานะ : Short SL 😭\n" + "ราคา : "+str(round(df["close"][len(df.index) - 1],5))+" USDT"+"\nROE : "+str(round(ROE,2))+" %\n\n💰ยอดเงินคงเหลือ : " + str(round(balance['total']["USDT"],2))+" USDT"
       		 		notify.send(message)
    if pozisyondami == False:
    	print("Status : Wait Position ...")
    if shortPozisyonda:
    	print("Status : Short Position")
    if longPozisyonda:
       print("Status : Long Position")
    print("====================")       

            
else:
    exchange_type = 'maintenance mode'

if __name__ == '__main__':
    app.run(debug=True)
