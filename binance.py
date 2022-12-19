import hashlib
import hmac
import time
from urllib.parse import urlencode
import requests

from decouple import config

API_KEY = config('KOO_API_KEY')
API_SECRET_KEY = config('KOO_API_SECRET_KEY')

BINANCE_TRADING_FEE = 0.001


class Binance:
    def __init__(self, api_key, api_secret):
        self.base_url = 'https://api.binance.com/'
        self.api_key = api_key
        self.api_secret = api_secret

    def hashing(self, query_string):
        return hmac.new(
            self.api_secret.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256
        ).hexdigest()

    def _get_timestamp(self):
        return int(time.time() * 1000)

    def _dispatch_request(self, http_method):
        session = requests.Session()
        session.headers.update(
            {"Content-Type": "application/json;charset=utf-8", "X-MBX-APIKEY": self.api_key}
        )
        return {
            "GET": session.get,
            "DELETE": session.delete,
            "PUT": session.put,
            "POST": session.post,
        }.get(http_method, "GET")

    def _send_signed_request(self, http_method, url_path, payload=None):
        if payload is None:
            payload = {}
        query_string = urlencode(payload, True)
        if query_string:
            query_string = "{}&timestamp={}".format(query_string, self._get_timestamp())
        else:
            query_string = "timestamp={}".format(self._get_timestamp())
        url = self.base_url + url_path + "?" + query_string + "&signature=" + self.hashing(query_string)
        print("{} {}".format(http_method, url))
        params = {"url": url, "params": {}}
        response = self._dispatch_request(http_method)(**params)
        return response.json()

    def get_all_orders(self, pair):
        return self._send_signed_request("GET", "api/v3/allOrders", {"symbol": pair})


def get_position_cost(records):
    # get filled record (binance API already return all 'FILLED' record?)
    filled_records = list(filter(lambda x: (x['status'] == 'FILLED'), records))

    # qty = amount / price
    position_val = 0
    cost_basis = 0
    qty = 0

    pnl = 0
    for record in filled_records:

        if record['side'] == 'BUY':
            position_val += float(record['cummulativeQuoteQty'])
            qty += float(record['executedQty'])
        elif record['side'] == 'SELL':
            # new_spent = old_spent - (sold * cost_basis)
            sold_qty = float(record['executedQty'])

            delta_pos_val = cost_basis * sold_qty
            position_val = position_val - delta_pos_val if position_val - delta_pos_val > 0 else 0

            # minus sold, (if sold > qty, mean sold contain staking reward)
            qty = qty - sold_qty if qty - sold_qty > 0 else 0

            # P/L
            pnl += (float(record['price']) - cost_basis) * sold_qty

        cost_basis = position_val / qty if qty else 0

    print("{} -> cost basis: {}, qty: {}, P/L: {}".format(trading_pair, cost_basis, qty, pnl))


if __name__ == '__main__':
    client = Binance(API_KEY, API_SECRET_KEY)

    # Testing
    trading_pair = 'ETHUSDT'
    records = client.get_all_orders(trading_pair)

    print(records)

    get_position_cost(records)
