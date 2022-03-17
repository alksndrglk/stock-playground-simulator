import pytest

from app.stock.models import GameModel, Game, Stock, BrokerageAccount, User
from app.store.bot.dataclassess import VkUser

"""
    users_1 = [
        VkUser(vk_id=3, user_name="Olef"),
        VkUser(vk_id=4, user_name="Leila"),
    ]

    users_2 = [
        VkUser(vk_id=33, user_name="Sasha"),
        VkUser(vk_id=34, user_name="Igor"),
    ]
"""

@pytest.fixture(scope="function")
def game_2_usrs():
    return Game(
        id=183,
        users={
            11142114: User(
                id=222,
                user_id=11142114,
                user_name="Alexander Igorevich",
                brokerage_account=BrokerageAccount(
                    id=241,
                    user_id=222,
                    game_id=183,
                    points=1000.0,
                    portfolio={},
                ),
            ),
            11142115: User(
                id=221,
                user_id=11142115,
                user_name="Alexander Ivanovich",
                brokerage_account=BrokerageAccount(
                    id=240,
                    user_id=221,
                    game_id=183,
                    points=1000.0,
                    portfolio={},
                ),
            )
        },
        chat_id=2000000006,
        state={},
        round_info={"round_number": 1, "finished_bidding": []},
        stocks={
            "TSL": Stock(
                symbol="TSL",
                description="Tesla",
                cost=18.99,
                game_id=183,
                id=1579,
            ),
            "AMZN": Stock(
                symbol="AMZN",
                description="Amazon",
                cost=15.99,
                game_id=183,
                id=1578,
            ),
            "AAPL": Stock(
                symbol="AAPL",
                description="Apple",
                cost=10.99,
                game_id=183,
                id=1577,
            ),
        },
        finished_at=None,
    )

@pytest.fixture(scope="function")
def game():
    return Game(
        id=183,
        users={
            11142115: User(
                id=221,
                user_id=11142115,
                user_name="Alexander Ivanovich",
                brokerage_account=BrokerageAccount(
                    id=240,
                    user_id=221,
                    game_id=183,
                    points=1000.0,
                    portfolio={},
                ),
            )
        },
        chat_id=2000000006,
        state={},
        round_info={"round_number": 1, "finished_bidding": []},
        stocks={
            "TSL": Stock(
                symbol="TSL",
                description="Tesla",
                cost=18.99,
                game_id=183,
                id=1579,
            ),
            "AMZN": Stock(
                symbol="AMZN",
                description="Amazon",
                cost=15.99,
                game_id=183,
                id=1578,
            ),
            "AAPL": Stock(
                symbol="AAPL",
                description="Apple",
                cost=10.99,
                game_id=183,
                id=1577,
            ),
        },
        finished_at=None,
    )


@pytest.fixture(scope="function")
def finished_game():
    return Game(
        id=184,
        users={},
        chat_id=2000000006,
        state={
            "1": {
                "11142115": "Alexander Ivanovich] -- На счете: 9890.00💲\nAкции:\nAAPL➖ 10"
            }
        },
        round_info={"round_number": 2, "finished_bidding": []},
        stocks={},
        finished_at=None,
    )
