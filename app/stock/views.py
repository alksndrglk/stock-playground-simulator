from aiohttp.web_exceptions import HTTPConflict
from aiohttp_apispec import (
    request_schema,
    response_schema,
    querystring_schema,
    docs,
)
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response

from app.stock.schemes import (
    AllGamesSchema,
    ChatIdSchema,
    GameModelSchema,
    StockSchema,
    StockListSchema,
    EventSchema,
    EventListSchema,
)


class StockAddView(AuthRequiredMixin, View):
    @docs(tags=["Stock"], description="Stock Add View")
    @request_schema(StockSchema)
    @response_schema(StockSchema)
    async def post(self):
        symbol = self.data["symbol"]
        existing_stock = await self.store.exchange.get_stock_by_symbol(symbol)
        if existing_stock:
            raise HTTPConflict
        stock = await self.store.exchange.create_stock(
            symbol=symbol,
            description=self.data["description"],
            cost=self.data["cost"],
        )
        return json_response(data=StockSchema().dump(stock))


class StockListView(AuthRequiredMixin, View):
    @docs(tags=["Stock"], description="List Stocks View")
    @response_schema(StockListSchema)
    async def get(self):
        stocks = await self.store.exchange.list_stocks()
        return json_response(data=StockListSchema().dump({"stocks": stocks}))


class EventAddView(AuthRequiredMixin, View):
    @docs(tags=["Event"], description="Event Add View")
    @request_schema(EventSchema)
    @response_schema(EventSchema)
    async def post(self):
        message = self.data["message"]
        existing_event = await self.store.exchange.get_event_by_message(message)
        if existing_event:
            raise HTTPConflict
        theme = await self.store.exchange.create_event(
            message=message, diff=self.data["diff"]
        )
        return json_response(data=EventSchema().dump(theme))


class EventListView(AuthRequiredMixin, View):
    @docs(tags=["Event"], description="List Events View")
    @response_schema(EventListSchema)
    async def get(self):
        events = await self.store.exchange.list_events()
        return json_response(data=EventListSchema().dump({"events": events}))


class GameStatisticView(AuthRequiredMixin, View):
    @docs(tags=["Game"], description="Game Statistic View")
    @querystring_schema(ChatIdSchema)
    async def get(self):
        chat_id = self.request.get("querystring", {}).get("chat_id")
        game = await self.store.exchange.get_stats(chat_id=chat_id)
        if chat_id:
            return json_response(data=GameModelSchema().dump(game))
        return json_response(data=AllGamesSchema().dump({"games": game}))
