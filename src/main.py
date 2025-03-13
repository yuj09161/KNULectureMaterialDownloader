# pylint: disable = import-error
from PySide6.QtCore import QTimer, Signal, QEvent
from PySide6.QtGui import QStandardItem
from PySide6.QtWidgets import (
    QApplication, QWidget, QMainWindow,
    QDialog, QFileDialog, QProgressDialog, QMessageBox
)

from configparser import ConfigParser
from collections.abc import Callable
from typing import Iterable
import os
import subprocess

import keyring

from UI import Ui_MainWin, Ui_LoginWin
from universal_main.universal_constants import (
    USER_DIR, DATADIR, PATHSEP, PROGRAM_DIR,
    IS_WINDOWS, IS_LINUX, IS_MACOS
)
from pyside_commons import ExceptionBridge
from models import Files, CanvasSubjectsModel
from workers import LectureMaterial, MaterialTypes
from workers.canvas import CanvasLoginWorker, CanvasSubjectGetter, CanvasFileInfoGetter
from workers.commons import FileDownloader
from workers.knu import KNUIdPwLoginWorker, KNULoginPushSender, KNUPushLoginWorker

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


class LoginWin(QDialog, Ui_LoginWin):
    __SERVICE_NAME = 'hys.LectureMaterialDownloader'

    succeeded = Signal(object, object)
    failed = Signal()

    def __init__(self, parent, config: ConfigParser):
        super().__init__(parent)
        self.setupUi(self)

        self.__config = config

        self.__result_sent = False

        self.__canvas_login_worker = CanvasLoginWorker(self)
        self.__knu_idpw_login_worker = KNUIdPwLoginWorker(self)
        self.__knu_login_push_sender = KNULoginPushSender(self)
        self.__knu_push_login_worker = KNUPushLoginWorker(self)

        self.rbIdPw.clicked.connect(self.__switch_to_idpw)
        self.rbPush.clicked.connect(self.__switch_to_push)

        self.lnUser.returnPressed.connect(lambda: self.lnPass.setFocus())
        self.lnPass.returnPressed.connect(self.__login)
        self.btnLogin.clicked.connect(self.__login)

        match self.__config['credentials'].getint('login_method'):
            case 0:
                self.rbIdPw.setChecked(True)
                # self.__switch_to_idpw()  # Useless
            case 1:
                self.rbPush.setChecked(True)
                self.__switch_to_push()

        if self.__config['credentials']['username']:
            self.chkSaveId.setChecked(True)
            self.lnUser.setText(self.__config['credentials']['username'])
            self.lnPass.setFocus()
        else:
            self.chkSaveId.setChecked(False)
            self.lnUser.setFocus()

        self.chkAutoLogin.setChecked(
            self.__config['credentials'].getboolean('auto_login')
        )

    def __switch_to_idpw(self):
        self.lnUser.returnPressed.disconnect()
        self.lnUser.returnPressed.connect(lambda: self.lnPass.setFocus())
        self.glLogin.removeWidget(self.lbUser)
        self.glLogin.removeWidget(self.lnUser)
        self.glLogin.addWidget(self.lbUser, 0, 0, 1, 1)
        self.glLogin.addWidget(self.lnUser, 0, 1, 1, 1)
        self.lbPass.show()
        self.lnPass.show()

    def __switch_to_push(self):
        self.lnUser.returnPressed.disconnect()
        self.lnUser.returnPressed.connect(self.__login)
        self.glLogin.removeWidget(self.lbUser)
        self.glLogin.removeWidget(self.lnUser)
        self.glLogin.addWidget(self.lbUser, 0, 0, 2, 1)
        self.glLogin.addWidget(self.lnUser, 0, 1, 2, 1)
        self.lbPass.hide()
        self.lnPass.hide()

    def __write_config(self):
        self.__config['credentials']['username'] =\
            self.lnUser.text() if self.chkSaveId.isChecked() else ''
        self.__config['credentials']['auto_login'] = str(self.chkAutoLogin.isChecked())
        self.__config['credentials']['login_method'] = str((
            self.rbIdPw.isChecked(), self.rbPush.isChecked()
        ).index(True))

        if self.chkAutoLogin.isChecked() and self.rbIdPw.isChecked():
            keyring.set_password(self.__SERVICE_NAME, self.lnUser.text(), self.lnPass.text())
        else:
            try:
                keyring.delete_password(self.__SERVICE_NAME, self.lnUser.text())
            except keyring.errors.PasswordDeleteError:
                pass

    def __auto_login(self):
        if self.rbIdPw.isChecked():
            try:
                password = keyring.get_password(self.__SERVICE_NAME, self.lnUser.text())
            except keyring.errors.KeyringError:
                QMessageBox.warning(
                    self, '키링 오류',
                    '키링 잠금 해제 실패\n암호 직접 입력 필요',
                    QMessageBox.Cancel
                )
            else:
                if password is None:
                    self.chkAutoLogin.setChecked(False)
                    QMessageBox.critical(
                        self, '암호 없음',
                        '자동 로그인이 활성화되었지만,\n암호가 저장되어 있지 않음',
                        QMessageBox.Cancel
                    )
                else:
                    self.lnPass.setText(password)
                    self.__login()
        else:  # self.rbPush.isChecked()
            self.__login()

    def __login(self):
        def error_cleanup():
            progress_dialog.reset()

        def push_sent(result: str):
            if not result['success']:
                progress_dialog.reset()
                QMessageBox.warning(self, '로그인 실패', f"{result['message']} ({result['code']})")
                return

            progress_dialog.setLabelText('승인 대기 중')
            match QMessageBox.information(
                self, '승인 필요',
                'KNUPIA 앱에서 로그인을 승인한 후, 확인 버튼을 눌러주세요',
                QMessageBox.Ok, QMessageBox.Cancel
            ):
                case QMessageBox.Ok:
                    progress_dialog.setLabelText('통합정보시스템 로그인 중')
                    self.__knu_push_login_worker.start(
                        self.lnUser.text(), result['trial'], end=on_knu_login
                    )
                case _:
                    progress_dialog.reset()

        def on_knu_login(result: dict[str, bool | str]):
            if result['success']:
                progress_dialog.setLabelText('Canvas 로그인 중')
                self.__canvas_login_worker.start(result['knu_session'], end=login_done, err=error_cleanup)
            else:
                QMessageBox.warning(self, '로그인 실패', f"{result['message']} ({result['code']})")
                progress_dialog.reset()

        def login_done(session_ids: dict[str, str]):
            self.succeeded.emit(session_ids['canvas_session'], session_ids['learningx_session'])
            self.__result_sent = True
            progress_dialog.reset()
            self.close()

        self.__write_config()

        if self.rbIdPw.isChecked():
            progress_dialog = QProgressDialog('통합정보시스템 로그인 중', None, 0, 0, self)
            self.__knu_idpw_login_worker.start(
                self.lnUser.text(), self.lnPass.text(),
                end=on_knu_login, err=error_cleanup
            )
            progress_dialog.exec()
        elif self.rbPush.isChecked():
            progress_dialog = QProgressDialog('KNUPIA 푸시 전송 중', None, 0, 0, self)
            self.__knu_login_push_sender.start(
                self.lnUser.text(),
                end=push_sent, err=error_cleanup
            )
            progress_dialog.exec()
        else:
            raise RuntimeError('No login method selected.')

    def showEvent(self, _):
        parent: QWidget = self.parent()
        self.setFixedHeight(self.height())
        self.move(
            parent.x() + (parent.width() - self.width()) // 2,
            parent.y() + (parent.height() - self.height()) // 2
        )
        if self.chkAutoLogin.isChecked():
            QTimer.singleShot(50, self.__auto_login)

    def closeEvent(self, event) -> None:
        self.__write_config()
        if not self.__result_sent:
            self.failed.emit()
        super().closeEvent(event)

