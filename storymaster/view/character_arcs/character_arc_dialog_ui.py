# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'character_arc_dialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QAbstractItemView, QApplication, QComboBox,
    QDialog, QDialogButtonBox, QFormLayout, QLabel,
    QLineEdit, QListWidget, QListWidgetItem, QSizePolicy,
    QSpacerItem, QTextEdit, QVBoxLayout, QWidget)

class Ui_CharacterArcDialog(object):
    def setupUi(self, CharacterArcDialog):
        if not CharacterArcDialog.objectName():
            CharacterArcDialog.setObjectName(u"CharacterArcDialog")
        CharacterArcDialog.resize(500, 400)
        self.verticalLayout = QVBoxLayout(CharacterArcDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.titleLabel = QLabel(CharacterArcDialog)
        self.titleLabel.setObjectName(u"titleLabel")
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.titleLabel.setFont(font)

        self.verticalLayout.addWidget(self.titleLabel)

        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.arcTitleLabel = QLabel(CharacterArcDialog)
        self.arcTitleLabel.setObjectName(u"arcTitleLabel")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.arcTitleLabel)

        self.arcTitleEdit = QLineEdit(CharacterArcDialog)
        self.arcTitleEdit.setObjectName(u"arcTitleEdit")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.arcTitleEdit)

        self.arcTypeLabel = QLabel(CharacterArcDialog)
        self.arcTypeLabel.setObjectName(u"arcTypeLabel")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.arcTypeLabel)

        self.arcTypeComboBox = QComboBox(CharacterArcDialog)
        self.arcTypeComboBox.setObjectName(u"arcTypeComboBox")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.arcTypeComboBox)

        self.charactersLabel = QLabel(CharacterArcDialog)
        self.charactersLabel.setObjectName(u"charactersLabel")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.charactersLabel)

        self.charactersListWidget = QListWidget(CharacterArcDialog)
        self.charactersListWidget.setObjectName(u"charactersListWidget")
        self.charactersListWidget.setMaximumSize(QSize(16777215, 120))
        self.charactersListWidget.setSelectionMode(QAbstractItemView.MultiSelection)

        self.formLayout.setWidget(3, QFormLayout.ItemRole.SpanningRole, self.charactersListWidget)

        self.descriptionLabel = QLabel(CharacterArcDialog)
        self.descriptionLabel.setObjectName(u"descriptionLabel")

        self.formLayout.setWidget(4, QFormLayout.ItemRole.LabelRole, self.descriptionLabel)

        self.descriptionEdit = QTextEdit(CharacterArcDialog)
        self.descriptionEdit.setObjectName(u"descriptionEdit")
        self.descriptionEdit.setMaximumSize(QSize(16777215, 120))

        self.formLayout.setWidget(5, QFormLayout.ItemRole.SpanningRole, self.descriptionEdit)


        self.verticalLayout.addLayout(self.formLayout)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.buttonBox = QDialogButtonBox(CharacterArcDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(CharacterArcDialog)
        self.buttonBox.accepted.connect(CharacterArcDialog.accept)
        self.buttonBox.rejected.connect(CharacterArcDialog.reject)

        QMetaObject.connectSlotsByName(CharacterArcDialog)
    # setupUi

    def retranslateUi(self, CharacterArcDialog):
        CharacterArcDialog.setWindowTitle(QCoreApplication.translate("CharacterArcDialog", u"Character Arc", None))
        self.titleLabel.setText(QCoreApplication.translate("CharacterArcDialog", u"Add/Edit Character Arc", None))
        self.arcTitleLabel.setText(QCoreApplication.translate("CharacterArcDialog", u"Title:", None))
        self.arcTypeLabel.setText(QCoreApplication.translate("CharacterArcDialog", u"Arc Type:", None))
        self.charactersLabel.setText(QCoreApplication.translate("CharacterArcDialog", u"Characters:", None))
        self.descriptionLabel.setText(QCoreApplication.translate("CharacterArcDialog", u"Description:", None))
    # retranslateUi

