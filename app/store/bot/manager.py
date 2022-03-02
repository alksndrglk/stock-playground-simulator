import typing
import json
from logging import getLogger
from app.stock.models import Stock

from app.store.vk_api.dataclasses import Update, Message
from app.store.bot.keyboards import GREETING, EXCHANGE, make_sell_dash, make_buy_dash

if typing.TYPE_CHECKING:
    from app.web.app import Application

test_portfolio = [
    Stock(symbol=s, cost=10, description="It's a stock") for s in ["AAPL", "SBR", "TSL"]
]


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app
        self.bot = None
        self.logger = getLogger("handler")

    async def handle_updates(self, updates: list[Update]):
        for update in updates:
            if update.object.action == {
                "type": "chat_invite_user",
                "member_id": -210570816,
            }:
                await self.send_keyboard(
                    update.object.peer_id,
                    keyboard=GREETING,
                    text="Для корректной работы бота, дайте ему права Администратора в настройках",
                )
            elif update.type == "message_event":
                payload = update.object.payload.get("command")
                if payload == "start":
                    await self.start(update.object.peer_id)
                if payload == "sell":
                    await self.send_keyboard(
                        update.object.peer_id,
                        keyboard=make_sell_dash(),
                        text="Для продажи доступны",
                    )
                if payload == "buy":
                    await self.send_keyboard(
                        update.object.peer_id,
                        keyboard=make_buy_dash(test_portfolio),
                        text="Для покупки доступны",
                    )

    async def start(self, peer_id):
        players = await self.app.store.vk_api.get_conversation_members(peer_id)
        await self.send_keyboard(peer_id, text="Выберите действие")
        self.logger.info(players)

    async def send_keyboard(self, peer_id, keyboard=EXCHANGE, text=" "):
        await self.app.store.vk_api.send_message(
            Message(
                peer_id=peer_id,
                text=text,
                keyboard=keyboard,
            )
        )
