import pika
import sys
import time
import json

from apollocrawler.src.helper import download, train_model
from apollocrawler.utils.store_helper import StoreHelper
from apollocrawler.utils.rmq_helper import setup
from apollocrawler.utils.constants import STOCK_STATS_FN
from apolloengine.src.encoder import StockEncoder


DEBUG = False
DELIMITER = '@'
DAYS_PARAM = 90
MODEL_FRESH_TIME = 3*7*24*3600*1000   # we require 3 weeks model freshness!

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
storing_channel = connection.channel()

storing_channel.exchange_declare(exchange='direct_logs', exchange_type='direct')

# storage = StoreHelper(STOCK_STATS_FN)
storage = StoreHelper()

def callback(ch, method, properties, ex_symbol):
    if DEBUG:
        print("Received %r" % ex_symbol)
    items = ex_symbol.decode('utf-8').split(DELIMITER)
    symbol, exchange = items
    try:
        print('Processing {}@{}'.format(symbol, exchange))
        model_age = storage.get_model_age(symbol, exchange)
        if model_age > MODEL_FRESH_TIME:
            # less than 24 hours so update the model!
            history_data = download(symbol, exchange)
            history_data_size = history_data.shape[0]
            if history_data_size >= DAYS_PARAM:
                stock_obj = train_model(history_data, symbol, exchange, DAYS_PARAM)
                storing_channel.basic_publish(exchange='direct_logs', routing_key='model', body=json.dumps(stock_obj, cls=StockEncoder))
            else:
                print('Not enough historical data for {}@{} - history size: {}'.format(symbol, exchange, history_data_size))
        else:
            print('Model for {}@{} is fresh!'.format(symbol, exchange))
    except Exception as e:
        print(str(e))
        pass
    ch.basic_ack(delivery_tag = method.delivery_tag)

def process_stock_symbols():
    connection, channel = setup('stock_queue')
    print('Waiting for stock symbol to process. To exit press CTRL+C')
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume('task_queue', callback)
    channel.start_consuming()

if __name__ == "__main__":
    process_stock_symbols()