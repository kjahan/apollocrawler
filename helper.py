import pika, requests
import sys
import pandas as pd
import pickle
import time

from fbprophet import Prophet

from apolloengine.utils import financial_utils
from apolloengine.stock import Stock

BASE_FOLDER = "apolloengine/uploads/"
STOCK_STATS_FN = BASE_FOLDER + "models/stock_stats_all_exchanges.pkl"

def setup(queue_name):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)
    return connection, channel


def scrape(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    r = requests.get(url, headers=headers)
    return r.text

def get_stock_symbols(exchange):
    return financial_utils.get_stock_symbols(exchange)

def download(symbol, exchange):
    data_path = BASE_FOLDER + exchange
    try:
        print("Downloading {} stock symbol ...".format(symbol))
        financial_utils.download_stock_history_data(symbol, exchange)
    except timeout_decorator.timeout_decorator.TimeoutError:
        print("Downloading {} stock symbol timed out!".format(symbol))

def update_model_stats(symbol, exchange, days_param=90):
    key = symbol + '@' + exchange
    stocks_stats = {}
    try:
        with open(STOCK_STATS_FN, 'rb') as fp:
            stocks_stats = pickle.load(fp)
    except FileNotFoundError:
        print("Model file doesn't exist!")
        pass
    current_ts = int(round(time.time() * 1000))
    if symbol in stocks_stats:
        previous_ts = stocks_stats[symbol].timestamp
        if (current_ts - previous_ts) < 24*3600*1000:
            # less than 24 hours
            return 0
    stock_fn = BASE_FOLDER + exchange + '/' + symbol + '.tsv'
    prices_df = pd.read_csv(stock_fn, sep='\t')
    if prices_df.empty or prices_df.shape[0] <= days_param:
        return 0
    history_slope = financial_utils.compute_slope(prices_df, 'y', days_param)
    m = Prophet()
    m.fit(prices_df)
    future = m.make_future_dataframe(periods=days_param)
    forecast = m.predict(future)
    trend_df = forecast[['trend']].tail(days_param)
    future_slope = financial_utils.compute_slope(trend_df, 'trend', days_param)
    print("Stock symbol: {}, history slope: {}, future slope: {}"
        .format(symbol, history_slope, future_slope))
    stock_obj = Stock(symbol, prices_df, history_slope, future_slope)
    stocks_stats[symbol] = stock_obj
    # store stocks/stats
    with open(STOCK_STATS_FN, 'wb') as fp:
        pickle.dump(stocks_stats, fp)
