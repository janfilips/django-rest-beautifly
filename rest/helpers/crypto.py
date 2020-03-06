def calculate_coins_performance(start_price, finish_price):

    coins_performance = []

    for coin in start_price:

        for x in finish_price:
            if x["symbol"] == coin["symbol"]:
                break

        percent = 100 / float(coin["price"]) * float(x["price"])
        percent = percent - 100
        percent = round(percent, 2)

        # print(' -', coin["symbol"], coin["price"],"->", x["price"],"=",str(percent)+"%")

        coin_performance = {
            "symbol": coin["symbol"],
            "from_price": coin["price"],
            "to_price": x["price"],
            "percent": percent,
        }
        coins_performance.append(coin_performance)

    return coins_performance


if __name__ == "__main__":

    # Example data

    start_coins_price = [
        {"symbol": "BTCUSDT", "price": "7192.77000000"},
        {"symbol": "ETHUSDT", "price": "144.43000000"},
        {"symbol": "XRPUSDT", "price": "0.21956000"},
        {"symbol": "BCHUSDT", "price": "205.21000000"},
        {"symbol": "LTCUSDT", "price": "43.78000000"},
        {"symbol": "EOSUSDT", "price": "2.58130000"},
        {"symbol": "BNBUSDT", "price": "14.67460000"},
        {"symbol": "XMRUSDT", "price": "52.47000000"},
        {"symbol": "ADAUSDT", "price": "0.03613000"},
        {"symbol": "TRXUSDT", "price": "0.01402000"},
    ]
    finish_coins_price = [
        {"symbol": "BTCUSDT", "price": "7185.80000000"},
        {"symbol": "ETHUSDT", "price": "144.22000000"},
        {"symbol": "XRPUSDT", "price": "0.21934000"},
        {"symbol": "BCHUSDT", "price": "204.91000000"},
        {"symbol": "LTCUSDT", "price": "43.73000000"},
        {"symbol": "EOSUSDT", "price": "2.58000000"},
        {"symbol": "BNBUSDT", "price": "14.65750000"},
        {"symbol": "XMRUSDT", "price": "52.41000000"},
        {"symbol": "ADAUSDT", "price": "0.03610000"},
        {"symbol": "TRXUSDT", "price": "0.01401000"},
    ]

    coins_performance = calculate_coins_performance(
        start_coins_price, finish_coins_price
    )

    # print("coins_performance", coins_performance)
