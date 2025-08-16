# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'arc_type_manager_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractButton, QAbstractItemView, QApplication, QDialog,
    QDialogButtonBox, QHBoxLayout, QHeaderView, QLabel,
    QPushButton, QSizePolicy, QSpacerItem, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget)

class Ui_ArcTypeManagerDialog(object):
    def setupUi(self, ArcTypeManagerDialog):
        if not ArcTypeManagerDialog.objectName():
            ArcTypeManagerDialog.setObjectName(u"ArcTypeManagerDialog")
        ArcTypeManagerDialog.resize(600, 400)
        self.verticalLayout = QVBoxLayout(ArcTypeManagerDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.titleLabel = QLabel(ArcTypeManagerDialog)
        self.titleLabel.setObjectName(u"titleLabel")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.titleLabel.setFont(font)

        self.verticalLayout.addWidget(self.titleLabel)

        self.toolbarLayout = QHBoxLayout()
        self.toolbarLayout.setObjectName(u"toolbarLayout")
        self.addArcTypeButton = QPushButton(ArcTypeManagerDialog)
        self.addArcTypeButton.setObjectName(u"addArcTypeButton")

        self.toolbarLayout.addWidget(self.addArcTypeButton)

        self.editArcTypeButton = QPushButton(ArcTypeManagerDialog)
        self.editArcTypeButton.setObjectName(u"editArcTypeButton")
        self.editArcTypeButton.setEnabled(False)

        self.toolbarLayout.addWidget(self.editArcTypeButton)

        self.deleteArcTypeButton = QPushButton(ArcTypeManagerDialog)
        self.deleteArcTypeButton.setObjectName(u"deleteArcTypeButton")
        self.deleteArcTypeButton.setEnabled(False)

        self.toolbarLayout.addWidget(self.deleteArcTypeButton)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.toolbarLayout.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.toolbarLayout)

        self.arcTypesTable = QTableWidget(ArcTypeManagerDialog)
        if (self.arcTypesTable.columnCount() < 2):
            self.arcTypesTable.setColumnCount(2)
        __qtablewidgetitem = QTableWidgetItem()
        self.arcTypesTable.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.arcTypesTable.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        self.arcTypesTable.setObjectName(u"arcTypesTable")
        self.arcTypesTable.setAlternatingRowColors(True)
        self.arcTypesTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.arcTypesTable.setSortingEnabled(True)

        self.verticalLayout.addWidget(self.arcTypesTable)

        self.buttonBox = QDialogButtonBox(ArcTypeManagerDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Close)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(ArcTypeManagerDialog)
        self.buttonBox.rejected.connect(ArcTypeManagerDialog.reject)

        QMetaObject.connectSlotsByName(ArcTypeManagerDialog)
    # setupUi

    def retranslateUi(self, ArcTypeManagerDialog):
        ArcTypeManagerDialog.setWindowTitle(QCoreApplication.translate("ArcTypeManagerDialog", u"Manage Arc Types", None))
        self.titleLabel.setText(QCoreApplication.translate("ArcTypeManagerDialog", u"Arc Type Management", None))
        self.addArcTypeButton.setText(QCoreApplication.translate("ArcTypeManagerDialog", u"Add Arc Type", None))
        self.editArcTypeButton.setText(QCoreApplication.translate("ArcTypeManagerDialog", u"Edit Arc Type", None))
        self.deleteArcTypeButton.setText(QCoreApplication.translate("ArcTypeManagerDialog", u"Delete Arc Type", None))
        ___qtablewidgetitem = self.arcTypesTable.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("ArcTypeManagerDialog", u"Name", None));
        ___qtablewidgetitem1 = self.arcTypesTable.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("ArcTypeManagerDialog", u"Description", None));
    # retranslateUi

