import requests.exceptions
import time
import pywaves as pw
from tsunami import Tsunami


node = 'https://nodes.wavesnodes.com'
address = pw.Address(privateKey='')

pw.setNode(node)
usdnId = 'DG2xFkPdDwKUoBkzGAhQtLpSGzfXLiCYPEzeKH2Ad24p'
tsunamiContract = '3PA51qCGL57rBWuD7CBTb3NeRQUxwUf6YRp'
tsunami = Tsunami(tsunamiContract, address, node, usdnId)
# Set default values
entryPrice = 0
invested = 0
# Set default values for putting an order
singleOrderAmount = 10
margin = 3
marginAdded = 0
priceMarginAddedAt = 0


while True:
    # Check for open positions
    try:
        position = tsunami.getPosition(address.address)
    except (requests.exceptions.JSONDecodeError, KeyError) as error:
        time.sleep(10)
        continue
    # Get markets price
    oraclePrice = tsunami.getOracleTwapPrice()
    marketPrice = tsunami.getTwapSpotPrice()
    # Calculate price difference 
    priceDif = marketPrice / oraclePrice
    # If market price > 3% oracle price open short position 
    if priceDif >= 1.02 and position['positionSize'] == 0:
        tsunami.short(singleOrderAmount, margin)
        invested += singleOrderAmount
        entryPrice = marketPrice
        time.sleep(30)

    if position['margin'] != 0 and invested == 0:
        invested = (position['margin'] * 1.01) / pow(10, 6)
        entryPrice = abs((position['margin'] * margin) / (position['positionSize']))
    payout = 0
    try:
        payout = tsunami.getPayout(address.address)
    except:
        time.sleep(10)
        continue

    profit = ((invested * margin) * 0.02) + invested

    # If USDN for withdraw covers 3.5% gain of traded funds CLOSE SHORT
    if payout >= profit:
        tsunami.closePosition()
    # if price goes up with 5% when short position opened increase current position / add margin
    if marketPrice >= entryPrice * 1.05 and marginAdded == 0:
        tsunami.short(singleOrderAmount, margin)
        tsunami.addMargin(singleOrderAmount / 3)
        marginAdded += singleOrderAmount / 3
        invested += singleOrderAmount + marginAdded
        priceMarginAddedAt = marketPrice

    if marketPrice >= priceMarginAddedAt * 1.05 and priceMarginAddedAt != 0:
        priceMarginAddedAt = marketPrice
        tsunami.short(singleOrderAmount, margin)
        tsunami.addMargin(singleOrderAmount / 3)
        invested += singleOrderAmount + (singleOrderAmount / 3)
        marginAdded += singleOrderAmount / 3

    # Time interval between checking price changes in seconds
    time.sleep(10)
