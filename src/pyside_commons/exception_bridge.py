from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QMessageBox

import sys


NL = '\n'


class ExceptionBridge(QObject):
    """Bridge exception in worker thread to MessageBox of main window.
    """
    _instance = None
    _inited = False
    _parent_setted = False
    __warning_sig = Signal(str, str, str)
    __error_sig = Signal(str, str, str)
    __fatal_sig = Signal(str, str, str, int)

    def __new__(cls, parent=None):
        instance = cls._instance
        if not instance:
            if not parent and (sys.stdout is None or not sys.stdout.isatty()):
                raise ValueError(
                    'Class is not initialized, and parent is not given.'
                )
            instance = cls._instance = super().__new__(cls, parent)
        return instance

    def __init__(self, parent=None):
        if not self._inited:
            super().__init__(parent)
            self.__parent = parent
            if parent:
                self.__warning_sig.connect(self.__show_warning)
                self.__error_sig.connect(self.__show_error)
                self.__fatal_sig.connect(self.__show_fatal)
                self._parent_setted = True
            else:
                print(
                    'Warning: '
                    'Class is not initialized, and parent is not given.\n'
                    'Initalizing with console mode...'
                )
                self.__warning_sig.connect(self.__print_warning)
                self.__error_sig.connect(self.__print_error)
                self.__fatal_sig.connect(self.__print_fatal)
            self._inited = True
        elif parent is not None:  # Change parent
            self.setParent(parent)
            self.__parent = parent
            if not self._parent_setted:
                self.__warning_sig.disconnect()
                self.__error_sig.disconnect()
                self.__fatal_sig.disconnect()
                self.__warning_sig.connect(self.__show_warning)
                self.__error_sig.connect(self.__show_error)
                self.__fatal_sig.connect(self.__show_fatal)
                self._parent_setted = True

    def warning(self, title: str, text: str, detail: str = '') -> None:
        """Show warning dialog.

        Args:
            title (str): Title of warning dialog.
            text (str): Text of warning dialog.
            detail (str, optional): Detailed information of warning dialog.
                (If not given, 'Show Detail' button will not display.)
        """
        self.__warning_sig.emit(title, text, detail)

    def error(self, title: str, text: str, detail: str = '') -> None:
        """Show error dialog.

        Args:
            title (str): Title of error dialog.
            text (str): Text of error dialog.
            detail (str, optional): Detailed information of error dialog.
                (If not given, 'Show Detail' button will not display.)
        """
        self.__error_sig.emit(title, text, detail)

    def fatal(
        self, title: str, text: str, detail: str = '', exitcode: int = 0
    ) -> None:
        """Show error dialog, and exists program.

        Args:
            title (str): Title of error dialog.
            text (str): Text of error dialog.
            detail (str, optional): Detailed information of error dialog.
                (If not given, 'Show Detail' button will not display.)
        """
        self.__fatal_sig.emit(title, text, detail, exitcode)

    def __initalize_messagebox(
        self, icon: QMessageBox.Icon, title: str, text: str, detail: str = ''
    ) -> QMessageBox:
        msgbox = QMessageBox(
            icon, title, f'{text:75s}' if detail else text,
            parent=self.__parent
        )
        if detail:
            msgbox.setDetailedText(detail)
        return msgbox

    def __show_warning(self, title: str, text: str, detail: str = '') -> None:
        self.__initalize_messagebox(
            QMessageBox.Warning, title, text, detail
        ).exec()

    def __show_error(self, title: str, text: str, detail: str = '') -> None:
        self.__initalize_messagebox(
            QMessageBox.Critical, title, text, detail
        ).exec()

    def __show_fatal(
        self, title: str, text: str, detail: str = '', exitcode: int = 0
    ) -> None:
        msgbox = self.__initalize_messagebox(
            QMessageBox.Critical, title, text, detail
        )
        msgbox.addButton('Exit', QMessageBox.DestructiveRole)
        msgbox.exec()
        sys.exit(exitcode)

    def __print_msg(self, type_: str, text: str, detail: str) -> None:
        print(f"{type_}: {text}\n  {(NL + '  ').join(detail.split(NL))}")

    def __print_warning(self, _: str, text: str, detail: str = '') -> None:
        self.__print_msg('Warning', text, detail)

    def __print_error(self, _: str, text: str, detail: str = '') -> None:
        self.__print_msg('Error', text, detail)

    def __print_fatal(
        self, _: str, text: str, detail: str = '', exitcode: int = 0
    ) -> None:
        self.__print_msg('Fatal', text, detail)
        sys.exit(exitcode)
