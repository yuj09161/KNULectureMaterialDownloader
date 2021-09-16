from PySide6.QtCore import Qt, QObject, Signal
from PySide6.QtGui import QStandardItemModel, QStandardItem

import itertools
from typing import (
    Callable, Sequence, Iterable,
    Union, Any, List, Tuple
)


class _StatusBridge(QObject):
    _signal = Signal(tuple)

    def __init__(self, parent):
        super().__init__(parent)
        self.__functions = {}
        self._signal.connect(self.__send_info)

    def __call__(self, progress_info: Tuple[int, str]):
        self._signal.emit(progress_info)

    def register_func(self, work_id: int, function: Callable[[str], Any]):
        self.__functions[work_id] = function

    def clear_func(self):
        self.__functions = {}

    def __send_info(self, info: Tuple[int, str]):
        work_id, progress_status = info
        self.__functions[work_id](progress_status)


class ModelBase(QStandardItemModel):
    """
    The base class of all other models.

    Provides some extra functions compared to Qt's QStandardItemModel.
    Create direct instance of this method is not recommended.

    Public functions and its signature:
        def set_data(self, datas: Iterable[Iterable[str]]) -> None:
            Sets model's data.
        def add_data(
            self, data: Iterable[str],
            items_at_first: Iterable[QStandardItem] = None,
            items_at_last: Iterable[QStandardItem] = None
        ) -> None:
            Adds a row.
        def del_row(self, k: int) -> None:
            Remove given row.
        def clear(self) -> None:
            Remove all rows.
    """

    _header = NotImplemented

    def __init__(self):
        """Create an instance of this class."""
        super().__init__()
        self._dummy = itertools.repeat(None)
        self._set_header()

    def _set_header(self) -> None:
        self.setHorizontalHeaderLabels(getattr(self, '_header', tuple()))

    def set_data(self, datas: Iterable[Iterable[str]]) -> None:
        """
        Sets data of model to argument datas.

        Args:
            datas (Iterable[Iterable[str]]):
                The iterable that contains texts to display.
        """
        self.clear()
        for data in datas:
            self.add_data(data)
        self._set_header()

    def add_data(
        self, data: Iterable[str],
        items_at_first: Iterable[QStandardItem] = None,
        items_at_last: Iterable[QStandardItem] = None
    ) -> None:
        """
        Adds given data(texts) (and additional items(optinal)) to model.

        Args:
            data (Iterable[str]): The texts to display.
            items_at_first (Iterable[QStandardItem], optional):
                If given, given items is inserted before the data.
            items_at_last (Iterable[QStandardItem], optional):
                If given, given items is inserted after the data.
        """
        items = []
        for d in data:
            item = QStandardItem(d)
            item.setEditable(False)
            items.append(item)

        if items_at_first:
            iter(items_at_first)
        if items_at_last:
            iter(items_at_last)

        self.appendRow([
            *(items_at_first if items_at_first else tuple()),
            *items,
            *(items_at_last if items_at_last else tuple())
        ])

    def del_row(self, k: int) -> None:
        """
        Remove given row.

        Args:
            k (int): The row number.
        """
        self.removeRow(k)

    def clear(self) -> None:
        """Removes all data."""
        super().clear()
        self._set_header()


