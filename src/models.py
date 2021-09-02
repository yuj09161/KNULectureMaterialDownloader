from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem

from typing import Union


# Base models
class BaseModel(QStandardItemModel):
    def __init__(self):
        super().__init__()
        self.set_header()

    # pylint: disable=dangerous-default-value
    def set_data(self, datas, additional_firsts=[], additional_lasts=[]):
        self.clear()
        if not (additional_firsts and additional_lasts):
            for data in datas:
                self.add_data(data)
        elif additional_firsts:
            assert isinstance(additional_firsts, list)
            assert len(datas) == len(additional_firsts)

            for data, additional_first in zip(datas, additional_firsts):
                self.add_data(data, additional_first)
        elif additional_lasts:
            assert isinstance(additional_lasts, list)
            assert len(datas) == len(additional_lasts)

            for data, additional_last in zip(datas, additional_lasts):
                self.add_data(data, additional_last)
        else:
            assert isinstance(additional_firsts, list)
            assert isinstance(additional_lasts, list)
            assert len(datas) == len(additional_firsts)\
                == len(additional_lasts)

            for data, additional_first, additional_last\
                    in zip(datas, additional_firsts, additional_lasts):
                self.add_data(data, additional_first, additional_last)
        self.set_header()

    def add_data(self, data, additional_first=None, additional_last=None):
        # caution: must syncronize with add_data method from CheckModel
        # Info: data must be iterable(list, tuple, zip etc.)
        items = []
        if additional_first:
            assert isinstance(additional_first, list)
            items += additional_first

        for d in data:
            item = QStandardItem(d)
            item.setEditable(False)
            items.append(item)

        if additional_last:
            assert isinstance(additional_last, list)
            items += additional_last

        self.appendRow(items)

    def clear(self):
        super().clear()
        self.set_header()

    def set_header(self):
        self.setHorizontalHeaderLabels(getattr(self, '_header', tuple()))


class CheckModel(BaseModel):
    def __init__(self):
        self._header = ('선택',) + self._header
        super().__init__()

    def add_data(
        self, data, additional_first=None, additional_last=None,
        *, chk_enabled=True, chk_state=Qt.Checked
    ):  # pylint: disable=arguments-differ
        # caution: data must be iterable(list, tuple, zip etc.)
        if additional_first:
            assert isinstance(additional_first, list)
            items = [(QStandardItem(''), *others)
                     for others in additional_first]
            items[0].setEditable(False)
            items[0].setCheckable(True)
            items[0].setCheckState(chk_state if chk_enabled else Qt.Unchecked)
            items[0].setEnabled(chk_enabled)
        else:
            chk = QStandardItem('')
            chk.setEditable(False)
            chk.setCheckable(True)
            chk.setCheckState(chk_state if chk_enabled else Qt.Unchecked)
            chk.setEnabled(chk_enabled)
            items = [chk]

        # caution: must syncronize with add_data method from BaseModel
        for d in data:
            item = QStandardItem(d)
            item.setEditable(False)
            items.append(item)

        if additional_last:
            assert isinstance(additional_last, list)
            items += additional_last

        self.appendRow(items)

    def is_selected(self):
        return [
            self.item(k, 0).checkState() == Qt.Checked
            for k in range(self.rowCount())
        ]

    def get_selected(self):
        return [
            k for k in range(self.rowCount())
            if self.item(k, 0).checkState() == Qt.Checked
        ]

    def del_selected(self):
        length = self.rowCount()
        k = 0
        deleted_row = []
        while k < length:
            if self.item(k, 0).checkState() == Qt.Checked:
                deleted_row.append(k)
                self.del_row(k)
                length -= 1
            else:
                k += 1
        return deleted_row

    @property
    def all_selected(self):
        for k in range(self.rowCount()):
            chk = self.item(k, 0)
            if chk.checkState() == Qt.Unchecked and chk.isEnabled():
                return False
        return True

    def select_all(self):
        for k in range(self.rowCount()):
            chk = self.item(k, 0)
            if chk.isEnabled():
                chk.setCheckState(Qt.Checked)

    def reverse_selection(self):
        for k in range(self.rowCount()):
            chk = self.item(k, 0)
            if chk.isEnabled():
                chk.setCheckState(
                    Qt.Unchecked
                    if chk.checkState() == Qt.Checked
                    else Qt.Checked
                )

    def clear_selection(self):
        for k in range(self.rowCount()):
            self.item(k, 0).setCheckState(Qt.Unchecked)

    def del_row(self, k):
        self.removeRow(k)
# end base models


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
        self.__subject_urls = []

    def set_subjects(self, subj_info: Union[list, tuple]):
        for subj in subj_info:
            self.add_data(*subj)

    def add_data(self, subject_name: str, subject_url: str):
        super().appendRow(QStandardItem(subject_name))
        self.__subject_urls.append(subject_url)

    def get_current_url(self, index: int):
        return self.__subject_urls[index]

    def clear(self):
        super().clear()
        self.__subject_urls = []


class Files(CheckModel):
    def __init__(self):
        self._header = ('No.', '파일명', '상태')
        self.__count = 0
        self.__infos = []
        super().__init__()

    def clear(self):
        self.__count = 0
        self.__infos = []
        super().clear()

    def add_data(self, name: str, url: str):
        # pylint: disable = arguments-differ
        self.__count += 1
        super().add_data(
            (str(self.__count), name, '대기'), chk_state=Qt.Unchecked
        )
        self.__infos.append((name, url))

    def get_selected(self):
        selected_row = super().get_selected()
        return [
            info for k, info in enumerate(self.__infos) if k in selected_row
        ]

    def set_result(self, result: Union[list, tuple]):
        k = 0
        for row in range(self.__count):
            if self.item(row, 0).checkState() == Qt.Checked:
                res = result[k]
                if res == '성공':
                    self.item(row, 0).setCheckState(Qt.Unchecked)
                    self.item(row, 0).setEnabled(False)
                self.item(row, len(self._header) - 1).setText('성공')
                k += 1
