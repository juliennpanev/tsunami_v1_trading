import time
import pywaves as pw
from tsunami import Tsunami

node = 'https://nodes.wavesnodes.com'
address = pw.Address(privateKey='')

pw.setNode(node)
usdnId = 'DG2xFkPdDwKUoBkzGAhQtLpSGzfXLiCYPEzeKH2Ad24p'
tsunamiContract = '3PNeboTZQz1XhwDY9V9N3K7xYJrq9XbaS5Z'
tsunami = Tsunami(tsunamiContract, address, node, usdnId)

# Check for open positions
position = tsunami.getPosition(address.address)

# Set default values
entryPrice = 0
invested = 0

# Set default values for putting an order
singleOrderAmount = 10
margin = 3

while True:
    # Get markets price
    oraclePrice = tsunami.getOracleTwapPrice()
    marketPrice = tsunami.getTwapSpotPrice()

    # Calculate price difference 
    priceDif = marketPrice / oraclePrice


    if priceDif >= 1.03 and position['positionSize'] == 0:
        tsunami.short(singleOrderAmount, margin)
        invested += singleOrderAmount
        entryPrice = marketPrice

    if position['margin'] != 0 and invested == 0:
        invested = (position['margin'] * 1.01) / pow(10, 6)


    payout = tsunami.getPayout(address.address)
    profit = ((invested * margin) * 0.035) + invested

    if payout >= profit:
        tsunami.closePosition()

    if marketPrice >= entryPrice * 1.05:
        tsunami.short(singleOrderAmount, 3)
        invested += singleOrderAmount

    time.sleep(30)

