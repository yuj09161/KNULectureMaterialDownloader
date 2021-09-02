from PySide6.QtCore import QThread, Signal

from multiprocessing import cpu_count


CPU_CNT = cpu_count()

HEADER = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/99.0.7113.93 Safari/537.36'
    )
}


class BaseRunner(QThread):
    ended = Signal(object)

    def __init__(self, parent, runner_cnt=0, runner=None):
        super().__init__(parent)

        self.runner_cnt = (
            runner_cnt if runner_cnt else min(CPU_CNT * 2, 16)
        )
        if runner:
            self._workers = [runner(self) for _ in range(self.runner_cnt)]

    def start(self, *args, **kwargs):
        # pylint: disable=attribute-defined-outside-init
        try:
            self.ended.disconnect()
        except RuntimeError:
            pass
        if 'end' in kwargs:
            self.ended.connect(kwargs.pop('end'))
        priority = kwargs.pop('priority', QThread.LowPriority)

        self.__args = args
        self.__kwargs = kwargs

        super().start(priority)

    def run(self):
        self.ended.emit(self.runner(*self.__args, **self.__kwargs))


class FileDownloader(BaseRunner):
    def runner(self, session, selected_files, dst):
        results = []
        for name, url in selected_files:
            response = session.get(url, headers=HEADER)
            if response.status_code == 200:
                results.append('성공')
                with open(dst + name, 'wb') as file:
                    file.write(response.content)
            else:
                results.append('실패')
        return results
