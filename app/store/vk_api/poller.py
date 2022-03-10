import asyncio
from asyncio import Task
from asyncio import queues
from asyncio.queues import Queue
from typing import Dict, Optional, List

from app.store import Store


class Poller:
    def __init__(self, store: Store):
        self.store = store
        self.is_running = False
        self.poll_task: Optional[Task] = None
        self._chat_queues: Dict[int, Queue] = {}
        self._workers: List[Task] = []

    async def start(self):
        self.is_running = True
        self.poll_task = asyncio.create_task(self.poll())

    async def stop(self):
        self.is_running = False
        await self.poll_task

    async def _worker(self, queue):
        asyncio.create_task(self.store.bots_manager.handle_updates(queue))

    async def poll(self):
        while self.is_running:
            updates = await self.store.vk_api.poll()
            for u in updates:
                if u.object.peer_id not in self._chat_queues:
                    queue = Queue()
                    self._chat_queues[u.object.peer_id] = queue
                    asyncio.create_task(self._worker(queue))
                await self._chat_queues[u.object.peer_id].put(u)
