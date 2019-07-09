import pika

def setup(queue_name):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)
    return connection, channel

def dispatch(channel, message):
    channel.basic_publish(exchange='', 
        routing_key='task_queue',
        body=message,
        properties=pika.BasicProperties(delivery_mode = 2)) # make message persistent
    print("Sent %r" % message)