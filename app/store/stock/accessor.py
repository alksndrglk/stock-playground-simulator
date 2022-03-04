from typing import List
from app.base.base_accessor import BaseAccessor

from app.stock.models import (
    BrokerageAccountModel,
    Game,
    GameModel,
    GameXUser,
    User,
    UserModel,
    GameStockModel,
    StockModel,
)
from app.store.database.gino import db
from app.store.bot.dataclassess import VkUser
from sqlalchemy.dialects.postgresql import insert


class ExchangeAccessor(BaseAccessor):
    async def get_game(self, peer_id: int):
        game_info = (
            await GameModel.outerjoin(GameXUser, GameModel.id == GameXUser.game_id)
            .outerjoin(UserModel, UserModel.id == GameXUser.user_id)
            .outerjoin(
                BrokerageAccountModel,
                (
                    BrokerageAccountModel.user_id == UserModel.id
                    and BrokerageAccountModel.game_id == GameModel.id
                ),
            )
            .select()
            .where(GameModel.id == peer_id)
            .gino.load(
                GameModel.distinct(GameModel.id).load(
                    add_users=UserModel.distinct(UserModel.id).load(
                        portfolio=BrokerageAccountModel.distinct(
                            BrokerageAccountModel.id
                        )
                    )
                )
            )
            .all()
        )
        val = [
            Game(
                [
                    User(
                        id=u.id,
                        vk_id=u.user_id,
                        user_name=u.user_name,
                        portfolio=u.portfolio.to_dct(),
                    )
                    for u in g.users
                ],
                chat_id=g.chat_id,
                state=g.state,
            )
            for g in game_info
        ]
        print(val)

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
        await insert(BrokerageAccountModel).values(
            [
                {
                    "user_id": u.id,
                    "game_id": game_id,
                    "points": 1000,
                }
                for u in users
            ]
        ).on_conflict_do_nothing().gino.all()

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

