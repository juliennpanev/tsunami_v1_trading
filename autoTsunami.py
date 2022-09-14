import requests
import time
import pywaves as pw
from tsunami import Tsunami

node = 'https://nodes.wavesnodes.com'
address = pw.Address(privateKey='')

pw.setNode(node)
usdnId = 'DG2xFkPdDwKUoBkzGAhQtLpSGzfXLiCYPEzeKH2Ad24p'
tsunamiContract = '3PNeboTZQz1XhwDY9V9N3K7xYJrq9XbaS5Z'
tsunami = Tsunami(tsunamiContract, address, node, usdnId)
# Set default values
entryPrice = 0
invested = 0
# Set default values for putting an order
singleOrderAmount = 13
margin = 3



while True:
    # Check for open positions
    try:
        position = tsunami.getPosition(address.address)
    except (AtributeError, requests.exceptions.JSONDecodeError, KeyError) as error:
        time.sleep(5)
        continue

    # Get markets price
    oraclePrice = tsunami.getOracleTwapPrice()
    marketPrice = tsunami.getTwapSpotPrice()
    # Calculate price difference 
    priceDif = marketPrice / oraclePrice
    # If market price > 2% oracle price open short position
    if priceDif >= 1.03 and position['positionSize'] == 0:
        tsunami.short(singleOrderAmount, margin)
        invested += singleOrderAmount
        entryPrice = marketPrice
        time.sleep(30)
        continue
    if position['margin'] != 0 and invested == 0:
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
    profit = ((invested * margin) * 0.03) + invested
    # If USDN for withdraw covers 3% gain of traded funds CLOSE SHORT

    if payout >= profit:
        tsunami.closePosition()
    # if price goes up with 5% when short position opened increase current position / add margin
    if marketPrice >= entryPrice * 1.03:
        tsunami.short(singleOrderAmount, margin)
        invested += singleOrderAmount
        entryPrice = marketPrice

    # Time interval between checking price changes in seconds
    time.sleep(5)
