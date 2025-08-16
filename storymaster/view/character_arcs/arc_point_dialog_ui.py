# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'arc_point_dialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QComboBox, QDialog,
    QDialogButtonBox, QFormLayout, QLabel, QLineEdit,
    QScrollArea, QSizePolicy, QSpinBox, QTextEdit,
    QVBoxLayout, QWidget)

class Ui_ArcPointDialog(object):
    def setupUi(self, ArcPointDialog):
        if not ArcPointDialog.objectName():
            ArcPointDialog.setObjectName(u"ArcPointDialog")
        ArcPointDialog.resize(500, 600)
        self.verticalLayout = QVBoxLayout(ArcPointDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.titleLabel = QLabel(ArcPointDialog)
        self.titleLabel.setObjectName(u"titleLabel")
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.titleLabel.setFont(font)

        self.verticalLayout.addWidget(self.titleLabel)

        self.scrollArea = QScrollArea(ArcPointDialog)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 480, 69))
        self.formLayout = QFormLayout(self.scrollAreaWidgetContents)
        self.formLayout.setObjectName(u"formLayout")
        self.orderLabel = QLabel(self.scrollAreaWidgetContents)
        self.orderLabel.setObjectName(u"orderLabel")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.orderLabel)

        self.orderSpinBox = QSpinBox(self.scrollAreaWidgetContents)
        self.orderSpinBox.setObjectName(u"orderSpinBox")
        self.orderSpinBox.setMinimum(1)
        self.orderSpinBox.setMaximum(999)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.orderSpinBox)

        self.titleArcLabel = QLabel(self.scrollAreaWidgetContents)
        self.titleArcLabel.setObjectName(u"titleArcLabel")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.titleArcLabel)

        self.titleEdit = QLineEdit(self.scrollAreaWidgetContents)
        self.titleEdit.setObjectName(u"titleEdit")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.titleEdit)

        self.nodeLabel = QLabel(self.scrollAreaWidgetContents)
        self.nodeLabel.setObjectName(u"nodeLabel")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.nodeLabel)

        self.nodeComboBox = QComboBox(self.scrollAreaWidgetContents)
        self.nodeComboBox.addItem("")
        self.nodeComboBox.setObjectName(u"nodeComboBox")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.nodeComboBox)

        self.descriptionLabel = QLabel(self.scrollAreaWidgetContents)
        self.descriptionLabel.setObjectName(u"descriptionLabel")

        self.formLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.descriptionLabel)

        self.descriptionEdit = QTextEdit(self.scrollAreaWidgetContents)
        self.descriptionEdit.setObjectName(u"descriptionEdit")
        self.descriptionEdit.setMaximumSize(QSize(16777215, 80))

        self.formLayout.setWidget(4, QFormLayout.ItemRole.SpanningRole, self.descriptionEdit)

        self.emotionalStateLabel = QLabel(self.scrollAreaWidgetContents)
        self.emotionalStateLabel.setObjectName(u"emotionalStateLabel")

        self.formLayout.setWidget(5, QFormLayout.ItemRole.LabelRole, self.emotionalStateLabel)

        self.emotionalStateEdit = QTextEdit(self.scrollAreaWidgetContents)
        self.emotionalStateEdit.setObjectName(u"emotionalStateEdit")
        self.emotionalStateEdit.setMaximumSize(QSize(16777215, 80))

        self.formLayout.setWidget(6, QFormLayout.ItemRole.SpanningRole, self.emotionalStateEdit)

        self.relationshipsLabel = QLabel(self.scrollAreaWidgetContents)
        self.relationshipsLabel.setObjectName(u"relationshipsLabel")

        self.formLayout.setWidget(7, QFormLayout.ItemRole.LabelRole, self.relationshipsLabel)

        self.relationshipsEdit = QTextEdit(self.scrollAreaWidgetContents)
        self.relationshipsEdit.setObjectName(u"relationshipsEdit")
        self.relationshipsEdit.setMaximumSize(QSize(16777215, 80))

        self.formLayout.setWidget(8, QFormLayout.ItemRole.SpanningRole, self.relationshipsEdit)

        self.goalsLabel = QLabel(self.scrollAreaWidgetContents)
        self.goalsLabel.setObjectName(u"goalsLabel")

        self.formLayout.setWidget(9, QFormLayout.ItemRole.LabelRole, self.goalsLabel)

        self.goalsEdit = QTextEdit(self.scrollAreaWidgetContents)
        self.goalsEdit.setObjectName(u"goalsEdit")
        self.goalsEdit.setMaximumSize(QSize(16777215, 80))

        self.formLayout.setWidget(10, QFormLayout.ItemRole.SpanningRole, self.goalsEdit)

        self.conflictLabel = QLabel(self.scrollAreaWidgetContents)
        self.conflictLabel.setObjectName(u"conflictLabel")

        self.formLayout.setWidget(11, QFormLayout.ItemRole.LabelRole, self.conflictLabel)

        self.conflictEdit = QTextEdit(self.scrollAreaWidgetContents)
        self.conflictEdit.setObjectName(u"conflictEdit")
        self.conflictEdit.setMaximumSize(QSize(16777215, 80))

        self.formLayout.setWidget(12, QFormLayout.ItemRole.SpanningRole, self.conflictEdit)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.scrollArea)

        self.buttonBox = QDialogButtonBox(ArcPointDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(ArcPointDialog)
        self.buttonBox.accepted.connect(ArcPointDialog.accept)
        self.buttonBox.rejected.connect(ArcPointDialog.reject)

        QMetaObject.connectSlotsByName(ArcPointDialog)
    # setupUi

    def retranslateUi(self, ArcPointDialog):
        ArcPointDialog.setWindowTitle(QCoreApplication.translate("ArcPointDialog", u"Arc Point", None))
        self.titleLabel.setText(QCoreApplication.translate("ArcPointDialog", u"Add/Edit Arc Point", None))
        self.orderLabel.setText(QCoreApplication.translate("ArcPointDialog", u"Order Index:", None))
        self.titleArcLabel.setText(QCoreApplication.translate("ArcPointDialog", u"Title:", None))
        self.nodeLabel.setText(QCoreApplication.translate("ArcPointDialog", u"Story Node:", None))
        self.nodeComboBox.setItemText(0, QCoreApplication.translate("ArcPointDialog", u"No Node", None))

        self.descriptionLabel.setText(QCoreApplication.translate("ArcPointDialog", u"Description:", None))
        self.emotionalStateLabel.setText(QCoreApplication.translate("ArcPointDialog", u"Emotional State:", None))
        self.relationshipsLabel.setText(QCoreApplication.translate("ArcPointDialog", u"Character Relationships:", None))
        self.goalsLabel.setText(QCoreApplication.translate("ArcPointDialog", u"Goals:", None))
        self.conflictLabel.setText(QCoreApplication.translate("ArcPointDialog", u"Internal Conflict:", None))
    # retranslateUi

