# pylint: disable = line-too-long, redundant-u-string-prefix

from PySide6.QtCore import Qt, QCoreApplication
# from PySide6.QtGui import
from PySide6.QtWidgets import (
    QWidget, QGroupBox,
    QGridLayout, QHBoxLayout, QVBoxLayout,
    QLineEdit, QComboBox,
    QPushButton, QRadioButton, QCheckBox,
    QLabel, QTreeView, QStatusBar,
    QSpacerItem, QSizePolicy
)


sizePolicy_PE = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
sizePolicy_PE.setHorizontalStretch(0)
sizePolicy_PE.setVerticalStretch(0)

sizePolicy_FF = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
sizePolicy_FF.setHorizontalStretch(0)
sizePolicy_FF.setVerticalStretch(0)

sizePolicy_PF = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
sizePolicy_PF.setHorizontalStretch(0)
sizePolicy_PF.setVerticalStretch(0)

sizePolicy_EF = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
sizePolicy_EF.setHorizontalStretch(0)
sizePolicy_EF.setVerticalStretch(0)


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

        self.gbDst = QGroupBox(self.centralwidget)
        self.glDst = QGridLayout(self.gbDst)
        self.glDst.setObjectName(u"glDst")

        self.lbDst = QLabel(self.gbDst)
        self.lbDst.setObjectName(u"lbDst")
        sizePolicy_EF.setHeightForWidth(self.lbDst.sizePolicy().hasHeightForWidth())
        self.lbDst.setSizePolicy(sizePolicy_EF)
        self.lbDst.setAlignment(Qt.AlignCenter)
        self.glDst.addWidget(self.lbDst, 0, 0, 2, 1)

        self.btnOpenDst = QPushButton(self.gbDst)
        self.btnOpenDst.setObjectName(u"btnOpenDst")
        sizePolicy_FF.setHeightForWidth(self.btnOpenDst.sizePolicy().hasHeightForWidth())
        self.btnOpenDst.setSizePolicy(sizePolicy_FF)
        self.glDst.addWidget(self.btnOpenDst, 0, 1, 1, 1)

        self.btnSetDst = QPushButton(self.gbDst)
        self.btnSetDst.setObjectName(u"btnSetDst")
        sizePolicy_FF.setHeightForWidth(self.btnSetDst.sizePolicy().hasHeightForWidth())
        self.btnSetDst.setSizePolicy(sizePolicy_FF)
        self.glDst.addWidget(self.btnSetDst, 1, 1, 1, 1)

        self.glCent.addWidget(self.gbDst, 0, 0, 1, 1)

        # Semester & subject group box
        self.gbSubject = QGroupBox(self.centralwidget)
        self.gbSubject.setObjectName(u"gbSubject")
        self.glSubject = QGridLayout(self.gbSubject)
        self.glSubject.setObjectName(u"glSubject")

        self.lbSemester = QLabel(self.gbSubject)
        self.lbSemester.setObjectName(u"lbSemester")
        self.glSubject.addWidget(self.lbSemester, 0, 0, 1, 1)

        self.cbSemester = QComboBox(self.gbSubject)
        self.cbSemester.setObjectName(u"cbSemester")
        sizePolicy_EF.setHeightForWidth(self.cbSemester.sizePolicy().hasHeightForWidth())
        self.cbSemester.setSizePolicy(sizePolicy_EF)
        self.glSubject.addWidget(self.cbSemester, 0, 1, 1, 1)

        self.lbSubject = QLabel(self.gbSubject)
        self.lbSubject.setObjectName(u"lbSubject")
        self.glSubject.addWidget(self.lbSubject, 1, 0, 1, 1)

        self.cbSubject = QComboBox(self.gbSubject)
        self.cbSubject.setObjectName(u"cbSubject")
        sizePolicy_EF.setHeightForWidth(self.cbSubject.sizePolicy().hasHeightForWidth())
        self.cbSubject.setSizePolicy(sizePolicy_EF)
        self.glSubject.addWidget(self.cbSubject, 1, 1, 1, 1)

        self.btnSetSubject = QPushButton(self.gbSubject)
        self.btnSetSubject.setObjectName(u"btnSetSubject")
        sizePolicy_PE.setHeightForWidth(self.btnSetSubject.hasHeightForWidth())
        self.btnSetSubject.setSizePolicy(sizePolicy_PE)
        self.glSubject.addWidget(self.btnSetSubject, 0, 2, 2, 1)

        self.glCent.addWidget(self.gbSubject, 0, 1, 1, 1)
        # end semester & subject

        # Files group box
        self.gbFile = QGroupBox(self.centralwidget)
        self.gbFile.setObjectName(u"gbFile")
        sizePolicy_PE.setHeightForWidth(self.gbFile.sizePolicy().hasHeightForWidth())
        self.gbFile.setSizePolicy(sizePolicy_PE)
        self.glFile = QGridLayout(self.gbFile)
        self.glFile.setObjectName(u"glFile")

        self.btnSelect = QPushButton(self.gbFile)
        self.btnSelect.setObjectName(u"btnSelect")
        self.glFile.addWidget(self.btnSelect, 0, 0, 1, 1)

        self.btnReverse = QPushButton(self.gbFile)
        self.btnReverse.setObjectName(u"btnReverse")
        self.glFile.addWidget(self.btnReverse, 0, 1, 1, 1)

        self.sp = QSpacerItem(198, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.glFile.addItem(self.sp, 0, 2, 1, 1)

        self.btnDownload = QPushButton(self.gbFile)
        self.btnDownload.setObjectName(u"btnDownload")
        self.glFile.addWidget(self.btnDownload, 0, 3, 1, 1)

        self.tvFile = QTreeView(self.gbFile)
        self.tvFile.setObjectName(u"tvFile")
        self.glFile.addWidget(self.tvFile, 1, 0, 1, 4)

        self.glCent.addWidget(self.gbFile, 2, 0, 1, 2)
        # end files

        MainWindow.setCentralWidget(self.centralwidget)

        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"LMS \uac15\uc758\uc790\ub8cc \ub2e4\uc6b4\ub85c\ub354", None))

        self.gbDst.setTitle(QCoreApplication.translate("MainWindow", u"\ub2e4\uc6b4\ub85c\ub4dc \uc704\uce58", None))
        self.btnOpenDst.setText(QCoreApplication.translate("MainWindow", u"\uc5f4\uae30", None))
        self.btnSetDst.setText(QCoreApplication.translate("MainWindow", u"\ubcc0\uacbd", None))

        self.gbSubject.setTitle(QCoreApplication.translate("MainWindow", u"\ud559\uae30/\uacfc\ubaa9", None))
        self.lbSemester.setText(QCoreApplication.translate("MainWindow", u"\ud559\uae30", None))
        self.lbSubject.setText(QCoreApplication.translate("MainWindow", u"\uacfc\ubaa9\uba85", None))
        self.btnSetSubject.setText(QCoreApplication.translate("MainWindow", u"\uc124\uc815", None))

        self.gbFile.setTitle(QCoreApplication.translate("MainWindow", u"\ud30c\uc77c \uc815\ubcf4", None))
        self.btnSelect.setText(QCoreApplication.translate("MainWindow", u"\ubaa8\ub450 \uc120\ud0dd", None))
        self.btnReverse.setText(QCoreApplication.translate("MainWindow", u"\uc120\ud0dd \ubc18\uc804", None))
        self.btnDownload.setText(QCoreApplication.translate("MainWindow", u"\uc120\ud0dd \ub2e4\uc6b4\ub85c\ub4dc", None))
    # retranslateUi

