import typing
import json
from logging import getLogger

from app.store.vk_api.dataclasses import Update, Message

if typing.TYPE_CHECKING:
    from app.web.app import Application


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app
        self.bot = None
        self.logger = getLogger("handler")

    async def handle_updates(self, updates: list[Update]):
        for update in updates:
            if update.object.action.get("type") == "chat_invite_user":
                await self.send_greeting(update.object.peer_id)
            elif update.type == "message_event":
                payload = update.object.payload.get("command")
                if payload == "start":
                    await self.start(update.object.peer_id)
                await self.app.store.vk_api.send_message(
                    Message(
                        peer_id=update.object.peer_id,
                        text="Для не корректной работы бота",
                    )
                )

    async def start(self, peer_id):
        players = await self.app.store.vk_api.get_conversation_members(peer_id)
        print(f"{players=}")
        self.logger.info(players)


    async def send_greeting(self, peer_id):
        await self.app.store.vk_api.send_message(
            Message(
                peer_id=peer_id,
                text="Для корректной работы бота, дайте ему права Администратора в настройках",
                keyboard=json.dumps(
                    {
                        "inline": True,
                        "buttons": [
                            [
                                {
                                    "action": {
                                        "type": "callback",
                                        "payload": '{"command": "start"}',
                                        "label": "Старт",
                                    },
                                    "color": "positive",
                                },
                            ]
                        ],
                    }
                ),
            )
        )
