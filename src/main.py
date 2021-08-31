from PySide6.QtWidgets import (
    QApplication, QMainWindow,
    QFileDialog, QMessageBox
)

import os
import subprocess
from typing import Union

import requests

from UI import Ui_MainWin
from constants import USER_DIR, PATHSEP, IS_WINDOWS, IS_LINUX, IS_MACOS
from models import Files
from workers import (
    LoginWorker, SubjectGetter, SubjectSetter, FileinfoGetter, FileDownloader
)


os.chdir(os.path.dirname(os.path.abspath(__file__)))


def open_explorer(path):
    if IS_WINDOWS:
        subprocess.Popen(
            ['explorer', path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
    elif IS_LINUX:
        subprocess.Popen(
            ['xdg-open', path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
    elif IS_MACOS:
        subprocess.Popen(
            ['open', path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )


class MainWin(QMainWindow, Ui_MainWin):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.__files = Files()
        self.__session = requests.Session()

        self.__dst = USER_DIR
        self.__user_info = None
        self.__stu_id = ''
        self.__subj_code = ''
        self.__subj_name = ''
        self.__index_to_code = None

        self.__login_worker = LoginWorker(self)
        self.__subject_getter = SubjectGetter(self)
        self.__subject_setter = SubjectSetter(self)
        self.__fileinfo_worker = FileinfoGetter(self)
        self.__file_downloader = FileDownloader(self)

        self.__set_download_enabled(False)
        self.__set_subj_enabled(False)

        self.lbDst.setText('저장 위치: ' + self.__dst[:-1])
        self.tvFile.setModel(self.__files)

        self.tvFile.clicked.connect(self.__set_btnSelect_text)
        self.lnId.returnPressed.connect(self.__login)

        self.btnOpenDst.clicked.connect(lambda: open_explorer(self.__dst))
        self.btnSetDst.clicked.connect(self.__set_dst)
        self.btnSelect.clicked.connect(self.__select)
        self.btnReverse.clicked.connect(self.__reverse_selection)
        self.btnDownload.clicked.connect(self.__download)
        self.btnLogin.clicked.connect(self.__login)
        self.btnSetSmst.clicked.connect(self.__get_subject)
        self.btnSetSubj.clicked.connect(self.__set_subject)

    def __set_download_enabled(self, state: bool):
        self.btnSelect.setEnabled(state)
        self.btnReverse.setEnabled(state)
        self.btnDownload.setEnabled(state)

    def __set_subj_enabled(self, state: bool):
        self.spinYear.setEnabled(state)
        self.cbSemester.setEnabled(state)
        self.cbSubject.setEnabled(state)
        self.btnSetSmst.setEnabled(state)
        self.btnSetSubj.setEnabled(state)

    def __start_work(self, msg: str):
        self.btnSetDst.setEnabled(False)
        self.__set_download_enabled(False)
        self.__set_subj_enabled(False)
        self.btnLogin.setEnabled(False)

        self.statusbar.showMessage(msg)
        self.pg.setRange(0, 0)

    def __end_work(self):
        self.pg.setRange(0, 1)
        self.statusbar.clearMessage()

        self.btnSetDst.setEnabled(True)
        self.__set_download_enabled(True)
        self.__set_subj_enabled(True)
        self.btnLogin.setEnabled(True)

    def __set_dst(self):
        dst = QFileDialog.getExistingDirectory(
            self, '저장할 폴더 선택', self.__dst
        )
        if dst:
            self.__dst = os.path.abspath(dst) + PATHSEP
            self.lbDst.setText('저장 위치: ' + self.__dst[:-1])

    def __select(self):
        if self.__files.all_selected:
            self.__files.clear_selection()
            self.__set_btnSelect_text(False)
        else:
            self.__files.select_all()
            self.__set_btnSelect_text(True)

    def __set_btnSelect_text(self, arg: Union[int, bool]):
        if not isinstance(arg, bool):
            is_all_selected = arg.column() == 0 and self.__files.all_selected
        else:
            is_all_selected = arg
        self.btnSelect.setText('선택 해제' if is_all_selected else '모두 선택')

    def __reverse_selection(self):
        self.__files.reverse_selection()
        self.__set_btnSelect_text(self.__files.all_selected)

    def __login(self):
        def end(response):
            self.__end_work()
            self.__set_download_enabled(False)
            self.__files.clear()
            is_error = response['isError']
            if is_error:
                self.__set_subj_enabled(False)
                self.gbLogin.setTitle('로그인 상태: 로그인 실패')
                QMessageBox.warning(self, '로그인 실패', response['message'])
            else:
                self.cbSubject.setEnabled(False)
                self.btnSetSubj.setEnabled(False)
                self.gbLogin.setTitle('로그인 상태: 로그인됨')

        self.__start_work('로그인 중')
        self.__login_worker.start(
            self.__session, self.lnUser.text(), self.lnPass.text(), end=end
        )

    def __get_subject(self):
        def end(response):
            self.__end_work()
            self.__set_download_enabled(False)
            self.__files.clear()
            subject_names, subject_codes = response
            if subject_names and subject_codes:
                self.__index_to_code = subject_names
                self.cbSubject.addItems(subject_codes)
            else:
                self.__index_to_code = []
                self.cbSubject.setEnabled(False)
                self.btnSetSubj.setEnabled(False)
                QMessageBox.warning(
                    self, '과목 조회 실패',
                    '해당 학기에 조회된 수강과목 없음'
                )

        self.__start_work('과목 조회 중')
        self.__index_to_code = []
        self.cbSubject.clear()
        self.__subject_getter.start(
            self.__session, self.spinYear.value(),
            self.cbSemester.currentIndex(),
            end=end
        )

    def __set_subject(self):
        def end(response):
            is_error = response['isError']
            self.__files.clear()
            if is_error:
                self.__end_work()
                self.__subj_code = ''
                self.__subj_name = ''
                self.gbSubject.setTitle('과목명: 설정 안 됨')
                self.__set_download_enabled(False)
                QMessageBox.warning(self, '과목 설정 실패', response['message'])
            else:
                self.__subj_code = subj_code
                self.__subj_name = self.cbSubject.currentText()
                self.gbSubject.setTitle(f'과목명: {self.__subj_name}')
                self.__get_info_of_files()

        self.__start_work('강의 들어가는 중')
        subj_code = self.__index_to_code[self.cbSubject.currentIndex()]
        self.__subject_setter.start(self.__session, subj_code, end=end)

    def __get_info_of_files(self):
        def end(datas):
            for data in datas:
                self.__files.add_data(*data)
            for k in range(self.__files.columnCount()):
                self.tvFile.resizeColumnToContents(k)
            self.__end_work()

        self.__start_work('강의자료 목록 가져오는 중')
        self.__fileinfo_worker.start(
            self.__session, self.lnId.text(),
            self.__index_to_code[self.cbSubject.currentIndex()],
            end=end
        )

    def __download(self):
        def end(results):
            self.__files.set_result(results)
            self.__end_work()

        selected = self.__files.get_selected()
        if selected:
            self.__start_work('강의자료 다운로드 중')
            self.__file_downloader.start(
                self.__session, selected, self.__dst, end=end
            )
        else:
            QMessageBox.information(
                self, '알림', '선택된 파일이 없음'
            )


def main():
    app = QApplication()

    main_win = MainWin()
    main_win.show()

    app.exec()


if __name__ == '__main__':
    main()
