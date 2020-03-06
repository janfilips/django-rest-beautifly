import os
import django
import datetime
import requests
import time

from django.conf import settings
from django.utils import timezone


print("Choose settings:")
print("1. development")
print("2. production")
s = input("? ")

if s == "1":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.develop")
if s == "2":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")
django.setup()


from ioi.game.models import Ticker

SLEEP_INTERVAL = 0.5

TICKER_ADDRESS = "https://api.binance.com/api/v3/ticker/price"
BINANCE_HEADERS = {"X-MBX-APIKEY": settings.BINANCE_KEY}

CURRENCIES = [
    {"symbol": "BTCUSDT", "desc": "Bitcoin"},
    {"symbol": "ETHUSDT", "desc": "Ethereum"},
    {"symbol": "XRPUSDT", "desc": "Ripple"},
    {"symbol": "BCHUSDT", "desc": "Bitcoin Cash"},
    {"symbol": "LTCUSDT", "desc": "Litecoin"},
    {"symbol": "EOSUSDT", "desc": "EOS"},
    {"symbol": "BNBUSDT", "desc": "Binance Coin"},
    {"symbol": "XMRUSDT", "desc": "Monero"},
    {"symbol": "ADAUSDT", "desc": "Cardano"},
    {"symbol": "TRXUSDT", "desc": "Tron"},
]


if __name__ == "__main__":

    epoch_prices = None

    print("Updating ticker...")
    while True:

        prices = []

        for currency in CURRENCIES:

            params = {"symbol": currency["symbol"]}

            r = requests.get(TICKER_ADDRESS, headers=BINANCE_HEADERS, params=params)
            if r.status_code == 200:
                r = r.json()
                prices.append(
                    {
                        "symbol": r["symbol"],
                        "price": float(r["price"]),
                        "desc": currency["desc"],
                    }
                )
                print(timezone.now(), "-", r["symbol"], "$" + str(r["price"]))
            else:
                print("Ticker error.")
                raise

        try:
            ticker = Ticker.objects.get(pk=1)
            ticker.prices = prices
            ticker.updated = datetime.datetime.now()
            ticker.save()
        except Ticker.DoesNotExist:
            ticker = Ticker.objects.create(prices=prices)

        if not epoch_prices:
            epoch_prices = prices
            ticker.epoch_prices = epoch_prices
            ticker.save()

        time.sleep(SLEEP_INTERVAL)
