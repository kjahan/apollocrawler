import pika
from random import shuffle

from .helper import get_stock_symbols
from .utils.rmq_helper import setup, dispatch

STOCK_EXCHANGES = ['nyse', 'nasdaq']
# STOCK_EXCHANGES = ['nyse', 'nasdaq', 'tsx']


def submit_stock_symbols(stock_batch_size):
    cnt = 0
    stop = False
    connection, channel = setup('stock_queue')
    for exchange in STOCK_EXCHANGES:
        symbols = get_stock_symbols(exchange)
        # randomly shuffle symbols
        shuffle(symbols)
        for sym in symbols:
            ex_sym = sym + '@' + exchange
            dispatch(channel, ex_sym)
            cnt += 1
            if cnt >= stock_batch_size:
                stop = True
                break
        if stop:
            break
    connection.close()

if __name__ == "__main__":
    stock_batch_size = 10
    submit_stock_symbols(stock_batch_size)