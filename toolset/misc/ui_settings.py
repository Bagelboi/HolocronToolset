# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'misc\settings.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(500, 313)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabWidget = QtWidgets.QTabWidget(Dialog)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout(self.tab)
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.pathList = QtWidgets.QListView(self.tab)
        self.pathList.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.pathList.setObjectName("pathList")
        self.verticalLayout_2.addWidget(self.pathList)
        self.addPathButton = QtWidgets.QPushButton(self.tab)
        self.addPathButton.setObjectName("addPathButton")
        self.verticalLayout_2.addWidget(self.addPathButton)
        self.removePathButton = QtWidgets.QPushButton(self.tab)
        self.removePathButton.setObjectName("removePathButton")
        self.verticalLayout_2.addWidget(self.removePathButton)
        self.horizontalLayout_8.addLayout(self.verticalLayout_2)
        self.line = QtWidgets.QFrame(self.tab)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.horizontalLayout_8.addWidget(self.line)
        self.pathFrame = QtWidgets.QFrame(self.tab)
        self.pathFrame.setEnabled(False)
        self.pathFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.pathFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.pathFrame.setObjectName("pathFrame")
        self.formLayout_2 = QtWidgets.QFormLayout(self.pathFrame)
        self.formLayout_2.setObjectName("formLayout_2")
        self.label_11 = QtWidgets.QLabel(self.pathFrame)
        self.label_11.setObjectName("label_11")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_11)
        self.pathNameEdit = QtWidgets.QLineEdit(self.pathFrame)
        self.pathNameEdit.setObjectName("pathNameEdit")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.pathNameEdit)
        self.label_12 = QtWidgets.QLabel(self.pathFrame)
        self.label_12.setObjectName("label_12")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_12)
        self.pathDirEdit = QtWidgets.QLineEdit(self.pathFrame)
        self.pathDirEdit.setObjectName("pathDirEdit")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.pathDirEdit)
        self.label_13 = QtWidgets.QLabel(self.pathFrame)
        self.label_13.setObjectName("label_13")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_13)
        self.pathTslCheckbox = QtWidgets.QCheckBox(self.pathFrame)
        self.pathTslCheckbox.setText("")
        self.pathTslCheckbox.setObjectName("pathTslCheckbox")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.pathTslCheckbox)
        self.horizontalLayout_8.addWidget(self.pathFrame)
        self.horizontalLayout_8.setStretch(0, 1)
        self.horizontalLayout_8.setStretch(2, 2)
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.gridLayout = QtWidgets.QGridLayout(self.tab_2)
        self.gridLayout.setObjectName("gridLayout")
        self.scrollArea = QtWidgets.QScrollArea(self.tab_2)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 456, 218))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.formLayout = QtWidgets.QFormLayout(self.scrollAreaWidgetContents)
        self.formLayout.setObjectName("formLayout")
        self.label_5 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.label_5.setObjectName("label_5")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_5)
        self.utxToolCombo = QtWidgets.QComboBox(self.scrollAreaWidgetContents)
        self.utxToolCombo.setObjectName("utxToolCombo")
        self.utxToolCombo.addItem("")
        self.utxToolCombo.addItem("")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.utxToolCombo)
        self.label_4 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.nssCompToolCombo = QtWidgets.QComboBox(self.scrollAreaWidgetContents)
        self.nssCompToolCombo.setEnabled(False)
        self.nssCompToolCombo.setMinimumSize(QtCore.QSize(80, 0))
        self.nssCompToolCombo.setObjectName("nssCompToolCombo")
        self.nssCompToolCombo.addItem("")
        self.horizontalLayout_2.addWidget(self.nssCompToolCombo)
        self.nssCompToolEdit = QtWidgets.QLineEdit(self.scrollAreaWidgetContents)
        self.nssCompToolEdit.setEnabled(True)
        self.nssCompToolEdit.setObjectName("nssCompToolEdit")
        self.horizontalLayout_2.addWidget(self.nssCompToolEdit)
        self.formLayout.setLayout(1, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout_2)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.ncsToolCombo = QtWidgets.QComboBox(self.scrollAreaWidgetContents)
        self.ncsToolCombo.setEnabled(False)
        self.ncsToolCombo.setMinimumSize(QtCore.QSize(80, 0))
        self.ncsToolCombo.setObjectName("ncsToolCombo")
        self.ncsToolCombo.addItem("")
        self.horizontalLayout_7.addWidget(self.ncsToolCombo)
        self.ncsToolEdit = QtWidgets.QLineEdit(self.scrollAreaWidgetContents)
        self.ncsToolEdit.setEnabled(True)
        self.ncsToolEdit.setObjectName("ncsToolEdit")
        self.horizontalLayout_7.addWidget(self.ncsToolEdit)
        self.formLayout.setLayout(2, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout_7)
        self.label_10 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.label_10.setObjectName("label_10")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_10)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.mdlToolCombo = QtWidgets.QComboBox(self.scrollAreaWidgetContents)
        self.mdlToolCombo.setEnabled(False)
        self.mdlToolCombo.setMinimumSize(QtCore.QSize(80, 0))
        self.mdlToolCombo.setObjectName("mdlToolCombo")
        self.mdlToolCombo.addItem("")
        self.horizontalLayout_3.addWidget(self.mdlToolCombo)
        self.mdlToolEdit = QtWidgets.QLineEdit(self.scrollAreaWidgetContents)
        self.mdlToolEdit.setEnabled(False)
        self.mdlToolEdit.setObjectName("mdlToolEdit")
        self.horizontalLayout_3.addWidget(self.mdlToolEdit)
        self.formLayout.setLayout(3, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout_3)
        self.label_6 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.label_6.setObjectName("label_6")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_6)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout.addWidget(self.scrollArea, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab_2, "")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.tab_3)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.scrollArea_2 = QtWidgets.QScrollArea(self.tab_3)
        self.scrollArea_2.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollArea_2.setObjectName("scrollArea_2")
        self.scrollAreaWidgetContents_2 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_2.setGeometry(QtCore.QRect(0, 0, 456, 218))
        self.scrollAreaWidgetContents_2.setObjectName("scrollAreaWidgetContents_2")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents_2)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.formLayout_3 = QtWidgets.QFormLayout()
        self.formLayout_3.setObjectName("formLayout_3")
        self.label = QtWidgets.QLabel(self.scrollAreaWidgetContents_2)
        self.label.setObjectName("label")
        self.formLayout_3.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.tempMiscEdit = QtWidgets.QLineEdit(self.scrollAreaWidgetContents_2)
        self.tempMiscEdit.setObjectName("tempMiscEdit")
        self.formLayout_3.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.tempMiscEdit)
        self.verticalLayout_3.addLayout(self.formLayout_3)
        self.scrollArea_2.setWidget(self.scrollAreaWidgetContents_2)
        self.gridLayout_2.addWidget(self.scrollArea_2, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab_3, "")
        self.verticalLayout.addWidget(self.tabWidget)
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_9.addItem(spacerItem)
        self.okButton = QtWidgets.QPushButton(Dialog)
        self.okButton.setObjectName("okButton")
        self.horizontalLayout_9.addWidget(self.okButton)
        self.applyButton = QtWidgets.QPushButton(Dialog)
        self.applyButton.setObjectName("applyButton")
        self.horizontalLayout_9.addWidget(self.applyButton)
        self.cancelButton = QtWidgets.QPushButton(Dialog)
        self.cancelButton.setObjectName("cancelButton")
        self.horizontalLayout_9.addWidget(self.cancelButton)
        self.verticalLayout.addLayout(self.horizontalLayout_9)

        self.retranslateUi(Dialog)
        self.tabWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Settings"))
        self.addPathButton.setText(_translate("Dialog", "Add"))
        self.removePathButton.setText(_translate("Dialog", "Remove"))
        self.label_11.setText(_translate("Dialog", "Name:"))
        self.label_12.setText(_translate("Dialog", "Path:"))
        self.label_13.setText(_translate("Dialog", "TSL:"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("Dialog", "Paths"))
        self.label_5.setText(_translate("Dialog", "GFF Files:"))
        self.utxToolCombo.setItemText(0, _translate("Dialog", "GFF Editor"))
        self.utxToolCombo.setItemText(1, _translate("Dialog", "Specialized Editor"))
        self.label_4.setText(_translate("Dialog", "NSS Compiler:"))
        self.nssCompToolCombo.setItemText(0, _translate("Dialog", "External"))
        self.ncsToolCombo.setItemText(0, _translate("Dialog", "External"))
        self.label_10.setText(_translate("Dialog", "NCS Decompiler:"))
        self.mdlToolCombo.setItemText(0, _translate("Dialog", "Internal"))
        self.label_6.setText(_translate("Dialog", "MDL Decompiler:"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("Dialog", "Tools"))
        self.label.setText(_translate("Dialog", "Extract Directory:"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("Dialog", "Misc"))
        self.okButton.setText(_translate("Dialog", "OK"))
        self.applyButton.setText(_translate("Dialog", "Apply"))
        self.cancelButton.setText(_translate("Dialog", "Cancel"))