import requests
import sys
import pandas as pd
import pickle

import timeout_decorator
from fbprophet import Prophet

from apolloengine.src.utils import financial_utils
from apolloengine.src.stock import Stock
from .utils.constants import BASE_FOLDER
from .utils.constants import STOCK_STATS_FN


def scrape(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    r = requests.get(url, headers=headers)
    return r.text

def get_stock_symbols(exchange):
    return financial_utils.get_stock_symbols(exchange)


def download(symbol, exchange):
    data_path = BASE_FOLDER + exchange
    history_data_size = 0
    try:
        print("Downloading {} stock symbol ...".format(symbol))
        history_data = financial_utils.download_stock_history_data(symbol, exchange)
    # except timeout_decorator.timeout_decorator.TimeoutError:
    except Exception as e:
        print("Downloading {} stock symbol timed out! {}".format(symbol, str(e)))
    return history_data

def train_model(prices_df, symbol, exchange, days_param=90):
    key = symbol + '@' + exchange
    # stock_fn = BASE_FOLDER + exchange + '/' + symbol + '.tsv'
    # prices_df = pd.read_csv(stock_fn, sep='\t')
    if prices_df.empty or prices_df.shape[0] <= days_param:
        return None
    history_slope = financial_utils.compute_slope(prices_df, 'y', days_param)
    last_price = prices_df.tail(1)['y'].values[0]
    m = Prophet()
    m.fit(prices_df)
    future = m.make_future_dataframe(periods=days_param)
    forecast = m.predict(future)
    trend_df = forecast[['trend']].tail(days_param)
    future_slope = financial_utils.compute_slope(trend_df, 'trend', days_param)
    market_cap = financial_utils.get_market_cap(symbol)
    print("Stock symbol: {}, history slope: {}, future slope: {}, market cap: {}"
        .format(symbol, history_slope, future_slope, market_cap))
    stock_obj = Stock(symbol)
    stock_obj.set_exchange(exchange)
    stock_obj.set_history_slope(history_slope)
    stock_obj.set_future_slope(future_slope)
    stock_obj.set_market_cap(market_cap)
    stock_obj.set_last_price(last_price)
    return stock_obj