class CheckModelBase(ModelBase):
    """
    Model that adds an checkbox to start of every row.

    Create direct instance of this method is not recommended.

    Adds checkbox to start of every row,
    and provide some checkbox-related functions.
    Create direct instance of this method is not recommended.

    Inherited public functions:
        def set_data(self, datas: Iterable[Iterable[str]]) -> None:
            Sets model's data.
        def del_row(self, k: int) -> None:
            Remove given row.
        def clear(self) -> None:
            Remove all rows.

    Public properties:
        default_check_state (QCheckState, Writable):
            Default check state when no state passed to function add_data.
            Also accepts bool type (Internally converts to QCheckedState).
        chk_enabled_cnt (int, Read-only):
            The number of checkbox enabled row.
        chk_selected_cnt (int, Read-only):
            The number of checked row.
        all_selected (bool, Read-only):
            If all row is checked, this property equals to True.
            Otherwise its value is False.
        row_checkstate (list[bool], Read-only):
            Contains checked state of all rows.
        checked_row (list[int], Read-only):
            Contains row number that checked.

    Public functions and its signature:
        def add_data(
            self, data: Iterable[str],
            items_at_first: Iterable[QStandardItem] = None,
            items_at_last: Iterable[QStandardItem] = None,
            *,
            chk_enabled: bool = True,
            chk_state: Qt.CheckState = Qt.Checked
        ) -> None:
            Adds a row.
        def del_selected(self) -> List[int]:
            Delete checked row(s).
        def select_all(self) -> None:
            Check all row(s).
        def reverse_selection(self) -> None:
            Uncheck checked row, check unchecked row.
        def clear_selection(self) -> None:
            Clears all checks.
    """
    _DEFAULT_CHECK_STATE = NotImplemented
    _SELECT_COL_NAME = '선택'

    def __init__(self, default_check_state: Union[bool, Qt.CheckState]):
        """
        Create an instance of this class.

        Args:
            default_check_state (Union[bool, Qt.CheckState]):
                Sets the default check state.
        """
        super().__init__()

        self.default_check_state = default_check_state

    def _set_header(self) -> None:
        self.setHorizontalHeaderLabels(itertools.chain(
            (self._SELECT_COL_NAME,), getattr(self, '_header', tuple())
        ))

    def add_data(
        self, data: Iterable[str],
        items_at_first: Iterable[QStandardItem] = None,
        items_at_last: Iterable[QStandardItem] = None,
        *,
        chk_enabled: bool = True,
        chk_state: Qt.CheckState = None
    ) -> None:
        """
        Adds given data(texts) (and additional items(optinal)) to model.

        Args:
            data (Iterable[str]):
                The texts to display.
            items_at_first (Iterable[QStandardItem], optional):
                If given, given items is inserted before the data.
            items_at_last (Iterable[QStandardItem], optional):
                If given, given items is inserted after the data.

        Keyword Args:
            chk_enabled (bool, optional):
                Enabled state of checkbox of the row.
                Defaults to True.
            chk_state (Qt.CheckState, optional):
                State of checkbox of the row.
                If not given,
                    the default_check_state property of class will be used.
        """
        # pylint: disable = arguments-differ
        if chk_state is None:
            chk_state = self._default_check_state

        chk_item = QStandardItem('')
        chk_item.setEditable(False)
        chk_item.setCheckable(True)
        chk_item.setCheckState(chk_state)
        chk_item.setEnabled(chk_enabled)
        chk_iter = (chk_item,)

        if items_at_first:
            items_at_first = itertools.chain(chk_item, items_at_first)
        else:
            items_at_first = chk_iter

        super().add_data(data, items_at_first, items_at_last)

    @property
    def default_check_state(self) -> bool:
        return self._default_check_state

    @default_check_state.setter
    def default_check_state(self, value: Union[bool, Qt.CheckState]) -> None:
        if isinstance(value, bool):
            self._default_check_state = Qt.Checked if value else Qt.Unchecked
        elif isinstance(value, Qt.CheckState):
            self._default_check_state = value
        else:
            raise TypeError

    @property
    def chk_enabled_cnt(self) -> int:
        cnt = 0
        for row in range(self.rowCount()):
            item = self.item(row, 0)
            if item.isEnabled():
                cnt += 1
        return cnt

    @property
    def chk_selected_cnt(self) -> int:
        cnt = 0
        for row in range(self.rowCount()):
            item = self.item(row, 0)
            if item.isEnabled():
                cnt += 1
        return cnt

    @property
    def all_selected(self) -> bool:
        row_cnt = self.rowCount()
        if row_cnt == 0:
            return False
        for k in range(row_cnt):
            chk = self.item(k, 0)
            if chk.checkState() == Qt.Unchecked and chk.isEnabled():
                return False
        return True

    @property
    def row_checkstate(self) -> List[bool]:
        return [
            self.item(k, 0).checkState() == Qt.Checked
            for k in range(self.rowCount())
        ]

    @property
    def checked_row(self) -> List[int]:
        return [
            k for k in range(self.rowCount())
            if self.item(k, 0).checkState() == Qt.Checked
        ]

    def del_selected(self) -> List[int]:
        """
        Delete checked row(s).

        Returns:
            List[int]: List of removed row indexes.
        """
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

    def select_all(self) -> None:
        """Check all row(s)."""
        for k in range(self.rowCount()):
            chk = self.item(k, 0)
            if chk.isEnabled():
                chk.setCheckState(Qt.Checked)

    def reverse_selection(self) -> None:
        """Uncheck checked row, check unchecked row."""
        for k in range(self.rowCount()):
            chk = self.item(k, 0)
            if chk.isEnabled():
                chk.setCheckState(
                    Qt.Unchecked
                    if chk.checkState() == Qt.Checked
                    else Qt.Checked
                )

    def clear_selection(self) -> None:
        """Clears all checks."""
        for k in range(self.rowCount()):
            self.item(k, 0).setCheckState(Qt.Unchecked)


