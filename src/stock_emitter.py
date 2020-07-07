import pika
import random

from apollocrawler.src.helper import get_stock_symbols
from apollocrawler.utils.rmq_helper import setup, dispatch

STOCK_EXCHANGES = ['nyse', 'nasdaq']
# STOCK_EXCHANGES = ['nyse', 'nasdaq', 'tsx']


def submit_stock_symbols(stock_batch_size):
    connection, channel = setup('stock_queue')
    # get all exchanges syms
    all_symbols = []
    for exchange in STOCK_EXCHANGES:
        all_symbols.extend([sym + '@' + exchange for sym in get_stock_symbols(exchange)])
    # randomly sample "stock_batch_size" symbols
    symbols = random.sample(all_symbols, stock_batch_size)
    for sym_ex in symbols:
        dispatch(channel, sym_ex)
    connection.close()

if __name__ == "__main__":
    stock_batch_size = 2
    submit_stock_symbols(stock_batch_size)