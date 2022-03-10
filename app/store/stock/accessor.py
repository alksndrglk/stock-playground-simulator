from datetime import datetime
from typing import List, Dict
from app.base.base_accessor import BaseAccessor
from sqlalchemy import and_
from app.stock.models import (
    BrokerageAccountModel,
    BrokerageAccount,
    Game,
    GameModel,
    GameXUser,
    Stock,
    StockMarketEvent,
    StockMarketEventModel,
    User,
    UserModel,
    GameStockModel,
    StockModel,
)
from app.store.bot.dataclassess import VkUser
from app.web.utils import secure_game_creation
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql.expression import func


class ExchangeAccessor(BaseAccessor):
    async def get_game(self, peer_id: int):
        game_info = (
            await GameModel.outerjoin(GameXUser, GameModel.id == GameXUser.game_id)
            .outerjoin(UserModel, UserModel.id == GameXUser.user_id)
            .outerjoin(GameStockModel, GameStockModel.game_id == GameModel.id)
            .outerjoin(
                BrokerageAccountModel,
                (
                    BrokerageAccountModel.user_id == UserModel.id
                    and BrokerageAccountModel.game_id == GameModel.id
                ),
            )
            .select()
            .where(and_(GameModel.chat_id == peer_id, GameModel.finished_at == None))
            .gino.load(
                GameModel.distinct(GameModel.id).load(
                    add_users=UserModel.distinct(UserModel.id).load(
                        portfolio=BrokerageAccountModel.distinct(
                            BrokerageAccountModel.id
                        )
                    ),
                    add_stocks=GameStockModel.distinct(GameStockModel.id),
                )
            )
            .all()
        )
        return (
            None
            if not game_info
            else [
                Game(
                    id=g.id,
                    users=g.users,
                    stocks=g.stocks,
                    chat_id=g.chat_id,
                    state=g.state,
                    round_info=g.round_info,
                )
                for g in game_info
            ][0]
        )

    @secure_game_creation
    async def create_game(self, players: List[VkUser], peer_id: int):
        game = await GameModel().get_or_create(peer_id)
        users = await self.user_registration(players, game.id)
        await self.connect_user_game(users, game.id)
        await self.portfolio_creation(users, game.id)
        return await self.stocks_initialization(game.id)

    async def user_registration(
        self, players: List[VkUser], game_id: int
    ) -> List[User]:
        qu = insert(UserModel).values(
            [
                {
                    "user_id": player.vk_id,
                    "user_name": player.user_name,
                }
                for player in players
            ]
        )

        users = await (
            qu.on_conflict_do_update(
                index_elements=[UserModel.user_id], set_={"created_at": datetime.now()}
            )
            .returning(*UserModel)
            .gino.all()
        )
        return [User(id=u.id, user_id=u.user_id, user_name=u.user_name) for u in users]

    async def connect_user_game(self, users: List[User], game_id: int):
        await GameXUser.insert().gino.all(
            [
                {
                    "game_id": game_id,
                    "user_id": u.id,
                }
                for u in users
            ]
        )

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

    async def stocks_initialization(self, game_id: int) -> Dict[str, Stock]:
        stocks = await StockModel.query.gino.all()
        stocks_in_game = (
            await insert(GameStockModel)
            .values(
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
            .on_conflict_do_nothing()
            .returning(*GameStockModel)
            .gino.all()
        )
        return {s.symbol: Stock(**s) for s in stocks_in_game}

    async def update_brokerage_acc(self, brokerage_account: BrokerageAccount):
        await BrokerageAccountModel.update.values(
            portfolio=brokerage_account.portfolio, points=brokerage_account.points
        ).where(
            and_(
                BrokerageAccountModel.user_id == brokerage_account.user_id,
                BrokerageAccountModel.game_id == brokerage_account.game_id,
            )
        ).gino.status()

    async def update_game(self, game: Game):
        await GameModel.update.values(
            round_info=game.round_info, state=game.state
        ).where(GameModel.id == game.id).gino.status()

    async def update_stocks(
        self, stocks: Dict[str, Stock], diff: int
    ) -> Dict[str, Stock]:
        new_stocks = await (GameStockModel.bulk_upsert(stocks.values(), diff))
        return {s.symbol: Stock(**s) for s in new_stocks}

    async def get_event(self) -> StockMarketEvent:
        return (
            await StockMarketEventModel.query.order_by(func.random()).gino.first()
        ).to_dct()
