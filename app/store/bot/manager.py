from collections import namedtuple
import typing
from logging import getLogger
from app.stock.models import Game, Stock
from app.store.bot.const import RULES_AND_GREET, add_to_chat_event

from app.store.vk_api.dataclasses import Update, Message, UpdateObject
from app.store.bot.keyboards import GREETING, EXCHANGE, make_sell_dash, make_buy_dash
from app.store.bot.conditions import VERB_TO_FUNCTION, RequestVerb
from app.store.bot.errors import (
    OperationIsUnavailable,
    RequestDoesNotMeetTheStandart,
    SymbolNotInPortfolio,
)

if typing.TYPE_CHECKING:
    from app.web.app import Application

test_portfolio = [
    Stock(id=1, game_id=1, symbol=s, cost=10, description="It's a stock")
    for s in ["AAPL", "SBR", "TSL"]
]

ClientMessage = namedtuple("Message", "verb symbol quantity")


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

            return ClientMessage(verb, symbol, quantity)
        except ValueError:
            raise RequestDoesNotMeetTheStandart

    async def handle_updates(self, updates: list[Update]):
        for update in updates:
            if update.object.action == add_to_chat_event:
                await self.send_keyboard(
                    update.object.peer_id,
                    keyboard=GREETING,
                    text=RULES_AND_GREET,
                )
            elif update.type == "message_event":
                payload = update.object.payload.get("command")
                if payload == "start":
                    await self.start(update.object.peer_id)
            elif update.type == "message_new":
                try:
                    await self.message_processing(update.object)
                except (
                    OperationIsUnavailable,
                    RequestDoesNotMeetTheStandart,
                    SymbolNotInPortfolio,
                ) as e:
                    await self.app.store.vk_api.send_message(
                        Message(
                            peer_id=update.object.peer_id,
                            text=str(e),
                        )
                    )

    async def start(self, peer_id: int):
        players = await self.app.store.vk_api.get_conversation_members(peer_id)
        await self.app.store.exchange.create_game(players, peer_id)

    async def send_keyboard(self, peer_id: int, keyboard=EXCHANGE, text=" "):
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
        brokerage_account = next(
            filter(lambda u: u.vk_id == upd.user_id, game.users)
        ).brokerage_account
        try:
            new_brokerage_acc = getattr(
                brokerage_account, VERB_TO_FUNCTION[client_message.verb]
            )(client_message.symbol, client_message.quantity)
        except OperationIsUnavailable:
            raise
        except SymbolNotInPortfolio:
            raise

        await self.app.store.exchange.update_brokerage_acc(new_brokerage_acc)
