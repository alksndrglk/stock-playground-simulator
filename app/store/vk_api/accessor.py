import random
import json
import typing
from typing import Optional, List

from aiohttp import TCPConnector
from aiohttp.client import ClientSession

from app.base.base_accessor import BaseAccessor
from app.store.bot.dataclassess import VkUser
from app.store.vk_api.dataclasses import Update, Message, UpdateObject
from app.store.vk_api.poller import Poller
from app.stock.models import User

if typing.TYPE_CHECKING:
    from app.web.app import Application

API_PATH = "https://api.vk.com/method/"


class VkApiAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.session: Optional[ClientSession] = None
        self.key: Optional[str] = None
        self.server: Optional[str] = None
        self.poller: Optional[Poller] = None
        self.ts: Optional[int] = None

    async def connect(self, app: "Application"):
        self.session = ClientSession(connector=TCPConnector(verify_ssl=False))
        try:
            await self._get_long_poll_service()
        except Exception as e:
            self.logger.error("Exception", exc_info=e)
        self.poller = Poller(app.store)
        self.logger.info("start polling")
        await self.poller.start()

    async def disconnect(self, app: "Application"):
        if self.session:
            await self.session.close()
        if self.poller:
            await self.poller.stop()

    @staticmethod
    def _build_query(host: str, method: str, params: dict) -> str:
        url = host + method + "?"
        if "v" not in params:
            params["v"] = "5.131"
        url += "&".join([f"{k}={v}" for k, v in params.items()])
        return url

    async def _get_long_poll_service(self):
        async with self.session.get(
            self._build_query(
                host=API_PATH,
                method="groups.getLongPollServer",
                params={
                    "group_id": self.app.config.bot.group_id,
                    "access_token": self.app.config.bot.token,
                },
            )
        ) as resp:
            data = (await resp.json())["response"]
            self.logger.info(data)
            self.key = data["key"]
            self.server = data["server"]
            self.ts = data["ts"]
            self.logger.info(self.server)

    async def poll(self):
        async with self.session.get(
            self._build_query(
                host=self.server,
                method="",
                params={
                    "act": "a_check",
                    "key": self.key,
                    "ts": self.ts,
                    "wait": 25,
                },
            )
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                self.logger.info(data)
                self.ts = data["ts"]
                raw_updates = data.get("updates", [])
                updates = []
                for update in raw_updates:
                    peer_id = update["object"].get("peer_id", None)
                    user_id = update["object"].get("user_id", None)
                    _type = update["type"]
                    updates.append(
                        Update(
                            type=_type,
                            object=UpdateObject(
                                id=update["object"]
                                .get("message", {})
                                .get("id"),
                                peer_id=peer_id
                                if peer_id
                                else update["object"]
                                .get("message", {})
                                .get("peer_id"),
                                user_id=user_id
                                if user_id
                                else update["object"]
                                .get("message", {})
                                .get("from_id"),
                                body=update["object"]
                                .get("message", {})
                                .get("text"),
                                action=update["object"]
                                .get("message", {})
                                .get("action", {}),
                                payload=update["object"].get("payload", {}),
                                obj=update["object"]
                                if _type == "message_event"
                                else {},
                            ),
                        )
                    )
                return updates
            # await self.app.store.bots_manager.handle_updates(updates)

    async def get_conversation_members(self, peer_id) -> Optional[List[VkUser]]:
        async with self.session.get(
            self._build_query(
                API_PATH,
                "messages.getConversationMembers",
                params={
                    "peer_id": peer_id,
                    "group_id": str(self.app.config.bot.group_id),
                    "access_token": self.app.config.bot.token,
                },
            )
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                users = []
                if not data.get("error", False):
                    for profile in data["response"].get("profiles"):
                        users.append(
                            VkUser(
                                vk_id=profile.get("id"),
                                user_name=" ".join(
                                    [
                                        profile.get("first_name"),
                                        profile.get("last_name"),
                                    ]
                                ),
                            )
                        )
                return users

    async def send_message(self, message: Message) -> None:
        query = self._build_query(
            API_PATH,
            "messages.send",
            params={
                "peer_id": message.peer_id,
                # "user_id": message.user_id,
                "random_id": random.randint(1, 2 ** 32),
                "group_id": str(self.app.config.bot.group_id),
                "message": message.text.replace("\n", "%0A"),
                "access_token": self.app.config.bot.token,
                "keyboard": json.dumps(message.keyboard),
            },
        )
        async with self.session.get(query) as resp:
            data = await resp.json()
            self.logger.info(data)

    async def send_answer(self, obj, text) -> None:
        query = self._build_query(
            API_PATH,
            "messages.sendMessageEventAnswer",
            params={
                "event_id": obj["event_id"],
                "user_id": obj["user_id"],
                "peer_id": obj["peer_id"],
                "access_token": self.app.config.bot.token,
                "event_data": json.dumps(
                    {
                        "type": "show_snackbar",
                        "text": text,
                    }
                ),
            },
        )
        async with self.session.get(query) as resp:
            data = await resp.json()
            self.logger.info(data)
