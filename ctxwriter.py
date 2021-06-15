from rich import print
from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Union
from threading import Thread, Lock
from json import load, dump, JSONDecodeError


class ContextThreadWriter(ABC):

    def __init__(self, lim: int = 500):
        self.lim = lim
        self.buf = []
        self.lock = Lock()
        self.ths = []

    @abstractmethod
    def write(self, cp):
        pass

    def load(self, dat: Union[list, tuple]):
        if not isinstance(dat, (list, tuple)):
            raise TypeError
        self.buf += dat

    def _safe_copy_and_write(self):
        with self.lock:
            cp = deepcopy(self.buf)
            self.buf.clear()
        self.write(cp)

    def _write(self, *args, **kwargs):
        th = Thread(target=self._safe_copy_and_write, args=args, kwargs=kwargs)
        self.ths.append(th)
        self.ths[-1].start()

    def _add(self, dat: Union[list, tuple]):
        self.load(dat)
        if len(self.buf) >= self.lim:
            print('Buffer limit met.  Writing.')
            self._write()

    def add(self, dat: Union[list, tuple]):
        self._add(dat)
    
    def __add__(self, dat: Union[list, tuple]):
        self._add(dat)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self.buf:
            print('Buffer not empty.  Writing.')
            self._write()
        for th in self.ths:
            th.join()
