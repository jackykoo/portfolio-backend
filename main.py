import yfinance as yf


if __name__ == '__main__':
    # define the ticker symbol
    ticker_symbol = 'meta'
    alibaba = '9988.HK'

    # get data on this ticker
    stock = yf.Ticker(ticker_symbol)

    # get the historical prices for this ticker
    # tickerDf = stock.history(period='1d', start='2022-10-1', end='2022-10-11')
    # print(tickerDf)
    price = stock.info['regularMarketPrice']
    print(price)
