from PySide6.QtCore import Signal, QThread

from multiprocessing import cpu_count
import asyncio
import platform
import traceback
import warnings

from .exception_bridge import ExceptionBridge


class _ThreadRunnerBase(QThread):
    ended = Signal(object)
    err_raised = Signal()

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
            err (Callbale[[], Any]): The error callback function.
        """
        # pylint: disable=attribute-defined-outside-init
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=RuntimeWarning)
            try:
                self.ended.disconnect()
            except RuntimeError:
                pass
            try:
                self.err_raised.disconnect()
            except RuntimeError:
                pass
        if 'end' in kwargs:
            self.ended.connect(kwargs.pop('end'))
        if 'err' in kwargs:
            self.err_raised.connect(kwargs.pop('err'))
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
            self.err_raised.emit()
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
            self.err_raised.emit()
        else:
            self.ended.emit(result)

    async def runner(self):
        raise NotImplementedError
