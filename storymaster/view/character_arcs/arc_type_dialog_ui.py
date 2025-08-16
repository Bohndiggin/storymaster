# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'arc_type_dialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QFormLayout, QLabel, QLineEdit, QSizePolicy,
    QSpacerItem, QTextEdit, QVBoxLayout, QWidget)

class Ui_ArcTypeDialog(object):
    def setupUi(self, ArcTypeDialog):
        if not ArcTypeDialog.objectName():
            ArcTypeDialog.setObjectName(u"ArcTypeDialog")
        ArcTypeDialog.resize(400, 250)
        self.verticalLayout = QVBoxLayout(ArcTypeDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.titleLabel = QLabel(ArcTypeDialog)
        self.titleLabel.setObjectName(u"titleLabel")
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.titleLabel.setFont(font)

        self.verticalLayout.addWidget(self.titleLabel)

        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.nameLabel = QLabel(ArcTypeDialog)
        self.nameLabel.setObjectName(u"nameLabel")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.nameLabel)

        self.nameEdit = QLineEdit(ArcTypeDialog)
        self.nameEdit.setObjectName(u"nameEdit")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.nameEdit)

        self.descriptionLabel = QLabel(ArcTypeDialog)
        self.descriptionLabel.setObjectName(u"descriptionLabel")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.descriptionLabel)

        self.descriptionEdit = QTextEdit(ArcTypeDialog)
        self.descriptionEdit.setObjectName(u"descriptionEdit")
        self.descriptionEdit.setMaximumSize(QSize(16777215, 100))

        self.formLayout.setWidget(2, QFormLayout.ItemRole.SpanningRole, self.descriptionEdit)


        self.verticalLayout.addLayout(self.formLayout)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.buttonBox = QDialogButtonBox(ArcTypeDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(ArcTypeDialog)
        self.buttonBox.accepted.connect(ArcTypeDialog.accept)
        self.buttonBox.rejected.connect(ArcTypeDialog.reject)

        QMetaObject.connectSlotsByName(ArcTypeDialog)
    # setupUi

    def retranslateUi(self, ArcTypeDialog):
        ArcTypeDialog.setWindowTitle(QCoreApplication.translate("ArcTypeDialog", u"Arc Type", None))
        self.titleLabel.setText(QCoreApplication.translate("ArcTypeDialog", u"Add/Edit Arc Type", None))
        self.nameLabel.setText(QCoreApplication.translate("ArcTypeDialog", u"Name:", None))
        self.descriptionLabel.setText(QCoreApplication.translate("ArcTypeDialog", u"Description:", None))
    # retranslateUi

