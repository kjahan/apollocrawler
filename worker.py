import pika
import multiprocessing
import sys
import threading
import time

from .helper import setup, download, train_model, save_model, get_model_age

DEBUG = False
DELIMITER = '@'
DAYS_PARAM = 90
lock = multiprocessing.Lock()

def callback(ch, method, properties, ex_symbol):
    if DEBUG:
        print("Received %r" % ex_symbol)
    items = ex_symbol.decode('utf-8').split(DELIMITER)
    symbol, exchange = items
    try:
        print('processing {}@{}'.format(symbol, exchange))
        model_age = 0 # in ms
        with lock:
            model_age = get_model_age(symbol)
        if model_age > 24*3600*1000:
            # less than 24 hours so update the model!
            download(symbol, exchange)
            stock_obj = train_model(symbol, exchange, DAYS_PARAM)
            with lock:
                save_model(stock_obj)
        else:
            print('model for {}@{} is fresh!'.format(symbol, exchange))
    except Exception as e:
        print(str(e))
        pass
    ch.basic_ack(delivery_tag = method.delivery_tag)

def process_stock_symbols():
    connection, channel = setup('task_queue')
    print('Waiting for stock symbol to process. To exit press CTRL+C')
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume('task_queue', callback)
    channel.start_consuming()

if __name__ == "__main__":
    # process_stock_symbols()
    t1 = threading.Thread(target=process_stock_symbols, args=[])
    t2 = threading.Thread(target=process_stock_symbols, args=[])
    t3 = threading.Thread(target=process_stock_symbols, args=[])
    t4 = threading.Thread(target=process_stock_symbols, args=[])
    t5 = threading.Thread(target=process_stock_symbols, args=[])
    t6 = threading.Thread(target=process_stock_symbols, args=[])
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t5.start()
    t6.start()
    t1.join()
    t2.join()
    t3.join()
    t4.join()
    t5.join()
    t6.join()