# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'tools\indoormap\indoorbuilder.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.kitSelect = QtWidgets.QComboBox(self.centralwidget)
        self.kitSelect.setObjectName("kitSelect")
        self.verticalLayout.addWidget(self.kitSelect)
        self.componentList = QtWidgets.QListWidget(self.centralwidget)
        self.componentList.setObjectName("componentList")
        self.verticalLayout.addWidget(self.componentList)
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.componentImage = QtWidgets.QLabel(self.groupBox)
        self.componentImage.setMinimumSize(QtCore.QSize(128, 128))
        self.componentImage.setMaximumSize(QtCore.QSize(128, 128))
        self.componentImage.setText("")
        self.componentImage.setScaledContents(True)
        self.componentImage.setObjectName("componentImage")
        self.gridLayout.addWidget(self.componentImage, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.groupBox)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.mapRenderer = IndoorMapRenderer(self.centralwidget)
        self.mapRenderer.setMouseTracking(True)
        self.mapRenderer.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.mapRenderer.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.mapRenderer.setObjectName("mapRenderer")
        self.horizontalLayout.addWidget(self.mapRenderer)
        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 3)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        self.menuNew = QtWidgets.QMenu(self.menubar)
        self.menuNew.setObjectName("menuNew")
        self.menuEdit = QtWidgets.QMenu(self.menubar)
        self.menuEdit.setObjectName("menuEdit")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionOpen = QtWidgets.QAction(MainWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.actionSave = QtWidgets.QAction(MainWindow)
        self.actionSave.setObjectName("actionSave")
        self.actionSaveAs = QtWidgets.QAction(MainWindow)
        self.actionSaveAs.setObjectName("actionSaveAs")
        self.actionNew = QtWidgets.QAction(MainWindow)
        self.actionNew.setObjectName("actionNew")
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.actionBuild = QtWidgets.QAction(MainWindow)
        self.actionBuild.setObjectName("actionBuild")
        self.actionSettings = QtWidgets.QAction(MainWindow)
        self.actionSettings.setObjectName("actionSettings")
        self.actionDeleteSelected = QtWidgets.QAction(MainWindow)
        self.actionDeleteSelected.setObjectName("actionDeleteSelected")
        self.actionDownloadKits = QtWidgets.QAction(MainWindow)
        self.actionDownloadKits.setObjectName("actionDownloadKits")
        self.menuNew.addAction(self.actionNew)
        self.menuNew.addAction(self.actionOpen)
        self.menuNew.addAction(self.actionSave)
        self.menuNew.addAction(self.actionSaveAs)
        self.menuNew.addSeparator()
        self.menuNew.addAction(self.actionBuild)
        self.menuNew.addAction(self.actionSettings)
        self.menuNew.addSeparator()
        self.menuNew.addAction(self.actionDownloadKits)
        self.menuNew.addSeparator()
        self.menuNew.addAction(self.actionExit)
        self.menuNew.addSeparator()
        self.menuEdit.addAction(self.actionDeleteSelected)
        self.menubar.addAction(self.menuNew.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Map Builder"))
        self.menuNew.setTitle(_translate("MainWindow", "File"))
        self.menuEdit.setTitle(_translate("MainWindow", "Edit"))
        self.actionOpen.setText(_translate("MainWindow", "Open"))
        self.actionSave.setText(_translate("MainWindow", "Save"))
        self.actionSaveAs.setText(_translate("MainWindow", "Save As"))
        self.actionNew.setText(_translate("MainWindow", "New"))
        self.actionExit.setText(_translate("MainWindow", "Exit"))
        self.actionBuild.setText(_translate("MainWindow", "Build"))
        self.actionSettings.setText(_translate("MainWindow", "Settings"))
        self.actionDeleteSelected.setText(_translate("MainWindow", "Delete Selected"))
        self.actionDownloadKits.setText(_translate("MainWindow", "Download Kits"))
from toolset.tools.indoormap.indoorbuilder import IndoorMapRenderer
