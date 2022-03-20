# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'tools\module\moduleeditor.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(970, 651)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.viewCreatureCheck = QtWidgets.QCheckBox(self.centralwidget)
        self.viewCreatureCheck.setStyleSheet("QCheckbox {\n"
"    spacing: 0px;\n"
"}\n"
"\n"
"QCheckBox::indicator {\n"
"    image: url(:/images/icons/k1/creature.png);\n"
"    border: 1px solid rgba(30, 144, 255, 0.0);\n"
"    width: 26px;\n"
"    height: 26px;\n"
"}\n"
"\n"
"QCheckBox::indicator:unchecked:hover {\n"
"    background: rgba(30, 144, 255, 0.2);\n"
"    border: 1px solid rgba(30, 144, 255, 0.4);\n"
"}\n"
"\n"
"QCheckBox::indicator:checked {\n"
"    background: rgba(30, 144, 255, 0.4);\n"
"    border:1px solid rgba(30, 144, 255, 0.6);\n"
"}\n"
"\n"
"QCheckBox::indicator:checked:hover {\n"
"    background: rgba(30, 144, 255, 0.5);\n"
"    border:1px solid rgba(30, 144, 255, 0.7);\n"
"}\n"
"\n"
"")
        self.viewCreatureCheck.setText("")
        self.viewCreatureCheck.setChecked(True)
        self.viewCreatureCheck.setObjectName("viewCreatureCheck")
        self.horizontalLayout_2.addWidget(self.viewCreatureCheck)
        self.viewDoorCheck = QtWidgets.QCheckBox(self.centralwidget)
        self.viewDoorCheck.setStyleSheet("QCheckBox::indicator {\n"
"    image: url(:/images/icons/k1/door.png);\n"
"    border: 1px solid rgba(30, 144, 255, 0.0);\n"
"    width: 26px;\n"
"    height: 26px;\n"
"}\n"
"\n"
"QCheckBox::indicator:unchecked:hover {\n"
"    background: rgba(30, 144, 255, 0.2);\n"
"    border: 1px solid rgba(30, 144, 255, 0.4);\n"
"}\n"
"\n"
"QCheckBox::indicator:checked {\n"
"    background: rgba(30, 144, 255, 0.4);\n"
"    border:1px solid rgba(30, 144, 255, 0.6);\n"
"}\n"
"\n"
"QCheckBox::indicator:checked:hover {\n"
"    background: rgba(30, 144, 255, 0.5);\n"
"    border:1px solid rgba(30, 144, 255, 0.7);\n"
"}\n"
"\n"
"")
        self.viewDoorCheck.setText("")
        self.viewDoorCheck.setChecked(True)
        self.viewDoorCheck.setObjectName("viewDoorCheck")
        self.horizontalLayout_2.addWidget(self.viewDoorCheck)
        self.viewPlaceableCheck = QtWidgets.QCheckBox(self.centralwidget)
        self.viewPlaceableCheck.setStyleSheet("QCheckBox::indicator {\n"
"    image: url(:/images/icons/k1/placeable.png);\n"
"    border: 1px solid rgba(30, 144, 255, 0.0);\n"
"    width: 26px;\n"
"    height: 26px;\n"
"}\n"
"\n"
"QCheckBox::indicator:unchecked:hover {\n"
"    background: rgba(30, 144, 255, 0.2);\n"
"    border: 1px solid rgba(30, 144, 255, 0.4);\n"
"}\n"
"\n"
"QCheckBox::indicator:checked {\n"
"    background: rgba(30, 144, 255, 0.4);\n"
"    border:1px solid rgba(30, 144, 255, 0.6);\n"
"}\n"
"\n"
"QCheckBox::indicator:checked:hover {\n"
"    background: rgba(30, 144, 255, 0.5);\n"
"    border:1px solid rgba(30, 144, 255, 0.7);\n"
"}\n"
"\n"
"")
        self.viewPlaceableCheck.setText("")
        self.viewPlaceableCheck.setChecked(True)
        self.viewPlaceableCheck.setObjectName("viewPlaceableCheck")
        self.horizontalLayout_2.addWidget(self.viewPlaceableCheck)
        self.viewStoreCheck = QtWidgets.QCheckBox(self.centralwidget)
        self.viewStoreCheck.setStyleSheet("QCheckBox::indicator {\n"
"    image: url(:/images/icons/k1/merchant.png);\n"
"    border: 1px solid rgba(30, 144, 255, 0.0);\n"
"    width: 26px;\n"
"    height: 26px;\n"
"}\n"
"\n"
"QCheckBox::indicator:unchecked:hover {\n"
"    background: rgba(30, 144, 255, 0.2);\n"
"    border: 1px solid rgba(30, 144, 255, 0.4);\n"
"}\n"
"\n"
"QCheckBox::indicator:checked {\n"
"    background: rgba(30, 144, 255, 0.4);\n"
"    border:1px solid rgba(30, 144, 255, 0.6);\n"
"}\n"
"\n"
"QCheckBox::indicator:checked:hover {\n"
"    background: rgba(30, 144, 255, 0.5);\n"
"    border:1px solid rgba(30, 144, 255, 0.7);\n"
"}\n"
"\n"
"")
        self.viewStoreCheck.setText("")
        self.viewStoreCheck.setChecked(True)
        self.viewStoreCheck.setObjectName("viewStoreCheck")
        self.horizontalLayout_2.addWidget(self.viewStoreCheck)
        self.viewSoundCheck = QtWidgets.QCheckBox(self.centralwidget)
        self.viewSoundCheck.setStyleSheet("QCheckBox::indicator {\n"
"    image: url(:/images/icons/k1/sound.png);\n"
"    border: 1px solid rgba(30, 144, 255, 0.0);\n"
"    width: 26px;\n"
"    height: 26px;\n"
"}\n"
"\n"
"QCheckBox::indicator:unchecked:hover {\n"
"    background: rgba(30, 144, 255, 0.2);\n"
"    border: 1px solid rgba(30, 144, 255, 0.4);\n"
"}\n"
"\n"
"QCheckBox::indicator:checked {\n"
"    background: rgba(30, 144, 255, 0.4);\n"
"    border:1px solid rgba(30, 144, 255, 0.6);\n"
"}\n"
"\n"
"QCheckBox::indicator:checked:hover {\n"
"    background: rgba(30, 144, 255, 0.5);\n"
"    border:1px solid rgba(30, 144, 255, 0.7);\n"
"}\n"
"\n"
"")
        self.viewSoundCheck.setText("")
        self.viewSoundCheck.setChecked(True)
        self.viewSoundCheck.setObjectName("viewSoundCheck")
        self.horizontalLayout_2.addWidget(self.viewSoundCheck)
        self.viewWaypointCheck = QtWidgets.QCheckBox(self.centralwidget)
        self.viewWaypointCheck.setStyleSheet("QCheckBox::indicator {\n"
"    image: url(:/images/icons/k1/waypoint.png);\n"
"    border: 1px solid rgba(30, 144, 255, 0.0);\n"
"    width: 26px;\n"
"    height: 26px;\n"
"}\n"
"\n"
"QCheckBox::indicator:unchecked:hover {\n"
"    background: rgba(30, 144, 255, 0.2);\n"
"    border: 1px solid rgba(30, 144, 255, 0.4);\n"
"}\n"
"\n"
"QCheckBox::indicator:checked {\n"
"    background: rgba(30, 144, 255, 0.4);\n"
"    border:1px solid rgba(30, 144, 255, 0.6);\n"
"}\n"
"\n"
"QCheckBox::indicator:checked:hover {\n"
"    background: rgba(30, 144, 255, 0.5);\n"
"    border:1px solid rgba(30, 144, 255, 0.7);\n"
"}\n"
"\n"
"")
        self.viewWaypointCheck.setText("")
        self.viewWaypointCheck.setChecked(True)
        self.viewWaypointCheck.setObjectName("viewWaypointCheck")
        self.horizontalLayout_2.addWidget(self.viewWaypointCheck)
        self.viewCameraCheck = QtWidgets.QCheckBox(self.centralwidget)
        self.viewCameraCheck.setStyleSheet("QCheckBox::indicator {\n"
"    image: url(:/images/icons/k1/camera.png);\n"
"    border: 1px solid rgba(30, 144, 255, 0.0);\n"
"    width: 26px;\n"
"    height: 26px;\n"
"}\n"
"\n"
"QCheckBox::indicator:unchecked:hover {\n"
"    background: rgba(30, 144, 255, 0.2);\n"
"    border: 1px solid rgba(30, 144, 255, 0.4);\n"
"}\n"
"\n"
"QCheckBox::indicator:checked {\n"
"    background: rgba(30, 144, 255, 0.4);\n"
"    border:1px solid rgba(30, 144, 255, 0.6);\n"
"}\n"
"\n"
"QCheckBox::indicator:checked:hover {\n"
"    background: rgba(30, 144, 255, 0.5);\n"
"    border:1px solid rgba(30, 144, 255, 0.7);\n"
"}\n"
"\n"
"")
        self.viewCameraCheck.setText("")
        self.viewCameraCheck.setChecked(True)
        self.viewCameraCheck.setObjectName("viewCameraCheck")
        self.horizontalLayout_2.addWidget(self.viewCameraCheck)
        self.viewEncounterCheck = QtWidgets.QCheckBox(self.centralwidget)
        self.viewEncounterCheck.setStyleSheet("QCheckBox::indicator {\n"
"    image: url(:/images/icons/k1/encounter.png);\n"
"    border: 1px solid rgba(30, 144, 255, 0.0);\n"
"    width: 26px;\n"
"    height: 26px;\n"
"}\n"
"\n"
"QCheckBox::indicator:unchecked:hover {\n"
"    background: rgba(30, 144, 255, 0.2);\n"
"    border: 1px solid rgba(30, 144, 255, 0.4);\n"
"}\n"
"\n"
"QCheckBox::indicator:checked {\n"
"    background: rgba(30, 144, 255, 0.4);\n"
"    border:1px solid rgba(30, 144, 255, 0.6);\n"
"}\n"
"\n"
"QCheckBox::indicator:checked:hover {\n"
"    background: rgba(30, 144, 255, 0.5);\n"
"    border:1px solid rgba(30, 144, 255, 0.7);\n"
"}\n"
"\n"
"")
        self.viewEncounterCheck.setText("")
        self.viewEncounterCheck.setChecked(True)
        self.viewEncounterCheck.setObjectName("viewEncounterCheck")
        self.horizontalLayout_2.addWidget(self.viewEncounterCheck)
        self.viewTriggerCheck = QtWidgets.QCheckBox(self.centralwidget)
        self.viewTriggerCheck.setStyleSheet("QCheckBox::indicator {\n"
"    image: url(:/images/icons/k1/trigger.png);\n"
"    border: 1px solid rgba(30, 144, 255, 0.0);\n"
"    width: 26px;\n"
"    height: 26px;\n"
"}\n"
"\n"
"QCheckBox::indicator:unchecked:hover {\n"
"    background: rgba(30, 144, 255, 0.2);\n"
"    border: 1px solid rgba(30, 144, 255, 0.4);\n"
"}\n"
"\n"
"QCheckBox::indicator:checked {\n"
"    background: rgba(30, 144, 255, 0.4);\n"
"    border:1px solid rgba(30, 144, 255, 0.6);\n"
"}\n"
"\n"
"QCheckBox::indicator:checked:hover {\n"
"    background: rgba(30, 144, 255, 0.5);\n"
"    border:1px solid rgba(30, 144, 255, 0.7);\n"
"}\n"
"\n"
"")
        self.viewTriggerCheck.setText("")
        self.viewTriggerCheck.setChecked(True)
        self.viewTriggerCheck.setObjectName("viewTriggerCheck")
        self.horizontalLayout_2.addWidget(self.viewTriggerCheck)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.resourceTree = QtWidgets.QTreeWidget(self.centralwidget)
        self.resourceTree.setMaximumSize(QtCore.QSize(200, 16777215))
        self.resourceTree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.resourceTree.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.resourceTree.setHeaderHidden(True)
        self.resourceTree.setObjectName("resourceTree")
        self.resourceTree.headerItem().setText(0, "1")
        self.horizontalLayout.addWidget(self.resourceTree)
        self.mainRenderer = ModuleRenderer(self.centralwidget)
        self.mainRenderer.setObjectName("mainRenderer")
        self.horizontalLayout.addWidget(self.mainRenderer)
        self.instanceList = QtWidgets.QListView(self.centralwidget)
        self.instanceList.setMaximumSize(QtCore.QSize(200, 16777215))
        self.instanceList.setObjectName("instanceList")
        self.horizontalLayout.addWidget(self.instanceList)
        self.horizontalLayout.setStretch(1, 1)
        self.verticalLayout.addLayout(self.horizontalLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 970, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
from toolset.tools.module.moduleeditor import ModuleRenderer
import resources_rc
