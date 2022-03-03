from typing import List
from app.base.base_accessor import BaseAccessor

from app.stock.models import (
    BrokerageAccountModel,
    GameModel,
    GameXUser,
    UserModel,
    GameStockModel,
    StockModel,
)
from app.store.database.gino import db
from app.store.bot.dataclassess import VkUser
from sqlalchemy.dialects.postgresql import insert


class ExchangeAccessor(BaseAccessor):
    async def create_game(self, players: List[VkUser], peer_id: int):
        async with db.transaction():
            game = await GameModel(chat_id=peer_id).create()
            await self.user_registration(players, game.id)
            await self.stocks_initialization(game.id)

    async def user_registration(self, players: List[VkUser], game_id: int):
        users = await (
            insert(UserModel)
            .values(
                [
                    {
                        "user_id": player.vk_id,
                        "user_name": player.user_name,
                    }
                    for player in players
                ]
            )
            .on_conflict_do_nothing()
            .returning(*UserModel)
            .gino.all()
        )

        await GameXUser.insert().gino.all(
            [
                {
                    "game_id": game_id,
                    "user_id": u.id,
                }
                for u in users
            ]
        )
        await self.portfolio_creation(users, game_id)

    async def portfolio_creation(self, users: list, game_id: int):
        await BrokerageAccountModel.insert().gino.all(
            [
                {
                    "user_id": u.id,
                    "game_id": game_id,
                    "points": 1000,
                }
                for u in users
            ]
        )

    async def stocks_initialization(self, game_id: int):
        stocks = await StockModel.query.gino.all()
        await GameStockModel.insert().gino.all(
            [
                {
                    "symbol": stock.symbol,
                    "description": stock.description,
                    "cost": stock.cost,
                    "game_id": game_id,
                }
                for stock in stocks
            ]
        )
