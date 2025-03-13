from PySide6.QtCore import Qt, QCoreApplication
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import (
    QDialog, QWidget, QMessageBox,
    QGridLayout, QHBoxLayout, QVBoxLayout,
    QSpacerItem, QSizePolicy,
    QPlainTextEdit, QLabel, QPushButton
)

from typing import Optional


sizePolicy_FF = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
sizePolicy_FF.setHorizontalStretch(0)
sizePolicy_FF.setVerticalStretch(0)


# UI classes
class Ui_About:
    def setupUi(self, About: QDialog):  # pylint: disable = W0621
        # pylint: disable = W0201
        if not About.objectName():
            About.setObjectName("About")
        About.setFixedWidth(600)
        About.setWindowFlags(
            About.windowFlags() ^ Qt.WindowMinMaxButtonsHint
        )

        self.glMain = QGridLayout(About)
        self.glMain.setObjectName("glMain")

        self.lbIcon = QLabel(About)
        self.lbIcon.setObjectName("lbIcon")
        self.lbIcon.setFixedSize(256, 256)
        self.lbIcon.setAlignment(Qt.AlignCenter)
        self.glMain.addWidget(self.lbIcon, 0, 0, 2, 1)

        self.lbTitle = QLabel(About)
        self.lbTitle.setObjectName("lbTitle")
        self.lbTitle.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.lbTitle.setFixedHeight(30)
        self.glMain.addWidget(self.lbTitle, 0, 1, 1, 2)

        self.lbDetail = QLabel(About)
        self.lbDetail.setObjectName("lbDesc")
        self.lbDetail.setWordWrap(True)
        self.lbDetail.setStyleSheet("font-size: 15px")
        self.lbDetail.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.glMain.addWidget(self.lbDetail, 1, 1, 1, 2)

        self.lbLicenseSummary = QLabel(About)
        self.lbLicenseSummary.setObjectName("lbNotice")
        self.lbLicenseSummary.setWordWrap(True)
        self.lbTitle.setMinimumHeight(30)
        self.glMain.addWidget(self.lbLicenseSummary, 2, 0, 1, 3)

        self.glMain.addItem(QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Ignored
        ), 3, 0, 1, 2)

        self.btnClose = QPushButton(About)
        self.btnClose.setObjectName("btnClose")
        sizePolicy_FF.setHeightForWidth(self.btnClose.hasHeightForWidth())
        self.btnClose.setSizePolicy(sizePolicy_FF)
        self.glMain.addWidget(self.btnClose, 3, 2)

        self.retranslateUi(About)

    def retranslateUi(self, About: QDialog):  # pylint: disable = W0621
        About.setWindowTitle(
            QCoreApplication.translate("About", "About", None)
        )
        self.btnClose.setText(
            QCoreApplication.translate("About", "\ub2eb\uae30", None)
        )


class Ui_License:
    def setupUi(self, License: QDialog):  # pylint: disable = W0621
        # pylint: disable = W0201
        if not License.objectName():
            License.setObjectName("info")
        License.setFixedSize(400, 300)
        License.setWindowFlags(
            License.windowFlags() ^ Qt.WindowMinMaxButtonsHint
        )

        self.vlCent = QVBoxLayout(License)
        self.vlCent.setObjectName("vlCent")

        self.pteMain = QPlainTextEdit(License)
        self.pteMain.setObjectName("pteMain")
        self.pteMain.setReadOnly(True)
        self.vlCent.addWidget(self.pteMain)

        self.widBot = QWidget(License)
        self.widBot.setObjectName("widBot")
        self.hlBot = QHBoxLayout(self.widBot)
        self.hlBot.setObjectName("hlBot")
        self.hlBot.setContentsMargins(0, 0, 0, 0)

        self.btnQt = QPushButton(License)
        self.btnQt.setObjectName("btnQt")
        self.btnQt.setVisible(False)
        self.hlBot.addWidget(self.btnQt)

        self.sp = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )
        self.hlBot.addItem(self.sp)

        self.btnClose = QPushButton(self.widBot)
        self.btnClose.setObjectName("btnExit")
        self.hlBot.addWidget(self.btnClose)

        self.vlCent.addWidget(self.widBot)

        self.retranslateUi(License)

    def retranslateUi(self, License: QDialog):  # pylint: disable = W0621
        self.btnQt.setText(
            QCoreApplication.translate("info", "About Qt", None)
        )
        self.btnClose.setText(
            QCoreApplication.translate("info", "\ub2eb\uae30", None)
        )
# End UI classes


class About(QDialog, Ui_About):
    def __init__(
        self, name: str, description: str, license_summary: str,
        app_icon: Optional[QIcon] = None, parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        self.setupUi(self)
        self.name = name
        self.detail = description
        self.license_summary = license_summary
        if app_icon is not None:
            self.icon = app_icon
        self.btnClose.clicked.connect(self.close)

    @property
    def icon(self) -> QPixmap:
        return self.lbIcon.pixmap()

    @icon.setter
    def icon(self, value: QIcon) -> None:
        self.lbIcon.setPixmap(value.pixmap(256, 256))

    @property
    def name(self) -> str:
        return self.lbTitle.text()

    @name.setter
    def name(self, value: str) -> None:
        self.lbTitle.setText(value)

    @property
    def detail(self) -> str:
        return self.lbDetail.text()

    @detail.setter
    def detail(self, value: str) -> None:
        self.lbDetail.setText(value)

    @property
    def license_summary(self) -> str:
        return self.lbLicenseSummary.text()

    @license_summary.setter
    def license_summary(self, value: str) -> None:
        self.lbLicenseSummary.setText(value)


class _LicenseBase(QDialog, Ui_License):
    def __init__(
        self, title: str, license_text: str, parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        self.setupUi(self)
        self.title = title
        self.license = license_text
        self.btnQt.clicked.connect(lambda: QMessageBox.aboutQt(self))
        self.btnClose.clicked.connect(self.close)
        self._post_init()

    def _post_init(self):
        pass

    @property
    def title(self):
        return self.windowTitle()

    @title.setter
    def title(self, value: str) -> None:
        self.setWindowTitle(value)

    @property
    def license(self):
        return self.pteMain.toPlainText()

    @license.setter
    def license(self, value: str) -> None:
        self.pteMain.setPlainText(value)


class License(_LicenseBase):
    pass


class LicenseWithAboutQt(_LicenseBase):
    def _post_init(self):
        self.btnQt.setVisible(True)
