# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'misc\help\discord.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(220, 118)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.htButton = QtWidgets.QPushButton(Dialog)
        self.htButton.setObjectName("htButton")
        self.verticalLayout.addWidget(self.htButton)
        self.dsButton = QtWidgets.QPushButton(Dialog)
        self.dsButton.setObjectName("dsButton")
        self.verticalLayout.addWidget(self.dsButton)
        self.kotorButton = QtWidgets.QPushButton(Dialog)
        self.kotorButton.setObjectName("kotorButton")
        self.verticalLayout.addWidget(self.kotorButton)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Discord Links"))
        self.label.setText(_translate("Dialog", "Discord Servers:"))
        self.htButton.setText(_translate("Dialog", "Holcron Toolset"))
        self.dsButton.setText(_translate("Dialog", "Deadly Stream"))
        self.kotorButton.setText(_translate("Dialog", "KOTOR"))