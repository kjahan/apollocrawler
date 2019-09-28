import pickle
import psycopg2
import time
import ast
import json

from apolloengine.src.stock import Stock


class StoreHelper:
    def __init__(self, filename=None):
        self.stocks_stats = {}
        if filename:
            self.filename = filename
            try:
                with open(self.filename, 'rb') as fp:
                    stocks_stats = pickle.load(fp)
            except FileNotFoundError:
                print("Model file doesn't exist!")
                pass
        else:
            self.filename = None
            self.connect_to_db()


    def connect_to_db(self):
        self.conn = psycopg2.connect("dbname='jahan' user='jahan' host='localhost' password=''")
        self.cursor = self.conn.cursor()

    def update_model(self, dict_model):
        if self.filename:
            self.update_file(dict_model)
        else:
            self.update_pg(dict_model)

    def update_file(self, dict_model):
        stock_obj = Stock(dict_model['symbol'], 
                        # pd.DataFrame.from_dict(dict_model['history_prices']),
                        None,
                        dict_model['history_slope'],
                        dict_model['future_slope'], 
                        dict_model['timestamp'])
        stocks_stats = {}
        try:
            with open(self.filename, 'rb') as fp:
                stocks_stats = pickle.load(fp)
        except FileNotFoundError:
            print("Model file doesn't exist!")
            pass
        stocks_stats[stock_obj.symbol] = stock_obj
        # store stocks/stats
        with open(self.filename, 'wb') as fp:
            pickle.dump(stocks_stats, fp)
        print("Updated model size: {}".format(len(stocks_stats)))

    def update_pg(self, dict_model):
        symbol = dict_model["symbol"]
        exchange = dict_model["exchange"]
        data = self.get_model(exchange)
        if len(data) > 0:
            stocks_stats = data[0][0]
            stocks_stats[symbol] = dict_model
            json_model = json.dumps(stocks_stats)
            self.cursor.execute("UPDATE stock_models SET updated = LOCALTIMESTAMP, model = Json(%s) WHERE exchange=%s", (json_model, exchange))
            self.conn.commit() # <- We MUST commit to reflect the inserted data
        else:
            self.insert_single_stock_model(dict_model)

    def get_model(self, exchange):
        self.cursor.execute("SELECT model from stock_models where exchange=%s", (exchange,))
        rows = self.cursor.fetchall()
        return rows

    def insert_single_stock_model(self, dict_model):
        symbol = dict_model["symbol"]
        exchange = dict_model["exchange"]
        stocks_stats = {}
        stocks_stats[symbol] = dict_model
        json_model = json.dumps(stocks_stats)
        self.cursor.execute("INSERT INTO stock_models (created, updated, model, exchange) VALUES (LOCALTIMESTAMP, LOCALTIMESTAMP, Json(%s), %s)", (json_model, exchange))
        self.conn.commit() # <- We MUST commit to reflect the inserted data

    def empty_model(self, exchange):
        if self.filename:
            self.empty_file_model(exchange)
        else:
            self.empty_pg(exchange)

    def empty_file_model(self):
        stocks_stats = {}
        # save an empty model in pickle file
        with open(self.filename, 'wb') as fp:
            pickle.dump(stocks_stats, fp)

    def empty_pg(self, exchange):
        stocks_stats = {}
        json_model = json.dumps(stocks_stats)
        self.cursor.execute("UPDATE stock_models SET updated = LOCALTIMESTAMP, model = Json(%s) WHERE exchange=%s", (json_model, exchange))
        self.conn.commit() # <- We MUST commit to reflect the inserted data

    def get_model_age(self, symbol, exchange):
        if self.filename:
            return self.get_model_age_from_file(symbol, exchange)
        else:
            return self.get_model_age_from_pg(symbol, exchange)

    def get_model_age_from_file(self, symbol, exchange):
        current_ts = int(round(time.time() * 1000)) # in ms
        model_age = 90*24*3600*1000 # 90 days old model by default
        if symbol in self.stocks_stats:
            previous_ts = self.stocks_stats[symbol].timestamp
            model_age = current_ts - previous_ts
        return model_age

    def get_model_age_from_pg(self, symbol, exchange):
        model_age = 90*24*3600*1000 # 90 days old model by default
        if not self.stocks_stats:
            data = self.get_model(exchange)
            if len(data) > 0:
                # cashe stocks data to minimize query time
                self.stocks_stats = data[0][0]        
        if self.stocks_stats:
            current_ts = int(round(time.time() * 1000)) # in ms
            if symbol in self.stocks_stats:
                previous_ts = self.stocks_stats[symbol]['timestamp']
                model_age = current_ts - previous_ts
        return model_age

    def get_stocks_from_pg(self, exchange):
        stock_symbols = set([])
        stock_stats = []
        data = self.get_model(exchange)
        if len(data) > 0:
            stocks_stats = data[0][0]
            stock_symbols = set(stocks_stats.keys())
            for symbol, stock in stocks_stats.items():
                last_price, market_cap = 0, 0
                if "market_cap" in stock:
                    market_cap = stock["market_cap"]
                if "last_price" in stock:
                    last_price = stock["last_price"]
                stock_obj = Stock(symbol)
                stock_obj.set_exchange(stock["exchange"])
                stock_obj.set_history_slope(stock["history_slope"])
                stock_obj.set_future_slope(stock["future_slope"])
                stock_obj.set_market_cap(market_cap)
                stock_obj.set_last_price(last_price)
                stock_stats.append(stock_obj)
        return stock_symbols, stock_stats

    def cleanup_pg(self):
        self.cursor.close()
        self.conn.close()
