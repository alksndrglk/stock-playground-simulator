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
            else:
                print(update.object.action)
                await self.app.store.vk_api.send_message(
                    Message(
                        peer_id=update.object.peer_id,
                        text="Для не корректной работы бота, дайте ему права Администратора в настройках",
                    )
                )

    async def send_greeting(self, peer_id):
        await self.app.store.vk_api.send_message(
            Message(
                peer_id=peer_id,
                text="Для корректной работы бота, дайте ему права Администратора в настройках",
                keyboard=json.dumps(
                    {
                        "one_time": True,
                        "buttons": [
                            [
                                {
                                    "action": {
                                        "type": "text",
                                        "payload": '{"button": "2"}',
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
