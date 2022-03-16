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
        self._chat_queues: Dict[int, Queue] = {}
        self._workers: List[Task] = []
        self._concurrent_workers = 0

    async def start(self):
        self.is_running = True
        self.poll_task = asyncio.create_task(self.poll())

    async def stop(self):
        self.is_running = False
        for worker in self._workers:
            worker.cancel()
        await asyncio.gather(*self._workers, return_exceptions=True)
        self.poll_task.cancel()

    async def _worker(self, queue):
        while True:
            upd = await queue.get()
            await self.store.bots_manager.handle_updates(upd)
            queue.task_done()

    async def poll(self):
        while self.is_running:
            updates = await self.store.vk_api.poll()
            for u in updates:
                if u.object.peer_id not in self._chat_queues:
                    queue = Queue()
                    self._chat_queues[u.object.peer_id] = queue
                    self._workers.append(
                        asyncio.create_task(self._worker(queue))
                    )
                self._chat_queues[u.object.peer_id].put_nowait(u)
