import json
import websocket
from kafka import KafkaProducer
from binance.client import Client
import pandas as pd
from dotenv import load_dotenv
import os


class CryptoPriceProducerStreaming:
    def __init__(self):
        load_dotenv("../.env",override=True)
        self.bootstrap_servers = os.getenv('BOOSTRAP_SERVERS')
        self.socket_url = os.getenv('SOCKET_URL')

        self.producer = KafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

        self.client = Client()

        exchange_info = self.client.get_exchange_info()
        self.symbols = [symbol['symbol'] for symbol in exchange_info['symbols'] if symbol['symbol'].endswith('USDT')]

        self.assets = [symbol.lower() + '@kline_1m' for symbol in self.symbols]
        self.relevant_assets = '/'.join(self.assets)
        self.socket = f"{self.socket_url}{self.relevant_assets}"

    def manipulate(self, data):
        value_data = data['k']
        price, sym = value_data['c'], value_data['s']
        event_time = pd.to_datetime(data['E'], unit='ms').isoformat()
        return {'price': price, 'symbol': sym, 'event_time': event_time}

    def on_message(self, ws, message):
        json_message = json.loads(message)
        if 'data' in json_message:
            data = json_message['data']
            if 'k' in data:
                manipulated_data = self.manipulate(data)
                self.producer.send('crypto-prices', value=manipulated_data)

    def on_error(self, ws, error):
        print(f"Error: {error}")
        ws.close()

    def on_open(self, ws):
        print("### WebSocket opened ###")

    def run(self):
        ws = websocket.WebSocketApp(
            self.socket,
            on_message=self.on_message,
            on_error=self.on_error,
            on_open=self.on_open
        )
        ws.run_forever()


def main():
    streamer = CryptoPriceProducerStreaming()
    streamer.run()

if __name__ == "__main__":
    main()