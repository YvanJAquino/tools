from asyncio import new_event_loop, run_coroutine_threadsafe
from threading import Thread, Lock


class ThreadedLoop(Thread):

    def __init__(self, *args, loop=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = 'ThreadedLoop'
        self.loop = loop or new_event_loop()
        self.lock = Lock()
        self.futures = []

    def terminate(self):
        for idx, fut in enumerate(self.futures):
            self.futures[idx] = fut.result()
        self.join()

    def __del__(self):
        if self.loop.is_running() and not self.loop.is_closed():
            self.terminate()

    def submit(self, coro):
        self.futures.append(run_coroutine_threadsafe(coro, loop=self.loop))
        return self.futures[-1]

    def run(self):
        self.loop.run_forever()

    def stop(self):
        self.loop.call_soon_threadsafe(self.loop.stop)
    
    def join(self):
        self.stop()
        super().join()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self.loop.is_running() and not self.loop.is_closed():
            self.terminate()

# if __name__ == '__main__':
#     async def write():
#         print('Hello from another thread!')
    
    
#     tl = ThreadedLoop()
#     tl.submit(write())
    