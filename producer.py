import pika
import helper

nyse_path = 'uploads/nyse/'

EXCHANGES = ['nyse', 'nasdaq']

def dispatch(channel, message):
    channel.basic_publish(exchange='', 
        routing_key='task_queue',
        body=message,
        properties=pika.BasicProperties(delivery_mode = 2)) #make message persistent
    print("Sent %r" % message)


def run():
    connection, channel = helper.setup('task_queue')
    symbols = helper.get_stock_symbols(EXCHANGES)
    for symbol in symbols:
        print(symbol)
        # dispatch(channel, ac_url)
    connection.close()

if __name__ == "__main__":
    run()