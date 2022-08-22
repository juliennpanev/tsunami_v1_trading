import time
import pywaves as pw
from tsunami import Tsunami

node = 'https://nodes.wavesnodes.com'
address = pw.Address(privateKey='')

pw.setNode(node)
usdnId = 'DG2xFkPdDwKUoBkzGAhQtLpSGzfXLiCYPEzeKH2Ad24p'
tsunamiContract = '3PNeboTZQz1XhwDY9V9N3K7xYJrq9XbaS5Z'
tsunami = Tsunami(tsunamiContract, address, node, usdnId)
position = tsunami.getPosition(address.address)
entryPrice = 0
invested = 0
fundingTimestamp = tsunami.getNextFundingTimestamp()
# funding = tsunami.getTimeToNextFunding()
payout = tsunami.getPayout(address.address)

while True:
    oraclePrice = tsunami.getOracleTwapPrice()
    marketPrice = tsunami.getTwapSpotPrice()
    priceDif = marketPrice / oraclePrice

    if priceDif >= 1.03 and marketPrice > oraclePrice and position['positionSize'] == 0:
        tsunami.short(10, 3)
        invested += 10
        entryPrice = marketPrice
    if position['margin'] is not 0 and invested == 0:
        invested = position['margin'] * 1.01


    payout = tsunami.getPayout(address.address)
    profit = entryPrice / marketPrice

    if payout >= invested * 1.03:
        desiredOut = invested * 1.03
        tsunami.closePosition()

    if marketPrice >= entryPrice * 1.03:
        tsunami.short(10, 3)
        invested += 10

    time.sleep(30)

