#!/usr/bin/env python
import pika
import sys
import ast
import pandas as pd

from .utils.constants import STOCK_STATS_FN
from .utils.store_helper import StoreHelper
from apolloengine.stock import Stock
 

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='direct_logs', exchange_type='direct')

result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

# storage = StoreHelper(STOCK_STATS_FN)
storage = StoreHelper()

# empty model
# storage.empty_model('tsx')

# for severity in severities:
channel.queue_bind(
    exchange='direct_logs', queue=queue_name, routing_key='model')

print(' [*] Waiting for stocks model. To exit press CTRL+C')


def callback(ch, method, properties, body):
	str_model = body.decode('utf-8')
	try:
		dict_model = ast.literal_eval(str_model)
		print(" [x] %r:%r" % (method.routing_key, dict_model['symbol']))
		storage.update_model(dict_model)
	except ValueError:
		pass


channel.basic_consume(
    queue=queue_name, on_message_callback=callback, auto_ack=True)

channel.start_consuming()