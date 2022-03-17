import asyncio
from unittest.mock import AsyncMock
import pytest
from aioresponses import aioresponses

from app.store import Store
from app.store.vk_api.poller import Poller
from app.store.vk_api.dataclasses import Update
from tests.data import *


def build_query(host: str, method: str, params: dict) -> str:
    url = host + method + "?"
    if "v" not in params:
        params["v"] = "5.131"
    url += "&".join([f"{k}={v}" for k, v in params.items()])
    return url


class TestPoller:
    async def test_stop(self, store: Store):

        poller = Poller(store)
        poller._worker = AsyncMock()
        await poller.start()
        assert poller.poll_task._state == "PENDING"
        await poller.stop()
        assert poller.poll_task._state == "CANCELLED"
'''
    async def test_vk_poll(self, store: Store):
        with aioresponses() as m:
            m.get(
                build_query(
                    host="https://lp.vk.com/wh210570816",
                    method="",
                    params={
                        "act": "a_check",
                        "key": "3c11021e164f538d5f228f1e8dc2b5baeb42636f",
                        "ts": 2621,
                        "wait": 25,
                    },
                ),
                payload=SELL_MSG,
            )
            m.get(
                build_query(
                    host="https://lp.vk.com/wh210570816",
                    method="",
                    params={
                        "act": "a_check",
                        "key": "3c11021e164f538d5f228f1e8dc2b5baeb42636f",
                        "ts": 2622,
                        "wait": 25,
                    },
                ),
                payload=BUY_MSG,
            )
            poller = Poller(store)
            # store.vk_api.poll = AsyncMock(return_value=OBJ_BUY_MSG)
            await poller.start()
            assert len(poller._chat_queues) == len(poller._workers)
            assert poller._worker.call_count == 2

            await poller.stop()
'''
