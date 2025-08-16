# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'litographer.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QMainWindow, QMenu, QMenuBar,
    QSizePolicy, QStatusBar, QWidget)

class Ui_LitographerWindow(object):
    def setupUi(self, LitographerWindow):
        if not LitographerWindow.objectName():
            LitographerWindow.setObjectName(u"LitographerWindow")
        LitographerWindow.resize(990, 600)
        self.centralwidget = QWidget(LitographerWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        LitographerWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(LitographerWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 990, 23))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        LitographerWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(LitographerWindow)
        self.statusbar.setObjectName(u"statusbar")
        LitographerWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(LitographerWindow)

        QMetaObject.connectSlotsByName(LitographerWindow)
    # setupUi

    def retranslateUi(self, LitographerWindow):
        LitographerWindow.setWindowTitle(QCoreApplication.translate("LitographerWindow", u"Litographer", None))
        self.menuFile.setTitle(QCoreApplication.translate("LitographerWindow", u"File", None))
    # retranslateUi

