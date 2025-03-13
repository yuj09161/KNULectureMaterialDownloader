from PySide6.QtCore import QCoreApplication

import os
import traceback

from .exception_bridge import ExceptionBridge


class OnlyOneInstance:
    def __init__(self, lockfile_path: str):
        self.__lockfile_path = lockfile_path

    def __enter__(self):
        try:
            self.__lockfile = open(self.__lockfile_path, 'x', encoding='utf-8')
        except FileExistsError:
            with open(self.__lockfile_path, 'r', encoding='utf-8') as file:
                pid = file.read()
            ExceptionBridge().fatal(
                '오류', '이미 프로그램의 다른 인스턴스가 실행 중', (
                    f'실행중인 인스턴스의 PID: {pid}\n'
                    '파일을 강제로 삭제하는 것은 권장하지 않음.\n'
                    '단, 프로그램이 직전에 강제 종료된 경우, '
                    'lockfile이 정상적으로 삭제되지 않았을 수 있음\n'
                ), 1
            )
            QCoreApplication.exec()
        else:
            self.__lockfile.write(str(os.getpid()))
            self.__lockfile.flush()

    def __exit__(self, exc_type, exc_value, tb):
        self.__lockfile.close()
        os.remove(self.__lockfile_path)
        if exc_type is not None:
            ExceptionBridge().warning(
                '오류', (
                    '프로그램 실행 중 처리되지 않은 오류\n'
                    '프로그램 종료될 수 있음'
                ), ''.join(traceback.format_exception(exc_type, exc_value, tb))
            )
            return False