class InfoModelBase(CheckModelBase):
    """
    Subclass of CheckModelBase that contains extra informations.

    Create direct instance of this method is not recommended.

    Inherited public properties:
        default_check_state (QCheckState, Writable):
            Default check state when no state passed to function add_data.
            Also accepts bool type (Internally converts to QCheckedState).
        chk_enabled_cnt (int, Read-only):
            The number of checkbox enabled row.
        chk_selected_cnt (int, Read-only):
            The number of checked row.
        all_selected (bool, Read-only):
            If all row is checked, this property equals to True.
            Otherwise its value is False.
        row_checkstate (list[bool], Read-only):
            Contains checked state of all rows.
        checked_row (list[int], Read-only):
            Contains row number that checked.

    Inherited public functions:
        def set_data(self, datas: Iterable[Iterable[str]]) -> None:
            Sets model's data.
        def del_row(self, k: int) -> None:
            Remove given row.
        def clear(self) -> None:
            Remove all rows.
        def del_selected(self) -> List[int]:
            Delete checked row(s).
        def select_all(self) -> None:
            Check all row(s).
        def reverse_selection(self) -> None:
            Uncheck checked row, check unchecked row.
        def clear_selection(self) -> None:
            Clears all checks.

    Public properties:
        info_of_selected (List[Any]):
            Get extra informations of checked row.

    Public functions and its signature:
        def add_data(
            self, to_display: Iterable[str], infos: Any,
            items_at_first: Iterable[QStandardItem] = None,
            items_at_last: Iterable[QStandardItem] = None,
            *,
            chk_enabled: bool = True,
            chk_state: Qt.CheckState = None
        ) -> None:
            Adds a row with checkbox.
        def del_row(self, k) -> None:
            Remove given row.
        def clear(self) -> None:
            Remove all rows.
    """

    def __init__(self, default_check_state: Union[bool, Qt.CheckState]):
        """
        Create an instance of this class.

        Args:
            default_check_state (Union[bool, Qt.CheckState]):
                Sets the default check state.
        """
        self._infos = []
        super().__init__(default_check_state)

    def add_data(
        self, to_display: Iterable[str], infos: Any,
        items_at_first: Iterable[QStandardItem] = None,
        items_at_last: Iterable[QStandardItem] = None,
        *,
        chk_enabled: bool = True,
        chk_state: Qt.CheckState = None
    ) -> None:
        """
        Adds given data(texts) (and additional items(optinal)) to model.

        Checkbox will be placed at first column.

        Args:
            to_display (Iterable[str]):
                The texts to display.
            infos (Any):
                The extra information.
                Will be used output of info_of_selected property.
            items_at_first (Iterable[QStandardItem], optional):
                If given, given items is inserted before the data.
            items_at_last (Iterable[QStandardItem], optional):
                If given, given items is inserted after the data.

        Keyword Args:
            chk_enabled (bool, optional):
                Enabled state of checkbox of the row.
                Defaults to True.
            chk_state (Qt.CheckState, optional):
                State of checkbox of the row.
                If not given, the _DEFAULT_CHECK_STATE of class will be used.
        """
        # pylint: disable = arguments-differ
        super().add_data(
            to_display, items_at_first, items_at_last,
            chk_enabled=chk_enabled, chk_state=chk_state
        )
        self._infos.append(infos)

    @property
    def info_of_selected(self) -> List[Any]:
        checked_row = self.checked_row
        return [
            info for k, info in enumerate(self._infos) if k in checked_row
        ]

    def del_row(self, k: str) -> None:
        """
        Remove given row.

        Args:
            k (int): The row number.
        """
        super().del_row(k)
        del self._infos[k]

    def clear(self) -> None:
        """Removes all data."""
        self._infos = []
        super().clear()


