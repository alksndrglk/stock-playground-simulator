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
        self.roll_task: Optional[Task] = None
        self._stop_event = asyncio.Event()
        self._chat_queues: Dict[int, Queue] = {}
        self._concurrent_workers = 0

    async def start(self):
        self.is_running = True
        self.poll_task = asyncio.create_task(self.poll())
        self._concurrent_workers -= 1
        if not self.is_running and self._concurrent_workers == 0:
            self._stop_event.set()

    async def stop(self):
        self.is_running = False
        self.poll_task.cancel()
        await self._stop_event.wait()

    async def _worker(self, queue):
        self._concurrent_workers += 1
        await self.store.bots_manager.handle_updates(queue)

    async def poll(self):
        while self.is_running:
            updates = await self.store.vk_api.poll()
            for u in updates:
                if u.object.peer_id not in self._chat_queues:
                    queue = Queue()
                    self._chat_queues[u.object.peer_id] = queue
                    asyncio.create_task(self._worker(queue))
                self._chat_queues[u.object.peer_id].put_nowait(u)
