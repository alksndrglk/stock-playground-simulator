from typing import TYPE_CHECKING, Dict, NamedTuple, Optional
from logging import getLogger
from app.stock.models import BrokerageAccount, Game, Stock, StockMarketEvent, User
from app.store.bot.const import RULES_AND_GREET, add_to_chat_event

from app.store.vk_api.dataclasses import Update, Message, UpdateObject
from app.store.bot.keyboards import STATIC, GREETING, END
from app.store.bot.conditions import VERB_TO_FUNCTION, RequestVerb
from app.store.bot.errors import (
    OperationIsUnavailable,
    RequestDoesNotMeetTheStandart,
    SymbolNotInPortfolio,
)

if TYPE_CHECKING:
    from app.web.app import Application


class ClientMessage(NamedTuple):
    verb: RequestVerb
    symbol: str
    quantity: int


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app
        self.bot = None
        self.logger = getLogger("handler")

    def parse_message(self, msg: str):
        try:
            command, symbol, quantity = msg.split()

            for verb in RequestVerb:
                if command == verb.value:
                    break
            else:
                self.logger("Unnown command in message")
                raise RequestDoesNotMeetTheStandart

            return ClientMessage(verb, symbol, int(quantity))
        except ValueError:
            raise RequestDoesNotMeetTheStandart

    async def handle_updates(self, updates: list[Update]):
        for update in updates:
            keyboard = STATIC
            text = ""
            if update.object.action == add_to_chat_event:
                keyboard, text = GREETING, RULES_AND_GREET
            elif update.type == "message_event":
                payload = update.object.payload.get("command")
                if payload == "start":
                    text = await self.start(update.object.peer_id)
                if payload == "finished_bidding":
                    keyboard, text = await self.user_finished_bidding(update.object)
                if payload == "end":
                    text = await self.finish_game(update.object.peer_id)
                    keyboard = END
            elif update.type == "message_new":
                try:
                    text = await self.message_processing(update.object)
                except (
                    OperationIsUnavailable,
                    RequestDoesNotMeetTheStandart,
                    SymbolNotInPortfolio,
                ) as e:
                    text = str(e)
            if text:
                await self.send_keyboard(
                    update.object.peer_id,
                    keyboard=keyboard,
                    text=text,
                )

    async def start(self, peer_id: int):
        players = await self.app.store.vk_api.get_conversation_members(peer_id)
        stocks = await self.app.store.exchange.create_game(players, peer_id)
        return self.market_situtaion(stocks)

    async def send_keyboard(self, peer_id: int, keyboard=STATIC, text=" "):
        await self.app.store.vk_api.send_message(
            Message(
                peer_id=peer_id,
                text=text,
                keyboard=keyboard,
            )
        )

    async def message_processing(self, upd: UpdateObject):
        try:
            client_message = self.parse_message(upd.body)
        except RequestDoesNotMeetTheStandart:
            raise

        game: Game = await self.app.store.exchange.get_game(upd.peer_id)
        brokerage_account = game.users[upd.user_id].brokerage_account
        try:
            new_brokerage_acc = getattr(
                brokerage_account, VERB_TO_FUNCTION[client_message.verb]
            )(
                client_message.symbol,
                client_message.quantity,
                game.stocks[client_message.symbol].cost,
            )
            await self.app.store.exchange.update_brokerage_acc(new_brokerage_acc)
            return "Операция выполнена"
        except OperationIsUnavailable:
            raise
        except SymbolNotInPortfolio:
            raise

    async def user_finished_bidding(self, upd: UpdateObject):
        msg = ""
        game: Game = await self.app.store.exchange.get_game(upd.peer_id)
        if upd.user_id not in game.round_info["finished_bidding"]:
            game.round_info["finished_bidding"].append(upd.user_id)
        if [*game.users.keys()] == game.round_info["finished_bidding"]:
            msg += f"{game.round_info['round_number']}й раунд торгов окончен\n"
            game.state[game.round_info["round_number"]] = {
                u: str(v) for u, v in game.users.items()
            }
            if game.round_info["round_number"] >= 11:
                await self.finish_game(upd.peer_id, game)
            else:
                game.round_info["round_number"] += 1
                event = await self.market_events()
                new_stocks = await self.recalculate_stocks(game, event)
                msg += self.market_situtaion(new_stocks, event=event)
                msg += self.brokerage_accounts_info(game.users, new_stocks)
            game.round_info["finished_bidding"] = []
        await self.app.store.exchange.update_game(game)
        return (END if game.round_info["round_number"] >= 11 else STATIC, msg)

    async def finish_game(self, peer_id: int, game: Game):
        pass

    async def market_events(self) -> StockMarketEvent:
        return await self.app.store.exchange.get_event()

    async def recalculate_stocks(
        self, game: Game, event: StockMarketEvent
    ) -> Dict[str, Stock]:
        return await self.app.store.exchange.update_stocks(
            game.id, game.stocks, event.diff
        )

    def brokerage_accounts_info(
        self, users: Dict[int, User], stocks: Dict[str, Stock]
    ) -> str:
        msg = "\n\nСостояние инвестиционных портфелей:\n"
        for _, u in users.items():
            fc = 0
            for k, v in u.brokerage_account.portfolio.items():
                fc += v * stocks[k].cost
            msg += (
                f"{u.user_name}({u.user_id}) {str(u)}: стоимость портфеля {fc:.2f}$\n"
            )
        return msg

    def market_situtaion(
        self,
        stocks: Dict[str, Stock],
        event: StockMarketEvent = None,
        text: str = "Цены на акции:\n",
    ) -> str:
        if event:
            text = str(event) + text
        text += "\n".join(str(s) for _, s in stocks.items())
        return text