class WorkModelBase(InfoModelBase):
    """
    Subclass of CheckModelBase that contains extra informations.

    Create direct instance of this method is not recommended.

    Inherited public properties:
        default_check_state (QCheckState, Writable):
            Default check state when no state passed to function add_data.
            Also accepts bool type (Internally converts to QCheckedState).
        chk_enabled_cnt (int, Read-only):
            The number of checkbox enabled row.
        chk_selected_cnt (int, Read-only):
            The number of checked row.
        all_selected (bool, Read-only):
            If all row is checked, this property equals to True.
            Otherwise its value is False.
        row_checkstate (list[bool], Read-only):
            Contains checked state of all rows.
        checked_row (list[int], Read-only):
            Contains row number that checked.
        info_of_selected (List[Any]):
            Get extra informations of checked row.

    Inherited public functions:
        def set_data(self, datas: Iterable[Iterable[str]]) -> None:
            Sets model's data.
        def del_selected(self) -> List[int]:
            Delete checked row(s).
        def select_all(self) -> None:
            Check all row(s).
        def reverse_selection(self) -> None:
            Uncheck checked row, check unchecked row.
        def clear_selection(self) -> None:
            Clears all checks.
        def del_row(self, k) -> None:
            Remove given row.
        def clear(self) -> None:
            Remove all rows.

    Public properties:
        info_and_signal_of_checked (tuple, Read-only):
            This contains (info_of_selected, StatusBridge of this state.)

    Public functions and its signature:
        def add_data(
            self, to_display: Iterable[str], infos: Any,
            items_at_first: Iterable[QStandardItem] = None,
            items_at_last: Iterable[QStandardItem] = None,
            *,
            chk_enabled: bool = True,
            chk_state: Qt.CheckState = None
        ) -> None:
            Adds a row with checkbox and status col.
        def set_result(
            self,
            results: Sequence[Iterable],
            disable_successed: bool = None
        ) -> None:
            Set results of each selected row.
        def del_successed(self) -> None:
            Remove successed work(s).
    """
    _WAIT_TEXT = '대기'

    def __init__(
        self,
        default_check_state: Union[bool, Qt.CheckState],
        disable_successed: bool
    ):
        """
        Create an instance of this class.

        Args:
            default_check_state (Union[bool, Qt.CheckState]):
                Sets the default check state.
            disable_successed (Union[bool, Qt.CheckState]):
                If true, the checkbox of successed row will be disabled.
        """
        super().__init__(default_check_state)
        self.__successed_row = set()
        self.__disable_successed = disable_successed

    def _set_header(self) -> None:
        self.setHorizontalHeaderLabels(itertools.chain(
            (self._SELECT_COL_NAME,),
            getattr(self, '_header', tuple()),
            ('상태',)
        ))

    def add_data(
        self, to_display: Iterable[str], infos: Any,
        items_at_first: Iterable[QStandardItem] = None,
        items_at_last: Iterable[QStandardItem] = None,
        *,
        chk_enabled: bool = True,
        chk_state: Qt.CheckState = None
    ) -> None:
        """
        Adds given data(texts) (and additional items(optinal)) to model.

        Checkbox will be placed at first column,
        and Status will be placed at last column.

        Args:
            to_display (Iterable[str]):
                The texts to display.
            items_at_first (Iterable[QStandardItem], optional):
                If given, given items is inserted before the data.
            items_at_last (Iterable[QStandardItem], optional):
                If given, given items is inserted after the data.

        Keyword Args:
            chk_enabled (bool, optional):
                Enabled state of checkbox of the row.
                Defaults to True.
            chk_state (Qt.CheckState, optional):
                State of checkbox of the row.
                If not given, the _DEFAULT_CHECK_STATE of class will be used.
        """
        # pylint: disable = arguments-differ
        status_item = QStandardItem(self._WAIT_TEXT)
        status_item.setEditable(False)
        status_iter = (status_item,)

        if items_at_last:
            items_at_last = itertools.chain(items_at_last, status_iter)
        else:
            items_at_last = status_iter

        super().add_data(
            to_display, infos, items_at_first, items_at_last,
            chk_enabled=chk_enabled, chk_state=chk_state
        )

    @property
    def info_and_signal_of_checked(
        self
    ) -> Tuple[List[Any], _StatusBridge]:
        # Result variables
        infos = []
        bridge = _StatusBridge(self)
        # Loop variables
        checked_row = self.checked_row
        last_col = self.columnCount() - 1

        for row, info in enumerate(self._infos):
            if row in checked_row:
                infos.append((row, *info))
                bridge.register_func(row, self.item(row, last_col).setText)
        return infos, bridge

    def set_result(
        self,
        results: Sequence[Iterable],
        disable_successed: bool = None
    ) -> None:
        """
        Set result of each selected row.

        Args:
            results (Sequence[Iterable]):
                The results, in row order.
                The Iterable must contain two items.
                    The type of first is bool,
                        and it means whether the work is successful.
                    The type of second is str,
                        and it is text to display.
            disable_successed (bool, optional):
                If this is true, successed row is disabled.
                If not given, it will be followed class's configuration.
        """
        if disable_successed is None:
            disable_successed = self.__disable_successed
        result_index = 0
        last_col = self.columnCount() - 1
        for row in range(self.rowCount()):
            if self.item(row, 0).checkState() == Qt.Checked:
                successed, text = results[result_index]
                if successed:
                    self.item(row, 0).setCheckState(Qt.Unchecked)
                    self.__successed_row.add(row)
                    if disable_successed:
                        self.item(row, 0).setEnabled(False)
                self.item(row, last_col).setText(text)
                result_index += 1

    def del_row(self, k: str) -> None:
        """
        Remove given row.

        Args:
            k (int): The row number.
        """
        super().del_row(k)
        self.__successed_row = \
            {x if x < k else x - 1 for x in self.__successed_row}

    def del_successed(self) -> None:
        """Remove successed work(s)."""
        row_count = self.rowCount()
        row = 0
        while row < row_count:
            if row in self.__successed_row:
                self.del_row(row)
                row_count -= 1
            else:
                row += 1

    def clear(self) -> None:
        """Removes all data."""
        super().clear()
        self.__successed_row = set()
