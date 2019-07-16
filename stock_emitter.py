import pika
from random import shuffle

from .helper import get_stock_symbols
from .utils.rmq_helper import setup, dispatch

STOCK_EXCHANGES = ['tsx', 'nyse', 'nasdaq']

def submit_stock_symbols():
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
            if cnt >= 20:
                stop = True
                break
        if stop:
            break
    connection.close()

if __name__ == "__main__":
    submit_stock_symbols()