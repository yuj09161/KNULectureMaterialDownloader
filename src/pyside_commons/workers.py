from PySide6.QtCore import Signal, QThread

import asyncio
from multiprocessing import cpu_count


class _ThreadRunnerBase(QThread):
    ended = Signal(object)

    def __init__(self, parent, workers_count=0):
        super().__init__(parent)

        self._workers_count = \
            workers_count if workers_count else min(cpu_count() * 2, 16)

    def start(self, *args, **kwargs) -> None:
        """
        Starts the worker(thread).

        The argument and keyword arguments will be passed to function runner.
        (Except "end" keyword argument, an argument that callback function.)

        Keyword args:
            end (Callable, optional): The callback function.
        """
        # pylint: disable=attribute-defined-outside-init
        try:
            self.ended.disconnect()
        except RuntimeError:
            pass
        if 'end' in kwargs:
            self.ended.connect(kwargs.pop('end'))
        priority = kwargs.pop('priority', QThread.LowPriority)

        self._args = args
        self._kwargs = kwargs

        super().start(priority)

    def run(self) -> None:
        raise NotImplementedError


class ThreadRunner(_ThreadRunnerBase):
    """The thread runner abstract class."""

    def run(self) -> None:
        self.ended.emit(self.runner(*self._args, **self._kwargs))

    def runner(self):
        raise NotImplementedError


class AsyncioThreadRunner(_ThreadRunnerBase):
    """The asyncio-function thread runner abstract class."""

    def run(self) -> None:
        self.ended.emit(
            asyncio.run(self.runner(*self._args, **self._kwargs))
        )

    async def runner(self):
        raise NotImplementedError
