import pika

from .helper import get_stock_symbols
from .utils.rmq_helper import setup, dispatch

STOCK_EXCHANGES = ['nyse', 'nasdaq']

def submit_stock_symbols():
    cnt = 0
    stop = False
    connection, channel = setup('stock_queue')
    for exchange in STOCK_EXCHANGES:
        symbols = get_stock_symbols(exchange)
        for sym in symbols:
            ex_sym = sym + '@' + exchange
            dispatch(channel, ex_sym)
            cnt += 1
            if cnt >= 45:
                stop = True
                break
        if stop:
            break
    connection.close()

if __name__ == "__main__":
    submit_stock_symbols()