class Ui_LoginWin:
    # pylint: disable = attribute-defined-outside-init
    def setupUi(self, LoginWin: QWidget):
        if not LoginWin.objectName():
            LoginWin.setObjectName(u"LoginWin")
        LoginWin.setFixedWidth(500)
        LoginWin.adjustSize()

        self.vlCent = QVBoxLayout(LoginWin)
        self.vlCent.setObjectName(u"vlCent")

        self.gbLoginMethod = QGroupBox(LoginWin)
        self.hlLoginMethod = QHBoxLayout(self.gbLoginMethod)

        self.rbIdPw = QRadioButton(self.gbLoginMethod)
        self.rbIdPw.setObjectName(u"rbIdPw")
        self.rbIdPw.setChecked(True)
        self.hlLoginMethod.addWidget(self.rbIdPw)

        self.rbPush = QRadioButton(self.gbLoginMethod)
        self.rbPush.setObjectName(u"rbPush")
        self.hlLoginMethod.addWidget(self.rbPush)

        self.vlCent.addWidget(self.gbLoginMethod)

        self.gbLogin = QGroupBox(LoginWin)
        self.glLogin = QGridLayout(self.gbLogin)

        self.lbUser = QLabel(self.gbLogin)
        self.lbUser.setObjectName(u"lbUser")
        sizePolicy_PF.setHeightForWidth(self.lbUser.hasHeightForWidth())
        self.lbUser.setSizePolicy(sizePolicy_PF)
        self.lbUser.setAlignment(Qt.AlignCenter)
        self.glLogin.addWidget(self.lbUser, 0, 0, 1, 1, Qt.AlignVCenter)

        self.lnUser = QLineEdit(self.gbLogin)
        self.lnUser.setObjectName(u"lnUser")
        self.glLogin.addWidget(self.lnUser, 0, 1, 1, 1, Qt.AlignVCenter)

        self.glLogin.addItem(
            QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Expanding),
            0, 0, 1, 2
        )

        self.lbPass = QLabel(self.gbLogin)
        self.lbPass.setObjectName(u"lbPass")
        sizePolicy_PF.setHeightForWidth(self.lbPass.hasHeightForWidth())
        self.lbPass.setSizePolicy(sizePolicy_PF)
        self.lbPass.setAlignment(Qt.AlignCenter)
        self.glLogin.addWidget(self.lbPass, 1, 0, 1, 1, Qt.AlignVCenter)

        self.lnPass = QLineEdit(self.gbLogin)
        self.lnPass.setObjectName(u"lnPass")
        self.lnPass.setEchoMode(QLineEdit.Password)
        self.glLogin.addWidget(self.lnPass, 1, 1, 1, 1, Qt.AlignVCenter)

        self.glLogin.addItem(
            QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Expanding),
            1, 0, 1, 2
        )

        self.widCheckBoxes = QWidget(self.gbLogin)
        self.hlCheckBoxes = QHBoxLayout(self.widCheckBoxes)
        self.hlCheckBoxes.setContentsMargins(0, 0, 0, 0)

        self.chkSaveId = QCheckBox(self.gbLogin)
        self.hlCheckBoxes.addWidget(self.chkSaveId)

        self.chkAutoLogin = QCheckBox(self.gbLogin)
        self.hlCheckBoxes.addWidget(self.chkAutoLogin)

        self.glLogin.addWidget(self.widCheckBoxes, 2, 0, 1, 2)

        self.btnLogin = QPushButton(self.gbLogin)
        self.btnLogin.setObjectName(u"btnLogin")
        sizePolicy_PE.setHeightForWidth(self.btnLogin.hasHeightForWidth())
        self.btnLogin.setSizePolicy(sizePolicy_PE)
        self.glLogin.addWidget(self.btnLogin, 0, 2, 3, 1)

        self.vlCent.addWidget(self.gbLogin)

        self.retranslateUi(LoginWin)

    def retranslateUi(self, LoginWin: QWidget):
        LoginWin.setWindowTitle(QCoreApplication.translate("MainWindow", u"LMS \ub85c\uadf8\uc778", None))

        self.gbLoginMethod.setTitle(QCoreApplication.translate("MainWindow", u"\ub85c\uadf8\uc778 \ubc29\ubc95 \uc120\ud0dd", None))
        self.rbIdPw.setText(u"ID+PW")
        self.rbPush.setText(u"KNUPIA \ud478\uc2dc")

        self.lbUser.setText(QCoreApplication.translate("MainWindow", u"ID", None))
        self.lbPass.setText(QCoreApplication.translate("MainWindow", u"PW", None))
        self.btnLogin.setText(QCoreApplication.translate("MainWindow", u"\ub85c\uadf8\uc778", None))
        self.chkSaveId.setText(QCoreApplication.translate("MainWindow", u"ID \uc800\uc7a5", None))
        self.chkAutoLogin.setText(QCoreApplication.translate("MainWindow", u"\uc790\ub3d9 \ub85c\uadf8\uc778", None))
