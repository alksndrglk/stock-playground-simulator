from typing import Optional

from app.base.base_accessor import BaseAccessor
from app.stock.models import (
    Game,
    User,
    Stock,
    StockMarketEvent,
    BrokerageAccount,
)
from typing import List


class ExchangeAccessor(BaseAccessor):
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
