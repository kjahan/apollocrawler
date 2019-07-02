import pika

from .helper import get_stock_symbols, setup

EXCHANGES = ['nyse', 'nasdaq']

def dispatch(channel, message):
    channel.basic_publish(exchange='', 
        routing_key='task_queue',
        body=message,
        properties=pika.BasicProperties(delivery_mode = 2)) #make message persistent
    print("Sent %r" % message)


def run():
    cnt = 0
    connection, channel = setup('task_queue')
    for exchange in EXCHANGES:
        symbols = get_stock_symbols(exchange)
        for sym in symbols:
            ex_sym = sym + '@' + exchange
            dispatch(channel, ex_sym)
            cnt += 1
            if cnt >= 2:
                break
    connection.close()

if __name__ == "__main__":
    run()