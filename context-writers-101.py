from threadedloop import ThreadedLoop
from copy import deepcopy
from json import load, dump, JSONDecodeError
from abc import ABC, abstractmethod
import asyncio

from rich import print

class ContextWriter(ABC):

    def __init__(self, lim: int = 500):
        self.buf = []
        self.lim = lim
        self.loop = ThreadedLoop()

    @abstractmethod
    async def write(self):
        pass

    @abstractmethod
    def load(self, data):
        pass

    def add(self, data):
        self.load(data)
        if len(self.buf) >= self.lim:
            print('Buffer limit hit.  Writing out...')
            self.loop.submit(self.write())

    def __enter__(self):
        self.loop.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self.buf:
            print(f'Buffer still has {len(self.buf)} records.  Writing out...')
            self.loop.submit(self.write())
        self.loop.__exit__(exc_type, exc_value, exc_traceback)

    def __add__(self, data):
        self.add(data)


class DictWriter(ContextWriter):

    def __init__(self, out, lim: int = 500):
        super().__init__(lim=lim)
        self.out = out

    async def write(self):
        with self.loop.lock:
            cp = deepcopy(self.buf)
            self.buf = []
        self.out += cp

    def load(self, data):
        if isinstance(data, list):
            self.buf += data
        elif isinstance(data, dict):
            for key, val in data.items():
                self.buf.append({key: val})


class JSONWriter(ContextWriter):

    def __init__(self, fp, lim: int = 500):
        super().__init__(lim=lim)
        self.fp = fp
 
    async def write(self):
        with self.loop.lock:
            cp = deepcopy(self.buf)
            self.buf = []
        try:
            with open(self.fp, 'rb') as src:
                data = load(src)
        except (FileNotFoundError, JSONDecodeError):
            data = []
        await asyncio.sleep(3)
        data += cp
        with open(self.fp, 'w') as dest:
            dump(data, dest, indent=2)

    def load(self, data):
        if isinstance(data, list):
            self.buf += data
        elif isinstance(data, dict):
            for key, val in data.items():
                self.buf.append({key: val})


if __name__ == '__main__':
    inp = [
        {
            'key-' + str(x) : 'val-' + str(x)
            for x in range(25 * a , 25 * (a + 1))
        } for a in range(5)
    ]

    inp2 = [
        [
            {'key-' + str(x) : 'val-' + str(x)}
            for x in range(250 * a, 250 * (a+1))
        ] for a in range(11) 
    ]


    out = []

    with JSONWriter('j-writer.json', lim = 1000) as dw:
        for data in inp2:
            dw + data
            input(f'Total buffered records: {len(dw.buf)}.  Press enter!')
