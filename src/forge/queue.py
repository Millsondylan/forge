import asyncio
from collections import deque

class TaskQueue:
    def __init__(self):
        self.queue = deque()

    async def add(self, task):
        self.queue.append(task)

    async def get(self):
        while not self.queue:
            await asyncio.sleep(0.1)
        return self.queue.popleft()
