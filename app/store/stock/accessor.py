from typing import Optional

from app.base.base_accessor import BaseAccessor
from app.stock.models import (
    Game,
    GameModel,
    GameXUser,
    User,
    Stock,
    StockMarketEvent,
    BrokerageAccount,
    UserModel,
    GameStockModel,
    StockModel,
)
from typing import List


class ExchangeAccessor(BaseAccessor):
    async def create_game(self, players, peer_id):
        game = await GameModel(chat_id=peer_id).create()
        users = await UserModel.insert().gino.all(
            [
                {
                    "user_id": player.user_id,
                    "user_name": player.user_name,
                }
                for player in players
            ]
        )
        await GameXUser.insert().gino.all(
            [
                {
                    "game_id": game.id,
                    "user_id": u.id,
                }
                for u in users
            ]
        )

    async def get_stock_by_symbol(self, symbol: str) -> Optional[Stock]:
        pass

    async def add_stock(
        self, symbol: str, description: str, cost: float
    ) -> Optional[Stock]:
        pass

    async def list_stocks(self) -> List[Stock]:
        pass

    async def list_events(self) -> List[StockMarketEvent]:
        pass

    async def create_user(self, user_name: str, vk_id: int) -> Optional[User]:
        pass

    async def get_user_stats_by_id(self, vk_id: int) -> Optional[BrokerageAccount]:
        pass

    async def get_game_stats_by_id(self, chat_id: int) -> Optional[Game]:
        pass
