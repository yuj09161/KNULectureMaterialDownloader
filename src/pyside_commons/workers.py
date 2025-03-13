from PySide6.QtCore import Signal, QThread

import asyncio
import platform
import traceback
from multiprocessing import cpu_count

from .exception_bridge import ExceptionBridge


class _ThreadRunnerBase(QThread):
    ended = Signal(object)
    err_raised = Signal(object)

    def __init__(self, parent, workers_count=0):
        super().__init__(parent)

        if workers_count:
            self._workers_count = workers_count
        elif 'faked' in platform.release():
            self._workers_count = 4
        else:
            self._workers_count = cpu_count() * 2

    def start(self, *args, **kwargs) -> None:
        """
        Starts the worker(thread).

        The argument and keyword arguments will be passed to function runner.
        (Except "end" keyword argument, an argument that callback function.)

        Keyword args:
            end (Callable[[Any], Any], optional): The callback function.
            err (Dict, optional): The callback function.
                (Structure of err:
                    (root)\n
                    ├─(code) [int]\n
                    └─(func) [Callbale[[int], Any]]
                )
        """
        # pylint: disable=attribute-defined-outside-init
        try:
            self.ended.disconnect()
        except RuntimeError:
            pass
        if 'end' in kwargs:
            self.ended.connect(kwargs.pop('end'))
        if 'err' in kwargs:
            err = kwargs.pop('err')
            self._err_code = err['code']
            self.err_raised.connect(err['func'])
        else:
            self._err_code = None
        priority = kwargs.pop('priority', QThread.LowPriority)

        self._args = args
        self._kwargs = kwargs

        super().start(priority)

    def run(self) -> None:
        raise NotImplementedError


class ThreadRunner(_ThreadRunnerBase):
    """The thread runner abstract class."""

    def run(self) -> None:
        try:
            result = self.runner(*self._args, **self._kwargs)
        except Exception:  # pylint: disable = W0703
            ExceptionBridge().warning(
                '오류', '작업 중 알 수 없는 오류', traceback.format_exc()
            )
            if self._err_code is not None:
                self.err_raised.emit(self._err_code)
        else:
            self.ended.emit(result)

    def runner(self):
        raise NotImplementedError


class AsyncioThreadRunner(_ThreadRunnerBase):
    """The asyncio-function thread runner abstract class."""

    def run(self) -> None:
        try:
            result = asyncio.run(self.runner(*self._args, **self._kwargs))
        except Exception:  # pylint: disable = W0703
            ExceptionBridge().warning(
                '오류', '작업 중 알 수 없는 오류', traceback.format_exc()
            )
            if self._err_code is not None:
                self.err_raised.emit(self._err_code)
        else:
            self.ended.emit(result)

    async def runner(self):
        raise NotImplementedError
