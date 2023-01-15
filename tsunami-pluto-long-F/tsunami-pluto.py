from datetime import datetime
import requests
import time
import pywaves as pw
from tsunami import Tsunami
import json


def printTime():
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    print(dt_string)



address = pw.Address(privateKey='')

pw.setNode('https://nodes.wavesnodes.com')

usdnId = 'DG2xFkPdDwKUoBkzGAhQtLpSGzfXLiCYPEzeKH2Ad24p'
tsunamiContract = '3PA51qCGL57rBWuD7CBTb3NeRQUxwUf6YRp'
tsunami = Tsunami(tsunamiContract, address, node, usdnId)

entryPrice = 0
invested = 0

singleOrderAmount = 100
margin = 3

while True:
  
    try:
        position = tsunami.getPosition(address.address)
        oraclePrice = tsunami.getOracleTwapPrice()
        marketPrice = tsunami.getTwapSpotPrice()
    except (json.decoder.JSONDecodeError, requests.exceptions.JSONDecodeError,
            KeyError) as error:
        time.sleep(5)
        continue

    if position['positionSize'] == 0:
        first_order = tsunami.long(singleOrderAmount, margin)
        printTime()
        print(first_order)
        invested += singleOrderAmount
        entryPrice = marketPrice
        time.sleep(5)
        continue
    if position['margin'] != 0:
        invested = (position['margin'] * 1.01) / pow(10, 6)
        size = position['positionSize']
        fundsWithMargin = (position['margin'] * margin)
        entryPrice = abs(fundsWithMargin / size)
    payout = 0
    try:
        payout = tsunami.getPayout(address.address)
    except:
        time.sleep(5)
        continue
    profit = ((invested * margin) * 0.025) + invested
    

    if payout >= profit:
        tsunami.closePosition()
        invested = 0
        entryPrice = 0
    
    if marketPrice <= entryPrice * 0.985:
        order = tsunami.long(singleOrderAmount, margin)
        print(order)
        printTime()
        invested += singleOrderAmount
        entryPrice = marketPrice

    # Time interval between checking price changes in seconds
    time.sleep(3)
