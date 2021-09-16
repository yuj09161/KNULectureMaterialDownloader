from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem

from typing import Union

from pyside_commons import WorkModelBase


class HelloLMSSubjectsModel(QStandardItemModel):
    def __init__(self):
        super().__init__()
        self.__subject_codes = []

    def set_subjects(self, subj_info: Union[list, tuple]):
        for subj in subj_info:
            self.add_data(*subj)

    def add_data(self, subject_name: str, subject_code: str):
        super().appendRow(QStandardItem(subject_name))
        self.__subject_codes.append(subject_code)

    def get_current_code(self, index: int):
        return self.__subject_codes[index]

    def clear(self):
        super().clear()
        self.__subject_codes = []


class CanvasSubjectsModel(QStandardItemModel):
    def __init__(self):
        super().__init__()
        self.__course_ids = []

    def set_subjects(self, subj_info: Union[list, tuple]):
        for subj in subj_info:
            self.add_data(*subj)

    def add_data(self, subject_name: str, course_id: str):
        super().appendRow(QStandardItem(subject_name))
        self.__course_ids.append(course_id)

    def get_current_id(self, index: int):
        return self.__course_ids[index]

    def clear(self):
        super().clear()
        self.__course_ids = []


class Files(WorkModelBase):
    def __init__(self):
        self._header = ('No.', '파일명')
        super().__init__(True, False)

    def add_data(self, name: str, url: str):
        # pylint: disable = arguments-differ
        super().add_data(
            (str(self.rowCount() + 1), name), (name, url),
            chk_state=Qt.Unchecked
        )
