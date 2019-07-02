import pika, time

from .helper import setup, download, update_model_stats

DEBUG = False
DELIMITER = '@'
DAYS_PARAM = 90

def callback(ch, method, properties, ex_symbol):
    
    if DEBUG:
        print("Received %r" % ex_symbol)
    items = ex_symbol.decode('utf-8').split(DELIMITER)
    symbol, exchange = items
    try:
        print('symbol: {} @ {} exchange'.format(symbol, exchange))
        download(symbol, exchange)
        update_model_stats(symbol, exchange, DAYS_PARAM)
    except Exception as e:
        print(str(e))
        pass
    ch.basic_ack(delivery_tag = method.delivery_tag)

def run():
    connection, channel = setup('task_queue')
    print('Waiting for URL to scrape. To exit press CTRL+C')
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume('task_queue', callback)
    channel.start_consuming()

if __name__ == "__main__":
    run()