class MainWin(QMainWindow, Ui_MainWin):
    __CONFIG_DIR = DATADIR + 'hys.LectureMaterialDownloader/'
    __CONFIG_FILE = __CONFIG_DIR + 'config.ini'

    download_result = Signal(QStandardItem, str)

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        ExceptionBridge(self)

        self.__config = ConfigParser()
        self.__load_config()

        self.__login_win = LoginWin(self, self.__config)

        self.__files = Files()
        self.__canvas_subjects = CanvasSubjectsModel()

        self.__canvas_session: str = ''
        self.__learningx_session: str = ''
        self.__all_subjects: dict[str, list[tuple[str, str]]] = {}

        # Workers
        self.__canvas_subject_getter = CanvasSubjectGetter(self)
        self.__canvas_file_info_getter = CanvasFileInfoGetter(self)
        self.__file_downloader = FileDownloader(self)

        self.tvFile.setModel(self.__files)
        self.cbSubject.setModel(self.__canvas_subjects)

        self.__login_win.succeeded.connect(self.__update_sessions)
        self.__login_win.failed.connect(self.close)

        self.cbSemester.currentIndexChanged.connect(self.__on_semester_changed)
        self.cbSubject.currentIndexChanged.connect(self.__on_subject_changed)

        self.tvFile.clicked.connect(self.__set_btn_select_text)

        self.btnOpenDst.clicked.connect(
            lambda: open_explorer(self.__config['download']['destination'])
        )
        self.btnSetDst.clicked.connect(self.__set_destination)

        self.btnSelect.clicked.connect(self.__select_or_unselect_all)
        self.btnReverse.clicked.connect(self.__reverse_selection)
        self.btnDownload.clicked.connect(self.__download)

        self.btnSetSubject.clicked.connect(self.__set_subject)

        self.download_result.connect(self.__on_download_result)

        self.__set_item_selection_selected(False)
        self.__set_subject_selection_enabled(False)

    # Display related functions
    def showEvent(self, event):
        if self.__canvas_session:
            assert self.__learningx_session
        else:
            QTimer.singleShot(50, lambda: self.__login_win.exec())
        return super().showEvent(event)

    def __set_subject_selection_enabled(self, state: bool):
        self.cbSubject.setEnabled(state)
        self.btnSetSubject.setEnabled(state)

    def __set_item_selection_selected(self, state: bool):
        self.btnSelect.setEnabled(state)
        self.btnReverse.setEnabled(state)
        self.btnDownload.setEnabled(state)

    def __on_semester_changed(self):
        self.__set_item_selection_selected(False)
        self.__files.clear()
        self.__canvas_subjects.set_subjects(self.__all_subjects[self.cbSemester.currentText()])

    def __on_subject_changed(self):
        self.__set_item_selection_selected(False)
        self.__files.clear()

    def __on_download_result(self, item: QStandardItem, progress: str):
        item.setText(progress)
    # end display

    def __set_destination(self):
        dst = QFileDialog.getExistingDirectory(
            self, '저장할 폴더 선택', self.__config['download']['destination']
        )
        if dst:
            self.__config['download']['destination'] = os.path.abspath(dst) + PATHSEP
            self.lbDst.setText(self.__config['download']['destination'][:-1])

    # Selection related functions
    def __select_or_unselect_all(self):
        if self.__files.all_selected:
            self.__files.clear_selection()
        else:
            self.__files.select_all()
        self.__set_btn_select_text()

    def __reverse_selection(self):
        self.__files.reverse_selection()
        self.__set_btn_select_text()

    def __set_btn_select_text(self, _ = None):
        self.btnSelect.setText(('모두 선택', '선택 해제')[self.__files.all_selected])
    # end selection

    # Canvas worker functions
    def __logout(self):
        def error_cleanup():
            self.__is_logined = False
            progress_dialog.reset()

        def end(result):
            self.__is_logined = False
            progress_dialog.reset()

        progress_dialog = QProgressDialog('로그아웃 중', None, 0, 0, self)
        progress_dialog.exec()

    def __set_subject(self):
        def error_cleanup():
            progress_dialog.reset()

        def end(materials: Iterable[LectureMaterial]):
            self.__files.clear()

            if not materials:
                QMessageBox.information(self, '강의자료 없음', '해당 과목의 강의자료 없음')
                progress_dialog.reset()
                return

            for name, type, url in materials:
                self.__files.add_data(name, type, url)
            for k in range(self.__files.columnCount()):
                self.tvFile.resizeColumnToContents(k)
            self.__set_item_selection_selected(True)
            progress_dialog.reset()

        progress_dialog = QProgressDialog('강의자료 목록 가져오는 중', None, 0, 0, self)
        self.__canvas_file_info_getter.start(
            self.__canvas_session,
            self.__learningx_session,
            self.__canvas_subjects.get_current_id(
                self.cbSubject.currentIndex()
            ),
            end=end,
            err=error_cleanup
        )
        progress_dialog.exec()
    # end Canvas

    def __update_sessions(self, canvas_session: str, learningx_session: str):
        def error_cleanup():
            progress_dialog.reset()

        def end(subjects: dict[str, list[tuple[str, str]]]):
            if not subjects:
                QMessageBox.information(self, '과목 없음', '수강중인 과목이 없음')
                progress_dialog.reset()
                return

            self.__all_subjects = subjects
            self.cbSemester.addItems(sorted(subjects.keys()))
            self.cbSemester.setCurrentIndex(len(subjects) - 1)
            self.__canvas_subjects.set_subjects(subjects[self.cbSemester.currentText()])
            self.__set_subject_selection_enabled(True)

            progress_dialog.reset()

        def refresh_subjects():
            self.__canvas_subject_getter.start(
                self.__canvas_session,
                end=end,
                err=error_cleanup
            )
            self.__canvas_subjects.clear()
            progress_dialog.exec()

        progress_dialog = QProgressDialog('과목 조회 중', None, 0, 0, self)

        self.__canvas_session = canvas_session
        self.__learningx_session = learningx_session

        QTimer.singleShot(10, refresh_subjects)

    # Common workers
    def __download(self):
        def error_cleanup():
            progress_dialog.reset()

        def end(download_results):
            self.__files.set_result(download_results)
            progress_dialog.reset()

        def new_callback(index: int) -> Callable[[str], None]:
            def inner(progress: str):
                self.download_result.emit(self.__files.item(index, 4), progress)
            return inner

        selected: Iterable[tuple[int, str, MaterialTypes, str]] = self.__files.info_of_selected
        if not selected:
            QMessageBox.information(self, '알림', '선택된 파일이 없음')
            return

        progress_dialog = QProgressDialog('강의자료 다운로드 중', None, 0, 0, self)
        works = [(name, type_, url, new_callback(idx)) for idx, name, type_, url in selected]
        self.__file_downloader.start(
            works, self.__config['download']['destination'], end=end, err=error_cleanup
        )
        progress_dialog.exec()

    def __load_default_config(self):
        self.__config['download'] = {
            'destination': USER_DIR
        }
        self.__config['credentials'] = {
            'username': '',
            'auto_login': 'False',
            'login_method': '0'
        }

    def __load_config(self):
        if os.path.isfile(self.__CONFIG_FILE):
            self.__config.read(self.__CONFIG_FILE)
        else:
            self.__load_default_config()
        self.lbDst.setText(self.__config['download']['destination'])

    def __save_config(self):
        os.makedirs(self.__CONFIG_DIR, exist_ok=True)
        with open(self.__CONFIG_FILE, 'w', encoding='utf-8') as file:
            self.__config.write(file)
    # end Common workers

    def closeEvent(self, event: QEvent):
        # self.__logout()
        self.__save_config()
        event.accept()


def main(app):
    main_win = MainWin()
    main_win.show()

    app.exec()


if __name__ == '__main__':
    app = QApplication()
    main(app)
