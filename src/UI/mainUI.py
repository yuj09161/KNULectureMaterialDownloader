# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
##
## Created by: Qt User Interface Compiler version 6.1.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *  # type: ignore
from PySide6.QtGui import *  # type: ignore
from PySide6.QtWidgets import *  # type: ignore


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.glCent = QGridLayout(self.centralwidget)
        self.glCent.setObjectName(u"glCent")
        self.lbDst = QLabel(self.centralwidget)
        self.lbDst.setObjectName(u"lbDst")

        self.glCent.addWidget(self.lbDst, 0, 0, 1, 2)

        self.btnChangeDst = QPushButton(self.centralwidget)
        self.btnChangeDst.setObjectName(u"btnChangeDst")

        self.glCent.addWidget(self.btnChangeDst, 0, 2, 1, 1)

        self.gbFile = QGroupBox(self.centralwidget)
        self.gbFile.setObjectName(u"gbFile")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.gbFile.sizePolicy().hasHeightForWidth())
        self.gbFile.setSizePolicy(sizePolicy)
        self.glFile = QGridLayout(self.gbFile)
        self.glFile.setObjectName(u"glFile")
        self.btnSelect = QPushButton(self.gbFile)
        self.btnSelect.setObjectName(u"btnSelect")

        self.glFile.addWidget(self.btnSelect, 1, 0, 1, 1)

        self.btnInverse = QPushButton(self.gbFile)
        self.btnInverse.setObjectName(u"btnInverse")

        self.glFile.addWidget(self.btnInverse, 1, 1, 1, 1)

        self.sp = QSpacerItem(198, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.glFile.addItem(self.sp, 1, 2, 1, 1)

        self.btnDownload = QPushButton(self.gbFile)
        self.btnDownload.setObjectName(u"btnDownload")

        self.glFile.addWidget(self.btnDownload, 1, 3, 1, 1)

        self.treeFile = QTreeWidget(self.gbFile)
        self.treeFile.setObjectName(u"treeFile")

        self.glFile.addWidget(self.treeFile, 0, 0, 1, 4)


        self.glCent.addWidget(self.gbFile, 1, 0, 1, 3)

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

        self.glLogin.addWidget(self.lnPass, 0, 3, 1, 2)

        self.lbId = QLabel(self.gbLogin)
        self.lbId.setObjectName(u"lbId")
        self.lbId.setAlignment(Qt.AlignCenter)

        self.glLogin.addWidget(self.lbId, 1, 0, 1, 1)

        self.lnId = QLineEdit(self.gbLogin)
        self.lnId.setObjectName(u"lnId")

        self.glLogin.addWidget(self.lnId, 1, 1, 1, 3)

        self.btnLogin = QPushButton(self.gbLogin)
        self.btnLogin.setObjectName(u"btnLogin")

        self.glLogin.addWidget(self.btnLogin, 1, 4, 1, 1)


        self.glCent.addWidget(self.gbLogin, 2, 0, 1, 1)

        self.gbSubject = QGroupBox(self.centralwidget)
        self.gbSubject.setObjectName(u"gbSubject")
        self.glSubject = QGridLayout(self.gbSubject)
        self.glSubject.setObjectName(u"glSubject")
        self.cbSubject = QComboBox(self.gbSubject)
        self.cbSubject.setObjectName(u"cbSubject")

        self.glSubject.addWidget(self.cbSubject, 1, 1, 1, 3)

        self.lbSubject = QLabel(self.gbSubject)
        self.lbSubject.setObjectName(u"lbSubject")

        self.glSubject.addWidget(self.lbSubject, 1, 0, 1, 1)

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

        self.btnSet = QPushButton(self.gbSubject)
        self.btnSet.setObjectName(u"btnSet")

        self.glSubject.addWidget(self.btnSet, 1, 4, 1, 1)

        self.cbSemester = QComboBox(self.gbSubject)
        self.cbSemester.addItem("")
        self.cbSemester.addItem("")
        self.cbSemester.addItem("")
        self.cbSemester.addItem("")
        self.cbSemester.setObjectName(u"cbSemester")

        self.glSubject.addWidget(self.cbSemester, 0, 3, 1, 2)


        self.glCent.addWidget(self.gbSubject, 2, 1, 1, 2)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.lbDst.setText(QCoreApplication.translate("MainWindow", u"\uc800\uc7a5 \uc704\uce58:", None))
        self.btnChangeDst.setText(QCoreApplication.translate("MainWindow", u"\uc120\ud0dd", None))
        self.gbFile.setTitle(QCoreApplication.translate("MainWindow", u"\ud30c\uc77c \uc815\ubcf4", None))
        self.btnSelect.setText(QCoreApplication.translate("MainWindow", u"\uc804\uccb4 \uc120\ud0dd", None))
        self.btnInverse.setText(QCoreApplication.translate("MainWindow", u"\uc120\ud0dd \ubc18\uc804", None))
        self.btnDownload.setText(QCoreApplication.translate("MainWindow", u"\uc120\ud0dd \ub2e4\uc6b4\ub85c\ub4dc", None))
        ___qtreewidgetitem = self.treeFile.headerItem()
        ___qtreewidgetitem.setText(2, QCoreApplication.translate("MainWindow", u"\uc790\ub8cc\uba85", None));
        ___qtreewidgetitem.setText(1, QCoreApplication.translate("MainWindow", u"No.", None));
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("MainWindow", u"\uc120\ud0dd", None));
        self.gbLogin.setTitle(QCoreApplication.translate("MainWindow", u"\ub85c\uadf8\uc778 \uc0c1\ud0dc: \ub85c\uadf8\uc544\uc6c3\ub428", None))
        self.lbUser.setText(QCoreApplication.translate("MainWindow", u"LMS \uc0ac\uc6a9\uc790\uba85", None))
        self.lbPass.setText(QCoreApplication.translate("MainWindow", u"LMS \ube44\ubc00\ubc88\ud638", None))
        self.lbId.setText(QCoreApplication.translate("MainWindow", u"\ud559\ubc88", None))
        self.btnLogin.setText(QCoreApplication.translate("MainWindow", u"\ub85c\uadf8\uc778", None))
        self.gbSubject.setTitle(QCoreApplication.translate("MainWindow", u"\uacfc\ubaa9\uba85: \uc124\uc815 \uc548 \ub428", None))
        self.lbSubject.setText(QCoreApplication.translate("MainWindow", u"\uacfc\ubaa9\uba85", None))
        self.lbYear.setText(QCoreApplication.translate("MainWindow", u"\ud559\ub144\ub3c4", None))
        self.spinYear.setSuffix(QCoreApplication.translate("MainWindow", u"\ub144", None))
        self.lbSemester.setText(QCoreApplication.translate("MainWindow", u"\ud559\uae30", None))
        self.btnSet.setText(QCoreApplication.translate("MainWindow", u"\uc124\uc815", None))
        self.cbSemester.setItemText(0, QCoreApplication.translate("MainWindow", u"1\ud559\uae30", None))
        self.cbSemester.setItemText(1, QCoreApplication.translate("MainWindow", u"2\ud559\uae30", None))
        self.cbSemester.setItemText(2, QCoreApplication.translate("MainWindow", u"\uc5ec\ub984\uacc4\uc808", None))
        self.cbSemester.setItemText(3, QCoreApplication.translate("MainWindow", u"\uaca8\uc6b8\uacc4\uc808", None))

    # retranslateUi

