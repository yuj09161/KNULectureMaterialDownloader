# pylint: disable = import-error

from PySide6.QtWidgets import QMainWindow, QFileDialog, QMessageBox

import os
import datetime
import subprocess
from typing import Union
from enum import Enum, auto

import requests

from UI import Ui_MainWin
from universal_main.universal_constants import (
    USER_DIR, DATADIR, PATHSEP, PROGRAM_DIR,
    IS_WINDOWS, IS_LINUX, IS_MACOS
)
from models import Files, HelloLMSSubjectsModel, CanvasSubjectsModel
from workers.commons import FileDownloader
from workers.hellolms import (
    LoginWorker as HelloLoginWorker,
    SubjectGetter as HelloSubjectGetter,
    SubjectSetter as HelloSubjectSetter,
    FileinfoGetter as HelloFileinfoGetter
)
from workers.canvas import (
    SubjectGetter as CanvasSubjectGetter,
    FileinfoGetter as CanvasFileinfoGetter
)

os.chdir(PROGRAM_DIR)


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


class _DownloadSource(Enum):
    HelloLMS = auto()
    Canvas = auto()


class MainWin(QMainWindow, Ui_MainWin):
    __CFG_DIR = DATADIR + 'hys.LectureMaterialDownloader/'
    __CFG_FILE = __CFG_DIR + 'config'

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.__files = Files()
        self.__hellolms_subjects = HelloLMSSubjectsModel()
        self.__canvas_subjects = CanvasSubjectsModel()

        self.__dst = USER_DIR
        self.__download_source = None
        self.__session = requests.Session()

        # common worker
        self.__file_downloader = FileDownloader(self)

        # hellolms worker
        self.__hello_login_worker = HelloLoginWorker(self)
        self.__hello_subject_getter = HelloSubjectGetter(self)
        self.__hello_subject_setter = HelloSubjectSetter(self)
        self.__hello_fileinfo_worker = HelloFileinfoGetter(self)

        # canvas lms worker
        self.__canvas_subject_getter = CanvasSubjectGetter(self)
        self.__canvas_fileinfo_worker = CanvasFileinfoGetter(self)

        self.tvFile.setModel(self.__files)

        self.cbSemester.currentIndexChanged.connect(self.__after_smst_change)
        self.cbSubject.currentIndexChanged.connect(self.__after_subj_change)

        self.rbHellolms.clicked.connect(self.__switch_to_hellolms)
        self.rbCanvas.clicked.connect(self.__switch_to_canvas)

        self.tvFile.clicked.connect(self.__set_btnSelect_text)

        self.lbDst.clicked.connect(lambda: open_explorer(self.__dst))
        self.btnSetDst.clicked.connect(self.__set_dst)
        self.btnSelect.clicked.connect(self.__select)
        self.btnReverse.clicked.connect(self.__reverse_selection)
        self.btnDownload.clicked.connect(self.__download)
        self.btnLogin.clicked.connect(self.__login)
        self.btnSetSmst.clicked.connect(self.__get_subject)
        self.btnSetSubj.clicked.connect(self.__set_subject)

        self.__switch_to_hellolms()
        self.__guess_semester()
        self.__load_config()

        self.rbHellolms.setChecked(True)

    # Display related functions
    def __guess_semester(self):
        today = datetime.date.today()
        self.spinYear.setValue(today.year)
        self.cbSemester.setCurrentIndex(2 * (today.month > 7))

    def __set_sourcerb_enabled(self, state: bool):
        self.rbHellolms.setEnabled(state)
        self.rbCanvas.setEnabled(state)

    def __set_download_enabled(self, state: bool):
        self.btnSelect.setEnabled(state)
        self.btnReverse.setEnabled(state)
        self.btnDownload.setEnabled(state)

    def __set_smst_enabled(self, state: bool):
        self.spinYear.setEnabled(state)
        self.cbSemester.setEnabled(state)
        self.btnSetSmst.setEnabled(state)

    def __set_subj_enabled(self, state: bool):
        self.cbSubject.setEnabled(state)
        self.btnSetSubj.setEnabled(state)

    def __set_login_lineedit_enabled(self, state: bool):
        enable_user = \
            state and self.__download_source == _DownloadSource.HelloLMS
        self.lnUser.setEnabled(enable_user)
        self.lnPass.setEnabled(enable_user)
        self.lnId.setEnabled(state)

    def __set_login_state(self, state: bool):
        self.__files.clear()
        self.__set_download_enabled(False)
        self.__set_subj_enabled(False)
        if state:
            self.__set_smst_enabled(True)
            self.__set_login_lineedit_enabled(False)
            self.btnLogin.setText('로그아웃')
            try:
                self.btnLogin.clicked.disconnect()
            except RuntimeError:
                pass
            self.btnLogin.clicked.connect(
                lambda: self.__set_login_state(False)
            )
        else:
            self.__set_smst_enabled(False)
            self.__set_login_lineedit_enabled(True)
            self.lnUser.clear()
            self.lnPass.clear()
            self.lnId.clear()
            self.btnLogin.setText('로그인')
            try:
                self.btnLogin.clicked.disconnect()
            except RuntimeError:
                pass
            self.btnLogin.clicked.connect(self.__login)

    def __start_work(self, msg: str):
        self.__set_sourcerb_enabled(False)
        self.__set_download_enabled(False)
        self.__set_smst_enabled(False)
        self.__set_subj_enabled(False)
        self.btnLogin.setEnabled(False)

        self.statusbar.showMessage(msg)
        self.pg.setRange(0, 0)

    def __end_work(self):
        self.pg.setRange(0, 1)
        self.statusbar.clearMessage()

        self.__set_sourcerb_enabled(True)
        self.__set_download_enabled(True)
        self.__set_smst_enabled(True)
        self.__set_subj_enabled(True)
        self.btnLogin.setEnabled(True)

    def __after_smst_change(self):
        self.__set_subj_enabled(False)
        self.cbSubject.clear()

    def __after_subj_change(self):
        self.__set_download_enabled(False)
        self.__files.clear()
    # end display

    # Source setting related functions
    def __switch_to_hellolms(self):
        if self.__download_source != _DownloadSource.HelloLMS:
            self.lbUser.setText('LMS 사용자명')
            self.lbPass.setText('LMS 비밀번호')
            self.lbId.setText('학번')

            self.cbSubject.setModel(self.__hellolms_subjects)
            self.lnId.returnPressed.connect(self.__login)
            self.lnId.setEnabled(True)
            try:
                self.lnPass.returnPressed.disconnect()
            except RuntimeError:
                pass
            self.__download_source = _DownloadSource.HelloLMS
            self.__set_login_state(False)

    def __switch_to_canvas(self):
        if self.__download_source != _DownloadSource.Canvas:
            self.lbUser.setText(f"{'-':^11}")
            self.lbPass.setText(f"{'-':^11}")
            self.lbId.setText('Access Token')

            self.cbSubject.setModel(self.__canvas_subjects)
            self.lnId.setEnabled(False)
            try:
                self.lnId.returnPressed.disconnect()
            except RuntimeError:
                pass
            self.lnPass.returnPressed.connect(self.__login)
            self.__download_source = _DownloadSource.Canvas
            self.__set_login_state(False)
    # end source

    def __set_dst(self):
        dst = QFileDialog.getExistingDirectory(
            self, '저장할 폴더 선택', self.__dst
        )
        if dst:
            self.__dst = os.path.abspath(dst) + PATHSEP
            self.lbDst.setText(self.__dst[:-1])

    # Selection related functions
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
    # end selection

    # HelloLMS worker functions
    def __hello_login(self):
        def end(response):
            self.__end_work()
            is_error = response['isError']
            if is_error:
                self.__set_login_state(False)
                self.gbLogin.setTitle('로그인 상태: 로그인 실패')
                QMessageBox.warning(self, '로그인 실패', response['message'])
            else:
                self.__set_login_state(True)
                self.gbLogin.setTitle('로그인 상태: 로그인됨')

        self.__start_work('로그인 중')
        self.__hello_login_worker.start(
            self.__session, self.lnUser.text(), self.lnPass.text(), end=end
        )

    def __hello_get_subject(self):
        def end(subjects):
            self.__end_work()
            self.__set_download_enabled(False)
            if subjects:
                self.__hellolms_subjects.set_subjects(subjects)
            else:
                self.__set_subj_enabled(False)
                QMessageBox.warning(
                    self, '과목 조회 실패',
                    '해당 학기에 조회된 수강과목 없음'
                )

        self.__start_work('과목 조회 중')
        self.__hellolms_subjects.clear()
        self.__hello_subject_getter.start(
            self.__session, self.spinYear.value(),
            self.cbSemester.currentIndex(),
            end=end
        )

    def __hello_set_subject(self):
        def end(response):
            is_error = response['isError']
            if is_error:
                self.__end_work()
                self.gbSubject.setTitle('과목명: 설정 안 됨')
                self.__set_download_enabled(False)
                QMessageBox.warning(self, '과목 설정 실패', response['message'])
            else:
                self.__files.clear()
                self.gbSubject.setTitle(f'과목명: {self.cbSubject.currentText()}')
                self.__hello_get_info_of_files()

        self.__start_work('강의 들어가는 중')
        subj_code = self.__hellolms_subjects.get_current_code(
            self.cbSubject.currentIndex()
        )
        self.__hello_subject_setter.start(self.__session, subj_code, end=end)

    def __hello_get_info_of_files(self):
        def end(datas):
            self.__end_work()
            if not datas:
                self.__set_download_enabled(False)
                QMessageBox.information(
                    self, '강의자료 없음', '해당 과목의 강의자료 없음'
                )
            else:
                for data in datas:
                    self.__files.add_data(*data)
                for k in range(self.__files.columnCount()):
                    self.tvFile.resizeColumnToContents(k)

        self.__start_work('강의자료 목록 가져오는 중')
        subj_code = self.__hellolms_subjects.get_current_code(
            self.cbSubject.currentIndex()
        )
        self.__hello_fileinfo_worker.start(
            self.__session, self.lnId.text(), subj_code,
            end=end
        )
    # end HelloLMS

    # Canvas worker functions
    def __canvas_login(self):
        def end(result):
            self.__end_work()
            if isinstance(result, list):
                self.__set_login_state(True)
                self.__set_subj_enabled(True)
                self.gbLogin.setTitle('로그인 상태: 로그인됨')
                if not result:
                    QMessageBox.warning(
                        self, '과목 없음', '현재 학기에 조회된 과목 없음'
                    )
                else:
                    self.__canvas_subjects.set_subjects(result)
            else:
                self.__set_login_state(False)
                QMessageBox.warning(self, '과목 조회 실패', result)

        self.__start_work('로그인 정보 확인(과목 조회) 중')
        self.__canvas_subject_getter.start(
            f'{self.spinYear.value()}년', self.cbSemester.currentText(),
            self.lnId.text(),
            end=end
        )

    def __canvas_get_subject(self):
        def end(result):
            if isinstance(result, list):
                if not result:
                    QMessageBox.warning(
                        self, '과목 없음', '해당 학기에 조회된 과목 없음'
                    )
                else:
                    self.__canvas_subjects.set_subjects(result)
            else:
                QMessageBox.warning(self, '과목 조회 실패', result)
            self.__end_work()

        self.__start_work('과목 조회 중')
        self.__canvas_subject_getter.start(
            f'{self.spinYear.value()}년', self.cbSemester.currentText(),
            self.lnId.text(),
            end=end
        )

    def __canvas_get_info_of_files(self):
        def end(result):
            self.__end_work()
            if isinstance(result, list):
                if not result:
                    self.__set_download_enabled(False)
                    QMessageBox.information(
                        self, '강의자료 없음', '해당 과목의 강의자료 없음'
                    )
                else:
                    for data in result:
                        self.__files.add_data(*data)
                    for k in range(self.__files.columnCount()):
                        self.tvFile.resizeColumnToContents(k)
            else:
                self.__set_download_enabled(False)
                QMessageBox.warning(self, '파일 가져오기 실패', result)

        self.__start_work('강의자료 목록 가져오는 중')
        self.__canvas_fileinfo_worker.start(
            self.lnId.text(), self.__canvas_subjects.get_current_id(
                self.cbSubject.currentIndex()
            ), end=end
        )
    # end Canvas

    # Worker switcher functions
    def __login(self):
        if self.__download_source == _DownloadSource.HelloLMS:
            self.__hello_login()
        elif self.__download_source == _DownloadSource.Canvas:
            self.__canvas_login()
        else:
            raise ValueError(f'Invalid source: {self.__download_source}')

    def __get_subject(self):
        if self.__download_source == _DownloadSource.HelloLMS:
            self.__hello_get_subject()
        elif self.__download_source == _DownloadSource.Canvas:
            self.__canvas_get_subject()
        else:
            raise ValueError(f'Invalid source: {self.__download_source}')

    def __set_subject(self):
        if self.__download_source == _DownloadSource.HelloLMS:
            self.__hello_set_subject()
        elif self.__download_source == _DownloadSource.Canvas:
            self.__canvas_get_info_of_files()
        else:
            raise ValueError(f'Invalid source: {self.__download_source}')
    # end switchers

    # Common workers
    def __download(self):
        def end(results):
            self.__files.set_result(results)
            self.__end_work()
            self.btnSetDst.setEnabled(True)

        selected = self.__files.info_of_selected
        if selected:
            self.btnSetDst.setEnabled(False)
            self.__start_work('강의자료 다운로드 중')
            self.__file_downloader.start(
                self.__session, selected, self.__dst, end=end
            )
        else:
            QMessageBox.information(
                self, '알림', '선택된 파일이 없음'
            )

    # def __load_default_config(self):

    def __load_config(self):
        if os.path.isfile(self.__CFG_FILE):
            with open(self.__CFG_FILE, 'r', encoding='utf-8') as file:
                self.__dst = file.read()
        # else:
        # self.__load_default_config()

        self.lbDst.setText(self.__dst[:-1])

    def __save_config(self):
        if not os.path.isdir(self.__CFG_DIR):
            os.makedirs(self.__CFG_DIR)

        with open(self.__CFG_FILE, 'w', encoding='utf-8') as file:
            file.write(self.__dst)

    def closeEvent(self, event):
        self.__save_config()
        event.accept()
    # end Common workers


def main(app):
    main_win = MainWin()
    main_win.show()

    app.exec()


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication

    app = QApplication()
    main(app)
