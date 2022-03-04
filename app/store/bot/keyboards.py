import json
from app.stock.models import Stock

GREETING = json.dumps(
    {
        "inline": False,
        "one_time": True,
        "buttons": [
            [
                {
                    "action": {
                        "type": "callback",
                        "payload": '{"command": "start"}',
                        "label": "Старт",
                    },
                    "color": "positive",
                },
            ]
        ],
    }
)

EXCHANGE = json.dumps(
    {
        "inline": False,
        "one_time": True,
        "buttons": [
            [
                {
                    "action": {
                        "type": "callback",
                        "payload": '{"command": "sell"}',
                        "label": "Продать",
                    },
                    "color": "primary",
                },
                {
                    "action": {
                        "type": "callback",
                        "payload": '{"command": "buy"}',
                        "label": "Купить",
                    },
                    "color": "primary",
                },
            ]
        ],
    }
)


def make_button(verb, symbol, cost, amount=0):
    return {
        "action": {
            "type": "callback",
            "payload": f'{{"{verb} symbol":"{symbol} {amount}"}}',
            "label": symbol,
        },
    }


def make_buy_dash(stocks: list[Stock]):
    return json.dumps(
        {
            "inline": False,
            "one_time": True,
            "buttons": [
                [make_button("buy", stock.symbol, stock.cost) for stock in stocks]
            ],
        }
    )


def make_sell_dash(portfolio):
    return json.dumps(
        {
            "inline": True,
            "buttons": [
                [
                    {
                        make_button("sell", stock.symbol, stock.cost, stock.amount)
                        for stock in portfolio
                    }
                ]
            ],
        }
    )
