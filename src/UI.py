# pylint: disable = line-too-long, redundant-u-string-prefix

from PySide6.QtCore import Qt, QCoreApplication, Signal
# from PySide6.QtGui import
from PySide6.QtWidgets import (
    QWidget, QGroupBox,
    QGridLayout, QHBoxLayout,
    QLineEdit, QComboBox, QSpinBox, QPushButton, QRadioButton,
    QLabel, QTreeView, QStatusBar, QProgressBar,
    QSpacerItem, QSizePolicy
)


sizePolicy_PE = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
sizePolicy_PE.setHorizontalStretch(0)
sizePolicy_PE.setVerticalStretch(0)

sizePolicy_FF = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
sizePolicy_FF.setHorizontalStretch(0)
sizePolicy_FF.setVerticalStretch(0)

sizePolicy_MF = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
sizePolicy_MF.setHorizontalStretch(0)
sizePolicy_MF.setVerticalStretch(0)

sizePolicy_EF = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
sizePolicy_EF.setHorizontalStretch(0)
sizePolicy_EF.setVerticalStretch(0)


class ClickableLabel(QLabel):
    clicked = Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setStyleSheet('color: blue; text-decoration: underline;')

    def mousePressEvent(self, event):
        event.accept()
        self.clicked.emit()


class Ui_MainWin(object):
    # pylint: disable = attribute-defined-outside-init
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWin")
        MainWindow.resize(800, 500)

        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.glCent = QGridLayout(self.centralwidget)
        self.glCent.setObjectName(u"glCent")

        # Sources group box
        self.gbSources = QGroupBox(self.centralwidget)
        self.hlSources = QHBoxLayout(self.gbSources)

        self.rbHellolms = QRadioButton(self.gbSources)
        self.hlSources.addWidget(self.rbHellolms)

        self.rbCanvas = QRadioButton(self.gbSources)
        self.hlSources.addWidget(self.rbCanvas)

        self.glCent.addWidget(self.gbSources, 0, 0, 1, 1)
        # end sources

        self.lbTitleDst = QLabel(self.centralwidget)
        self.lbTitleDst.setObjectName(u"lbTitleDst")
        sizePolicy_MF.setHeightForWidth(self.lbTitleDst.hasHeightForWidth())
        self.lbTitleDst.setSizePolicy(sizePolicy_MF)
        self.lbTitleDst.setAlignment(Qt.AlignCenter)
        self.glCent.addWidget(self.lbTitleDst, 0, 1, 1, 1)

        self.lbDst = ClickableLabel(self.centralwidget)
        self.lbDst.setObjectName(u"lbDst")
        sizePolicy_EF.setHeightForWidth(self.lbDst.sizePolicy().hasHeightForWidth())
        self.lbDst.setSizePolicy(sizePolicy_EF)
        self.lbDst.setAlignment(Qt.AlignCenter)
        self.glCent.addWidget(self.lbDst, 0, 2, 1, 2)

        self.btnSetDst = QPushButton(self.centralwidget)
        self.btnSetDst.setObjectName(u"btnSetDst")
        sizePolicy_FF.setHeightForWidth(self.btnSetDst.sizePolicy().hasHeightForWidth())
        self.btnSetDst.setSizePolicy(sizePolicy_FF)
        self.glCent.addWidget(self.btnSetDst, 0, 4, 1, 1)

        # Files group box
        self.gbFile = QGroupBox(self.centralwidget)
        self.gbFile.setObjectName(u"gbFile")
        sizePolicy_PE.setHeightForWidth(self.gbFile.sizePolicy().hasHeightForWidth())
        self.gbFile.setSizePolicy(sizePolicy_PE)
        self.glFile = QGridLayout(self.gbFile)
        self.glFile.setObjectName(u"glFile")

        self.btnSelect = QPushButton(self.gbFile)
        self.btnSelect.setObjectName(u"btnSelect")
        self.glFile.addWidget(self.btnSelect, 1, 0, 1, 1)

        self.btnReverse = QPushButton(self.gbFile)
        self.btnReverse.setObjectName(u"btnReverse")
        self.glFile.addWidget(self.btnReverse, 1, 1, 1, 1)

        self.sp = QSpacerItem(198, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.glFile.addItem(self.sp, 1, 2, 1, 1)

        self.btnDownload = QPushButton(self.gbFile)
        self.btnDownload.setObjectName(u"btnDownload")
        self.glFile.addWidget(self.btnDownload, 1, 3, 1, 1)

        self.tvFile = QTreeView(self.gbFile)
        self.tvFile.setObjectName(u"tvFile")
        self.glFile.addWidget(self.tvFile, 0, 0, 1, 4)

        self.glCent.addWidget(self.gbFile, 1, 0, 1, 5)
        # end files

        # Login group box
        self.gbLogin = QGroupBox(self.centralwidget)
        self.gbLogin.setObjectName(u"gbLogin")
        self.glLogin = QGridLayout(self.gbLogin)
        self.glLogin.setObjectName(u"glLogin")

        self.lbUser = QLabel(self.gbLogin)
        self.lbUser.setObjectName(u"lbUser")
        self.lbUser.setAlignment(Qt.AlignCenter)
        self.glLogin.addWidget(self.lbUser, 0, 0, 1, 1)

        self.lnUser = QLineEdit(self.gbLogin)
        self.lnUser.setObjectName(u"lnUser")
        self.glLogin.addWidget(self.lnUser, 0, 1, 1, 1)

        self.lbPass = QLabel(self.gbLogin)
        self.lbPass.setObjectName(u"lbPass")
        self.lbPass.setAlignment(Qt.AlignCenter)
        self.glLogin.addWidget(self.lbPass, 0, 2, 1, 1)

        self.lnPass = QLineEdit(self.gbLogin)
        self.lnPass.setObjectName(u"lnPass")
        self.lnPass.setEchoMode(QLineEdit.Password)
        self.glLogin.addWidget(self.lnPass, 0, 3, 1, 2)

        self.lbId = QLabel(self.gbLogin)
        self.lbId.setObjectName(u"lbId")
        self.lbId.setAlignment(Qt.AlignCenter)
        self.glLogin.addWidget(self.lbId, 1, 0, 1, 1)

        self.lnId = QLineEdit(self.gbLogin)
        self.lnId.setObjectName(u"lnId")
        self.lnId.setEchoMode(QLineEdit.Password)
        self.glLogin.addWidget(self.lnId, 1, 1, 1, 3)

        self.btnLogin = QPushButton(self.gbLogin)
        self.btnLogin.setObjectName(u"btnLogin")
        self.glLogin.addWidget(self.btnLogin, 1, 4, 1, 1)

        self.glCent.addWidget(self.gbLogin, 2, 0, 1, 3)
        # end login

        # Semester & subject group box
        self.gbSubject = QGroupBox(self.centralwidget)
        self.gbSubject.setObjectName(u"gbSubject")
        self.glSubject = QGridLayout(self.gbSubject)
        self.glSubject.setObjectName(u"glSubject")

        self.lbYear = QLabel(self.gbSubject)
        self.lbYear.setObjectName(u"lbYear")
        self.glSubject.addWidget(self.lbYear, 0, 0, 1, 1)

        self.spinYear = QSpinBox(self.gbSubject)
        self.spinYear.setObjectName(u"spinYear")
        self.spinYear.setMinimum(2010)
        self.spinYear.setMaximum(2099)
        self.spinYear.setValue(2021)
        self.glSubject.addWidget(self.spinYear, 0, 1, 1, 1)

        self.lbSemester = QLabel(self.gbSubject)
        self.lbSemester.setObjectName(u"lbSemester")
        self.glSubject.addWidget(self.lbSemester, 0, 2, 1, 1)

        self.cbSemester = QComboBox(self.gbSubject)
        self.cbSemester.setObjectName(u"cbSemester")
        self.glSubject.addWidget(self.cbSemester, 0, 3, 1, 1)

        self.btnSetSmst = QPushButton(self.gbSubject)
        self.btnSetSmst.setObjectName(u"btnSetSmst")
        self.glSubject.addWidget(self.btnSetSmst, 0, 4, 1, 1)

        self.lbSubject = QLabel(self.gbSubject)
        self.lbSubject.setObjectName(u"lbSubject")
        self.glSubject.addWidget(self.lbSubject, 1, 0, 1, 1)

        self.cbSubject = QComboBox(self.gbSubject)
        self.cbSubject.setObjectName(u"cbSubject")
        self.glSubject.addWidget(self.cbSubject, 1, 1, 1, 3)

        self.btnSetSubj = QPushButton(self.gbSubject)
        self.btnSetSubj.setObjectName(u"btnSetSubj")
        self.glSubject.addWidget(self.btnSetSubj, 1, 4, 1, 1)

        self.glCent.addWidget(self.gbSubject, 2, 3, 1, 2)
        # end semester & subject

        MainWindow.setCentralWidget(self.centralwidget)

        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")

        self.pg = QProgressBar(self)
        self.pg.setRange(0, 1)
        self.pg.setTextVisible(False)
        self.statusbar.addPermanentWidget(self.pg)

        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"LMS \uac15\uc758\uc790\ub8cc \ub2e4\uc6b4\ub85c\ub354", None))

        self.gbSources.setTitle(u"\uc704\uce58 \uc120\ud0dd")
        self.rbHellolms.setText(u"HelloLMS")
        self.rbCanvas.setText(u"Canvas")

        self.lbTitleDst.setText(QCoreApplication.translate("MainWindow", u"\uc800\uc7a5 \uc704\uce58", None))
        self.btnSetDst.setText(QCoreApplication.translate("MainWindow", u"\ubcc0\uacbd", None))

        self.gbFile.setTitle(QCoreApplication.translate("MainWindow", u"\ud30c\uc77c \uc815\ubcf4", None))
        self.btnSelect.setText(QCoreApplication.translate("MainWindow", u"\ubaa8\ub450 \uc120\ud0dd", None))
        self.btnReverse.setText(QCoreApplication.translate("MainWindow", u"\uc120\ud0dd \ubc18\uc804", None))
        self.btnDownload.setText(QCoreApplication.translate("MainWindow", u"\uc120\ud0dd \ub2e4\uc6b4\ub85c\ub4dc", None))

        self.gbLogin.setTitle(QCoreApplication.translate("MainWindow", u"\ub85c\uadf8\uc778 \uc0c1\ud0dc: \ub85c\uadf8\uc544\uc6c3\ub428", None))
        self.lbUser.setText(QCoreApplication.translate("MainWindow", u"LMS \uc0ac\uc6a9\uc790\uba85", None))
        self.lbPass.setText(QCoreApplication.translate("MainWindow", u"LMS \ube44\ubc00\ubc88\ud638", None))
        self.lbId.setText(QCoreApplication.translate("MainWindow", u"\ud559\ubc88", None))
        self.btnLogin.setText(QCoreApplication.translate("MainWindow", u"\ub85c\uadf8\uc778", None))

        self.gbSubject.setTitle(QCoreApplication.translate("MainWindow", u"\uacfc\ubaa9\uba85: \uc124\uc815 \uc548 \ub428", None))
        self.lbYear.setText(QCoreApplication.translate("MainWindow", u"\ud559\ub144\ub3c4", None))
        self.spinYear.setSuffix(QCoreApplication.translate("MainWindow", u"\ub144", None))
        self.lbSemester.setText(QCoreApplication.translate("MainWindow", u"\ud559\uae30", None))
        self.cbSemester.addItem(QCoreApplication.translate("MainWindow", u"1\ud559\uae30", None))
        self.cbSemester.addItem(QCoreApplication.translate("MainWindow", u"\uc5ec\ub984\uacc4\uc808", None))
        self.cbSemester.addItem(QCoreApplication.translate("MainWindow", u"2\ud559\uae30", None))
        self.cbSemester.addItem(QCoreApplication.translate("MainWindow", u"\uaca8\uc6b8\uacc4\uc808", None))
        self.btnSetSmst.setText(QCoreApplication.translate("MainWindow", u"\uacfc\ubaa9 \uc870\ud68c", None))
        self.lbSubject.setText(QCoreApplication.translate("MainWindow", u"\uacfc\ubaa9\uba85", None))
        self.btnSetSubj.setText(QCoreApplication.translate("MainWindow", u"\uc124\uc815", None))
    # retranslateUi
