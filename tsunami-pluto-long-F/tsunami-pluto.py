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


node = 'http://20.7.14.174:6869'
address = pw.Address(privateKey='')

pw.setNode(node)
usdnId = 'DG2xFkPdDwKUoBkzGAhQtLpSGzfXLiCYPEzeKH2Ad24p'
tsunamiContract = '3PA51qCGL57rBWuD7CBTb3NeRQUxwUf6YRp'
tsunami = Tsunami(tsunamiContract, address, node, usdnId)
# Set default values
entryPrice = 0
invested = 0
# Set default values for putting an order
singleOrderAmount = 100
margin = 3

while True:
    # Check for open positions
    try:
        position = tsunami.getPosition(address.address)
        oraclePrice = tsunami.getOracleTwapPrice()
        marketPrice = tsunami.getTwapSpotPrice()
    except (json.decoder.JSONDecodeError, requests.exceptions.JSONDecodeError,
            KeyError) as error:
        time.sleep(5)
        continue

    # Get markets price

    # Calculate price difference
    # priceDif = marketPrice / oraclePrice
    #invested = (position['margin'] / pow(10, 6)) * 1.01
    # open LONG position
    if position['positionSize'] == 0:
        first_order = tsunami.long(singleOrderAmount, margin)
        printTime()
        print(first_order)
        invested += singleOrderAmount
        entryPrice = marketPrice
        time.sleep(10)
        continue
    if position['margin'] != 0: # and invested == 0:
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
    # If USDN for withdraw covers 1% gain of traded funds CLOSE LONG

    if payout >= profit:
        tsunami.closePosition()
        invested = 0
        entryPrice = 0
    # if price goes up with 5% when short position opened increase current position / add margin
    if marketPrice <= entryPrice * 0.985:
        order = tsunami.long(singleOrderAmount, margin)
        print(order)
        printTime()
        invested += singleOrderAmount
        entryPrice = marketPrice

    # Time interval between checking price changes in seconds
    time.sleep(3)
