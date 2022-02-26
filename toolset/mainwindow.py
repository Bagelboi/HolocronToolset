from __future__ import annotations

import json
import multiprocessing
import os
import subprocess
import traceback
from contextlib import suppress
from distutils.version import StrictVersion
from time import sleep
from typing import Optional, List, Union, Tuple, Dict


import requests
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QSortFilterProxyModel, QModelIndex, QThread, QPoint
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon, QPixmap, QImage, QCloseEvent, QTransform, QResizeEvent
from PyQt5.QtWidgets import QMainWindow, QFileDialog,QWidget, QMessageBox, QHeaderView, QAbstractItemView, QListView
from pykotor.common.stream import BinaryReader
from pykotor.extract.file import FileResource, ResourceIdentifier
from pykotor.extract.installation import SearchLocation
from pykotor.resource.formats.erf import load_erf, ERFType, write_erf
from pykotor.resource.formats.mdl import load_mdl, write_mdl
from pykotor.resource.formats.rim import write_rim, load_rim
from pykotor.resource.formats.tpc import load_tpc, write_tpc, TPCTextureFormat, TPC
from pykotor.resource.type import ResourceType
from watchdog.events import FileSystemEventHandler, FileModifiedEvent
from watchdog.observers import Observer

import mainwindow_ui
from data.configuration import Configuration, InstallationConfig
from data.installation import HTInstallation
from editors.bwm.bwm_editor import BWMEditor
from editors.dlg.dlg_editor import DLGEditor
from editors.editor import Editor
from editors.erf.erf_editor import ERFEditor
from editors.gff.gff_editor import GFFEditor
from editors.jrl.jrl_editor import JRLEditor
from editors.nss.nss_editor import NSSEditor
from editors.ssf.sff_editor import SSFEditor
from editors.tlk.tlk_editor import TLKEditor
from editors.tpc.tpc_editor import TPCEditor
from editors.twoda.twoda_editor import TwoDAEditor
from editors.txt.txt_editor import TXTEditor
from editors.utc.utc_editor import UTCEditor
from editors.utd.utd_editor import UTDEditor
from editors.ute.ute_editor import UTEEditor
from editors.uti.uti_editor import UTIEditor
from editors.utm.utm_editor import UTMEditor
from editors.utp.utp_editor import UTPEditor
from editors.uts.uts_editor import UTSEditor
from editors.utt.utt_editor import UTTEditor
from editors.utw.utw_editor import UTWEditor
from misc.about import About
from misc.asyncloader import AsyncLoader, AsyncBatchLoader
from misc.audio_player import AudioPlayer
from misc.settings import Settings
from misc.clone_module import CloneModuleDialog

import resources_rc


PROGRAM_VERSION = "1.4.0"


class ToolWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = mainwindow_ui.Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(QPixmap(":/images/icons/sith.png")))

        self.active: Optional[HTInstallation] = None
        self.config = Configuration()

        firstTime = self.config.firstTime
        if firstTime:
            self.config.installations = []
            self.config.installations.append(InstallationConfig("KotOR", "", False))
            self.config.installations.append(InstallationConfig("TSL", "", True))

            self.config.firstTime = False

            with suppress(Exception):
                extractPath = os.path.realpath('.') + "/ext"
                os.mkdir(extractPath)
                self.config.extractPath = extractPath

            self.config.save()

        self.installations = {}

        self.ui.resourceTabs.setEnabled(False)
        self.ui.sidebar.setEnabled(False)
        self.ui.resourceTabs.currentChanged.connect(self.resizeColumns)
        self.ui.gameCombo.currentIndexChanged.connect(self.changeActiveInstallation)
        self.ui.extractButton.clicked.connect(self.extractFromSelected)
        self.ui.openButton.clicked.connect(self.openFromSelected)

        self.ui.coreSearchEdit.textEdited.connect(self.filterDataModel)

        self.ui.moduleSearchEdit.textEdited.connect(self.filterDataModel)
        self.ui.moduleReloadButton.clicked.connect(self.reloadModule)
        self.ui.moduleRefreshButton.clicked.connect(lambda: self.refreshModuleList(True))
        self.ui.modulesCombo.currentIndexChanged.connect(lambda index: self.changeModule(self._modules_list[self.active.name].index(index, 0).data(QtCore.Qt.UserRole)))

        self.ui.overrideSearchEdit.textEdited.connect(self.filterDataModel)
        self.ui.overrideRefreshButton.clicked.connect(self.refreshOverrideList)
        self.ui.overrideReloadButton.clicked.connect(self.reloadOverride)
        self.ui.overrideFolderCombo.currentTextChanged.connect(self.changeOverrideFolder)

        self.ui.texturesCombo.currentTextChanged.connect(self.changeTexturePack)
        self.ui.textureSearchEdit.textEdited.connect(self.filterDataModel)
        self.ui.textureSearchEdit.textEdited.connect(self.ui.texturesList.loadVisibleTextures)

        self.ui.openAction.triggered.connect(self.openFromFile)
        self.ui.actionSettings.triggered.connect(self.openSettingsDialog)
        self.ui.actionExit.triggered.connect(self.close)
        self.ui.actionNewDLG.triggered.connect(lambda: DLGEditor(self, self.active).show())
        self.ui.actionNewNSS.triggered.connect(lambda: NSSEditor(self, self.active).show())
        self.ui.actionNewUTC.triggered.connect(lambda: UTCEditor(self, self.active).show())
        self.ui.actionNewUTP.triggered.connect(lambda: UTPEditor(self, self.active).show())
        self.ui.actionNewUTD.triggered.connect(lambda: UTDEditor(self, self.active).show())
        self.ui.actionNewUTI.triggered.connect(lambda: UTIEditor(self, self.active).show())
        self.ui.actionNewUTT.triggered.connect(lambda: UTTEditor(self, self.active).show())
        self.ui.actionNewUTM.triggered.connect(lambda: UTMEditor(self, self.active).show())
        self.ui.actionNewUTW.triggered.connect(lambda: UTWEditor(self, self.active).show())
        self.ui.actionNewUTE.triggered.connect(lambda: UTEEditor(self, self.active).show())
        self.ui.actionNewUTS.triggered.connect(lambda: UTSEditor(self, self.active).show())
        self.ui.actionNewGFF.triggered.connect(lambda: GFFEditor(self, self.active).show())
        self.ui.actionNewERF.triggered.connect(lambda: ERFEditor(self, self.active).show())
        self.ui.actionNewTXT.triggered.connect(lambda: TXTEditor(self, self.active).show())
        self.ui.actionNewSSF.triggered.connect(lambda: SSFEditor(self, self.active).show())
        self.ui.actionCloneModule.triggered.connect(lambda: CloneModuleDialog(self, self.active, self.installations).exec_())
        self.ui.actionEditTLK.triggered.connect(self.openActiveTalktable)
        self.ui.actionEditJRL.triggered.connect(self.openActiveJournal)
        self.ui.actionHelpUpdates.triggered.connect(self.checkForUpdates)
        self.ui.actionHelpAbout.triggered.connect(self.openAboutDialog)

        self._core_models: Dict[str, ResourceModel] = {}
        self.ui.coreTree.setModel(ResourceModel())
        self.ui.coreTree.header().resizeSection(1, 40)
        self.ui.coreTree.setSortingEnabled(True)
        self.ui.coreTree.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.ui.coreTree.doubleClicked.connect(self.openFromSelected)

        self.modulesModel = ResourceModel()
        self.ui.modulesTree.setModel(self.modulesModel.proxyModel())
        self.ui.modulesTree.header().resizeSection(1, 40)
        self.ui.modulesTree.setSortingEnabled(True)
        self.ui.modulesTree.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.ui.modulesTree.doubleClicked.connect(self.openFromSelected)
        self._modules_list: Dict[str, QStandardItemModel] = {}
        self.ui.modulesCombo.setModel(QStandardItemModel())

        self.overrideModel = ResourceModel()
        self.ui.overrideTree.setModel(self.overrideModel.proxyModel())
        self.ui.overrideTree.header().resizeSection(1, 40)
        self.ui.overrideTree.setSortingEnabled(True)
        self.ui.overrideTree.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.ui.overrideTree.doubleClicked.connect(self.openFromSelected)

        self.texturesModel = TextureListModel()
        self.ui.texturesList.setModel(self.texturesModel.proxyModel())
        self.ui.texturesList.doubleClicked.connect(self.openFromSelected)

        self._clearModels()
        self.reloadSettings()

        self.checkForUpdates(True)

    def closeEvent(self, e: QCloseEvent) -> None:
        self.ui.texturesList.stop()

    def refreshTexturePackList(self):
        self.ui.texturesCombo.clear()
        for texturepack in self.active.texturepacks_list():
            self.ui.texturesCombo.addItem(texturepack)

    def changeTexturePack(self, texturepack: str):
        self.texturesModel = TextureListModel()
        self.ui.texturesList.setModel(self.texturesModel.proxyModel())

        if texturepack == "":
            return

        self.texturesModel.proxyModel().setFilterFixedString(self.ui.textureSearchEdit.text())
        image = QImage(bytes([0 for i in range(64 * 64 * 3)]), 64, 64, QImage.Format_RGB888)
        icon = QIcon(QPixmap.fromImage(image))

        for texture in self.active.texturepack_resources(texturepack):
            if texture.restype() in [ResourceType.TPC, ResourceType.TGA]:
                item = QStandardItem(icon, texture.resname())
                item.setToolTip(texture.resname())
                item.resource = texture
                item.setData(False, QtCore.Qt.UserRole)  # Mark as unloaded
                self.texturesModel.appendRow(item)
        self.ui.texturesList.setInstallation(self.active)

    def updateMenus(self) -> None:
        version = "x" if self.active is None else "2" if self.active.tsl else "1"

        dialogIconPath = ":/images/icons/k{}/dialog.png".format(version)
        self.ui.actionNewDLG.setIcon(QIcon(QPixmap(dialogIconPath)))
        self.ui.actionNewDLG.setEnabled(self.active is not None)

        scriptIconPath = ":/images/icons/k{}/script.png".format(version)
        self.ui.actionNewNSS.setIcon(QIcon(QPixmap(scriptIconPath)))
        self.ui.actionNewNSS.setEnabled(self.active is not None)

        creatureIconPath = ":/images/icons/k{}/creature.png".format(version)
        self.ui.actionNewUTC.setIcon(QIcon(QPixmap(creatureIconPath)))
        self.ui.actionNewUTC.setEnabled(self.active is not None)

        placeableIconPath = ":/images/icons/k{}/placeable.png".format(version)
        self.ui.actionNewUTP.setIcon(QIcon(QPixmap(placeableIconPath)))
        self.ui.actionNewUTP.setEnabled(self.active is not None)

        doorIconPath = ":/images/icons/k{}/door.png".format(version)
        self.ui.actionNewUTD.setIcon(QIcon(QPixmap(doorIconPath)))
        self.ui.actionNewUTD.setEnabled(self.active is not None)

        itemIconPath = ":/images/icons/k{}/item.png".format(version)
        self.ui.actionNewUTI.setIcon(QIcon(QPixmap(itemIconPath)))
        self.ui.actionNewUTI.setEnabled(self.active is not None)

        soundIconPath = ":/images/icons/k{}/sound.png".format(version)
        self.ui.actionNewUTS.setIcon(QIcon(QPixmap(soundIconPath)))
        self.ui.actionNewUTS.setEnabled(self.active is not None)

        triggerIconPath = ":/images/icons/k{}/trigger.png".format(version)
        self.ui.actionNewUTT.setIcon(QIcon(QPixmap(triggerIconPath)))
        self.ui.actionNewUTT.setEnabled(self.active is not None)

        merchantIconPath = ":/images/icons/k{}/merchant.png".format(version)
        self.ui.actionNewUTM.setIcon(QIcon(QPixmap(merchantIconPath)))
        self.ui.actionNewUTM.setEnabled(self.active is not None)

        waypointIconPath = ":/images/icons/k{}/waypoint.png".format(version)
        self.ui.actionNewUTW.setIcon(QIcon(QPixmap(waypointIconPath)))
        self.ui.actionNewUTW.setEnabled(self.active is not None)

        encounterIconPath = ":/images/icons/k{}/encounter.png".format(version)
        self.ui.actionNewUTE.setIcon(QIcon(QPixmap(encounterIconPath)))
        self.ui.actionNewUTE.setEnabled(self.active is not None)

        self.ui.actionEditTLK.setEnabled(self.active is not None)
        self.ui.actionEditJRL.setEnabled(self.active is not None)

        self.ui.actionCloneModule.setEnabled(self.active is not None)

    def reloadSettings(self) -> None:
        self.config.reload()
        self.ui.mdlDecompileCheckbox.setVisible(self.config.mdlAllowDecompile)
        self.reloadInstallations()

    def openSettingsDialog(self) -> None:
        """
        Opens the Settings dialog and refresh installation combo list if changes.
        """
        if Settings().exec_():
            self.reloadSettings()

    def openAboutDialog(self) -> None:
        """
        Opens the about dialog.
        """
        About(self, PROGRAM_VERSION).exec_()

    def checkForUpdates(self, silent: bool = False) -> None:
        """
        Scans for any updates and opens a dialog with a message based on the scan result.

        Args:
            silent: If true, only shows popup if an update is available.
        """
        try:
            req = requests.get("https://pastebin.com/raw/tUJCGgrX")
            data = json.loads(req.text)

            latestVersion = data['latestVersion']
            downloadLink = data['downloadLink']

            if StrictVersion(latestVersion) > StrictVersion(PROGRAM_VERSION):
                QMessageBox(QMessageBox.Information, "New version is available.",
                            "New version available for <a href='{}'>download</a>.".format(downloadLink),
                            QMessageBox.Ok, self).exec_()
            else:
                if not silent:
                    QMessageBox(QMessageBox.Information, "Version is up to date",
                                "You are running the latest version (" + latestVersion + ").", QMessageBox.Ok, self).exec_()
        except Exception:
            if not silent:
                QMessageBox(QMessageBox.Information, "Unable to fetch latest version.",
                            "Check if you are connected to the internet.", QMessageBox.Ok, self).exec_()

    def openActiveTalktable(self) -> None:
        """
        Opens the talktable for the active (currently selected) installation. If there is no active information, show
        a message box instead.
        """
        filepath = self.active.path() + "dialog.tlk"
        data = BinaryReader.load_file(filepath)
        self.openResourceEditor(filepath, "dialog", ResourceType.TLK, data)

    def openActiveJournal(self) -> None:
        res = self.active.resource("global", ResourceType.JRL, [SearchLocation.OVERRIDE, SearchLocation.CHITIN])
        self.openResourceEditor(res.filepath, "global", ResourceType.JRL, res.data)

    def resizeColumns(self) -> None:
        self.ui.coreTree.setColumnWidth(1, 10)
        self.ui.coreTree.setColumnWidth(0, self.ui.coreTree.width() - 80)
        self.ui.coreTree.header().setSectionResizeMode(QHeaderView.Fixed)
        self.ui.modulesTree.setColumnWidth(1, 10)
        self.ui.modulesTree.setColumnWidth(0, self.ui.modulesTree.width() - 80)
        self.ui.modulesTree.header().setSectionResizeMode(QHeaderView.Fixed)
        self.ui.overrideTree.setColumnWidth(1, 10)
        self.ui.overrideTree.setColumnWidth(0, self.ui.overrideTree.width() - 80)
        self.ui.overrideTree.header().setSectionResizeMode(QHeaderView.Fixed)

    def resizeEvent(self, size: QtGui.QResizeEvent) -> None:
        super().resizeEvent(size)
        self.resizeColumns()

    def _clearModels(self) -> None:
        """
        Clears all data models for the different tabs.
        """

        self.ui.modulesCombo.setModel(QStandardItemModel())
        self.ui.overrideFolderCombo.clear()
        self.ui.overrideFolderCombo.addItem("[Root]")

        self.modulesModel.clear()
        self.overrideModel.clear()

        self.resizeColumns()

    def reloadInstallations(self) -> None:
        """
        Refresh the list of installations available in the combobox.
        """
        self.ui.gameCombo.clear()
        self.ui.gameCombo.addItem("[None]")

        for installation in self.config.installations:
            self.ui.gameCombo.addItem(installation.name)

    def changeActiveInstallation(self, index: int) -> None:
        """
        Changes the active installation selected. If an installation does not have a path yet set, the user is prompted
        to select a directory for it. If the installation path remains unset then the active installation also remains
        unselected.

        Args:
            index: Index of the installation in the installationCombo combobox.
        """
        self.ui.gameCombo.setCurrentIndex(index)

        self._clearModels()
        self.ui.resourceTabs.setEnabled(False)
        self.ui.sidebar.setEnabled(False)
        self.active = None
        self.updateMenus()

        if index <= 0:
            return

        self.ui.resourceTabs.setEnabled(True)
        self.ui.sidebar.setEnabled(True)

        name = self.ui.gameCombo.itemText(index)
        path = self.config.installation(name).path
        tsl = self.config.installation(name).tsl

        # If the user has not set a path for the particular game yet, ask them too.
        if path == "":
            path = QFileDialog.getExistingDirectory(self, "Select the game directory for {}".format(name))

        # If the user still has not set a path, then return them to the [None] option.
        if path == "":
            self.ui.gameCombo.setCurrentIndex(0)
        else:
            # If the installation had not already been loaded previously this session, load it now
            if name not in self.installations:
                task = lambda: HTInstallation(path, name, tsl, self)
                loader = AsyncLoader(self, "Loading Installation", task, "Failed to load installation")

                if loader.exec_():
                    self.config.installation(name).path = path
                    self.config.save()

                    self.installations[name] = loader.value

            # If the data has been successfully been loaded, dump the data into the models
            if name in self.installations:
                self.active = self.installations[name]

                if name not in self._core_models:
                    self._core_models[name] = ResourceModel()
                    [self._core_models[name].addResource(resource) for resource in self.active.chitin_resources()]
                self.ui.coreTree.setModel(self._core_models[name].proxyModel())
                self._core_models[name].proxyModel().setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
                self._core_models[name].proxyModel().setFilterFixedString(self.ui.coreSearchEdit.text())

                if name not in self._modules_list:
                    self.refreshModuleList(False)
                else:
                    self.ui.modulesCombo.setModel(self._modules_list[name])

                self.refreshOverrideList()
                self.ui.overrideFolderFrame.setVisible(self.active.tsl)
                self.ui.overrideLine.setVisible(self.active.tsl)

                self.refreshTexturePackList()

                self.updateMenus()
            else:
                self.ui.gameCombo.setCurrentIndex(0)

    def changeModule(self, module: str) -> None:
        """
        Updates the items in the module tree to the module specified.
        """

        self.modulesModel.clear()
        self.ui.moduleReloadButton.setEnabled(True)

        if self.active is None or module is None or module == "" or module == "[None]":
            self.ui.moduleReloadButton.setEnabled(False)
            return

        for resource in self.active.module_resources(module):
            self.modulesModel.addResource(resource)

        self.resizeColumns()

    def reloadModule(self) -> None:
        """
        Reloads the files stored in the currently selected module and updates the data model.
        """
        module = self.ui.modulesCombo.currentData()
        self.active.reload_module(module)

        self.modulesModel.clear()
        for resource in self.active.module_resources(module):
            self.modulesModel.addResource(resource)

        self.resizeColumns()

    def refreshModuleList(self, reload: bool = True) -> None:
        """
        Refreshes the list of modules in the modulesCombo combobox.
        """
        if self.active is None:
            return

        if reload:
            self.active.load_modules()

        self._modules_list[self.active.name] = QStandardItemModel(self)
        self._modules_list[self.active.name].appendRow(QStandardItem("[None]"))

        if self.config.showModuleNames:
            areaNames = self.active.module_names()
            for module in self.active.modules_list():
                item = QStandardItem("[{}] {}".format(areaNames[module], module))
                item.setData(module, QtCore.Qt.UserRole)
                self._modules_list[self.active.name].appendRow(item)
        else:
            for module in self.active.modules_list():
                item = QStandardItem(module)
                item.setData(module, QtCore.Qt.UserRole)
                self._modules_list[self.active.name].appendRow()

        self.ui.modulesCombo.setModel(self._modules_list[self.active.name])

    def changeOverrideFolder(self, folder: str) -> None:
        self.overrideModel.clear()

        if self.active is None:
            return

        folder = "" if folder == "[Root]" else folder

        for resource in self.active.override_resources(folder):
            self.overrideModel.addResource(resource)

        self.resizeColumns()

    def refreshOverrideList(self) -> None:
        """
        Refreshes the list of override directories in the overrideFolderCombo combobox.
        """
        self.active.load_override()

        self.ui.overrideFolderCombo.clear()
        self.ui.overrideFolderCombo.addItem("[Root]")
        for directory in self.active.override_list():
            if directory == "":
                continue
            self.ui.overrideFolderCombo.addItem(directory)

    def reloadOverride(self) -> None:
        """
        Reloads the files stored in the active installation's override folder and updates the respective data model.
        """
        folder = self.ui.overrideFolderCombo.currentText()
        folder = "" if folder == "[Root]" else folder

        self.active.reload_override(folder)

        self.overrideModel.clear()
        for resource in self.active.override_resources(folder):
            self.overrideModel.addResource(resource)

        self.resizeColumns()

    def currentDataView(self) -> QAbstractItemView:
        """
        Returns the QTreeView object that is currently being shown on the resourceTabs.
        """
        if self.ui.resourceTabs.currentIndex() == 0:
            return self.ui.coreTree
        if self.ui.resourceTabs.currentIndex() == 1:
            return self.ui.modulesTree
        if self.ui.resourceTabs.currentIndex() == 2:
            return self.ui.overrideTree
        if self.ui.resourceTabs.currentIndex() == 3:
            return self.ui.texturesList

    def currentDataModel(self) -> ResourceModel:
        """
        Returns the QTreeView object that is currently being shown on the resourceTabs.
        """
        if self.ui.resourceTabs.currentIndex() == 0:
            return self.ui.coreTree.model().parent()
        if self.ui.resourceTabs.currentIndex() == 1:
            return self.modulesModel
        if self.ui.resourceTabs.currentIndex() == 2:
            return self.overrideModel
        if self.ui.resourceTabs.currentIndex() == 3:
            return self.texturesModel

    def filterDataModel(self, text: str) -> None:
        """
        Filters the data model that is currently shown on the resourceTabs.

        Args:
            text: The text to filter through.
        """
        self.currentDataView().model().setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.currentDataView().model().setFilterFixedString(text)

    def extractFromSelected(self) -> None:
        """
        Extracts the resources from the items selected in the tree of the currently open resourceTabs tab.
        """

        resources = self.currentDataModel().resourceFromIndexes(self.currentDataView().selectedIndexes())

        if len(resources) == 1:
            # Player saves resource with a specific name
            default = resources[0].resname() + "." + resources[0].restype().extension
            filepath = QFileDialog.getSaveFileName(self, "Save resource", default)[0]

            if filepath:
                tasks = [lambda: self._extractResource(resources[0], filepath)]
                loader = AsyncBatchLoader(self, "Extracting Resources", tasks, "Failed to Extract Resources")
                loader.exec_()

        elif len(resources) >= 1:
            # Player saves resources with original name to a specific directory
            folderpath = QFileDialog.getExistingDirectory(self, "Select directory to extract to")
            if folderpath:
                tasks = []
                for resource in resources:
                    filename = resource.resname() + "." + resource.restype().extension
                    filepath = folderpath + "/" + filename
                    tasks.append(lambda a=resource, b=filepath: self._extractResource(a, b))

                loader = AsyncBatchLoader(self, "Extracting Resources", tasks, "Failed to Extract Resources")
                loader.exec_()

    def _extractResource(self, resource: FileResource, filepath: str) -> None:
        try:
            data = resource.data()
            folderpath = os.path.dirname(filepath) + "/"
            filename = os.path.basename(filepath)

            decompileTPC = self.ui.tpcDecompileCheckbox.isChecked()
            extractTXI = self.ui.tpcTxiCheckbox.isChecked()
            decompileMDL = self.ui.mdlDecompileCheckbox.isChecked()
            extractTexturesMDL = self.ui.mdlTexturesCheckbox.isChecked()

            manipulateTPC = decompileTPC or extractTXI
            manipulateMDL = decompileMDL or extractTexturesMDL

            if resource.restype() == ResourceType.MDX and decompileMDL:
                # Ignore extracting MDX files if decompiling MDLs
                return

            if resource.restype() == ResourceType.TPC and manipulateTPC:
                tpc = load_tpc(data)

                if extractTXI:
                    txi_filename = filename.replace(".tpc", ".txi")
                    with open(folderpath + txi_filename, 'wb') as file:
                        file.write(tpc.txi.encode('ascii'))

                if decompileTPC:
                    data = bytearray()
                    write_tpc(tpc, data, ResourceType.TGA)
                    filepath = filepath.replace(".tpc", ".tga")

            if resource.restype() == ResourceType.MDL and manipulateMDL:
                mdxData = self.active.resource(resource.resname(), ResourceType.MDX).data
                mdl = load_mdl(data, 0, 0, mdxData, 0, 0)

                if decompileMDL:
                    data = bytearray()
                    write_mdl(mdl, data, ResourceType.MDL_ASCII)
                    filepath = filepath.replace(".mdl", ".ascii.mdl")

                if extractTexturesMDL:
                    for texture in mdl.all_textures():
                        try:
                            tpc = self.active.texture(texture)
                            if extractTXI:
                                with open(folderpath + texture + ".txi", 'wb') as file:
                                    file.write(tpc.txi.encode('ascii'))
                            file_format = ResourceType.TGA if decompileTPC else ResourceType.TPC
                            extension = "tga" if file_format == ResourceType.TGA else "tpc"
                            write_tpc(tpc, "{}{}.{}".format(folderpath, texture, extension), file_format)
                        except Exception as e:
                            self.error.emit("Could not find or extract tpc: " + texture)

            with open(filepath, 'wb') as file:
                file.write(data)
        except Exception as e:
            traceback.print_exc()
            raise Exception("Failed to extract resource: " + resource.resname() + "." + resource.restype().extension)

    def openFromSelected(self) -> None:
        """
        Opens the resources from the items selected in the tree of the currently open resourceTabs tab.
        """
        resources = self.currentDataModel().resourceFromIndexes(self.currentDataView().selectedIndexes())
        for resource in resources:
            filepath, editor = self.openResourceEditor(resource.filepath(), resource.resname(), resource.restype(), resource.data())
            inERForRIM = resource.filepath().endswith('.erf') or resource.filepath().endswith('.rim') or resource.filepath().endswith('.mod')

            # If opened with external editor AND the resource in encapsulated in ERF/RIM
            if isinstance(editor, subprocess.Popen) and resource.filepath() != editor and inERForRIM:
                handler = EncapsulatedExternalUpdateHandler(self, filepath, editor, resource.filepath(), resource.resname(), resource.restype())
                handler.errorOccurred.connect(self.externalEncapsulatedSavedError)
                handler.fileModified.connect(self.reloadModule)
                handler.start()
            elif self.active.module_path() in filepath and isinstance(editor, Editor):
                editor.savedFile.connect(self.reloadModule)

    def openFromFile(self) -> None:
        filepath, filter = QFileDialog.getOpenFileName(self, "Open a file")

        if filepath != "":
            resref, restype_ext = os.path.basename(filepath).split('.', 1)
            restype = ResourceType.from_extension(restype_ext)
            with open(filepath, 'rb') as file:
                data = file.read()
            self.openResourceEditor(filepath, resref, restype, data)

    def openResourceEditor(self, filepath: str, resref: str, restype: ResourceType, data: bytes, *,
                           noExternal=False) -> Union[Tuple[str, Editor], Tuple[str, subprocess.Popen], Tuple[None, None]]:
        """
        Opens an editor for the specified resource. If the user settings have the editor set to inbuilt it will return
        the editor, otherwise it returns None

        Args:
            filepath: Path to the resource.
            resref: The ResRef.
            restype: The resource type.
            data: The resource data.
            noExternal: If True, internal editors will only be used, regardless of user settings.

        Returns:
            Either the Editor object if using an internal editor, the filepath if using a external editor or None if
            no editor was successfully opened.
        """
        editor = None
        external = None

        encapsulated = filepath.endswith('.erf') or filepath.endswith('.rim') or filepath.endswith('.mod') or filepath.endswith('.bif') or filepath.endswith('.key')
        inERForRIM = filepath.endswith('.erf') or filepath.endswith('.rim') or filepath.endswith('.mod')
        shouldUseExternal = (self.config.erfExternalEditors and inERForRIM) or not inERForRIM
        noExternal = noExternal or not shouldUseExternal

        def useGFFEditor():
            editor = external = None
            if self.config.gffEditorPath and not noExternal:
                external = self.config.gffEditorPath
            else:
                editor = GFFEditor(self, self.active)
            return editor, external

        if restype in [ResourceType.TwoDA]:
            if self.config.twodaEditorPath and not noExternal:
                external = self.config.twodaEditorPath
            else:
                editor = TwoDAEditor(self, self.active)

        if restype in [ResourceType.SSF]:
            editor = SSFEditor(self, self.active)

        if restype in [ResourceType.TLK]:
            if self.config.tlkEditorPath and not noExternal:
                external = self.config.tlkEditorPath
            else:
                editor = TLKEditor(self, self.active)

        if restype in [ResourceType.WOK, ResourceType.DWK, ResourceType.PWK]:
            editor = BWMEditor(self, self.active)

        if restype in [ResourceType.TPC, ResourceType.TGA, ResourceType.JPG, ResourceType.BMP, ResourceType.PNG]:
            editor = TPCEditor(self, self.active)

        if restype in [ResourceType.TXT, ResourceType.TXI, ResourceType.LYT, ResourceType.VIS]:
            if self.config.txtEditorPath and not noExternal:
                external = self.config.txtEditorPath
            else:
                editor = TXTEditor(self)

        if restype in [ResourceType.NSS]:
            if self.active:
                editor = NSSEditor(self, self.active)
            else:
                editor = TXTEditor(self, self.active)

        if restype in [ResourceType.NCS]:
            if self.active:
                editor = NSSEditor(self, self.active)

        if restype in [ResourceType.DLG]:
            if self.config.dlgEditorPath and not noExternal:
                external = self.config.dlgEditorPath
            else:
                editor = DLGEditor(self, self.active)

        if restype in [ResourceType.UTC]:
            if self.active is None or not self.config.gffSpecializedEditors:
                editor, external = useGFFEditor()
            else:
                editor = UTCEditor(self, self.active)

        if restype in [ResourceType.UTP]:
            if self.active is None or not self.config.gffSpecializedEditors:
                editor, external = useGFFEditor()
            else:
                editor = UTPEditor(self, self.active)

        if restype in [ResourceType.UTD]:
            if self.active is None or not self.config.gffSpecializedEditors:
                editor, external = useGFFEditor()
            else:
                editor = UTDEditor(self, self.active)

        if restype in [ResourceType.UTS]:
            if self.active is None or not self.config.gffSpecializedEditors:
                editor, external = useGFFEditor()
            else:
                editor = UTSEditor(self, self.active)

        if restype in [ResourceType.UTT]:
            if self.active is None or not self.config.gffSpecializedEditors:
                editor, external = useGFFEditor()
            else:
                editor = UTTEditor(self, self.active)

        if restype in [ResourceType.UTM]:
            if self.active is None or not self.config.gffSpecializedEditors:
                editor, external = useGFFEditor()
            else:
                editor = UTMEditor(self, self.active)

        if restype in [ResourceType.UTW]:
            if self.active is None or not self.config.gffSpecializedEditors:
                editor, external = useGFFEditor()
            else:
                editor = UTWEditor(self, self.active)

        if restype in [ResourceType.UTE]:
            if self.active is None or not self.config.gffSpecializedEditors:
                editor, external = useGFFEditor()
            else:
                editor = UTEEditor(self, self.active)

        if restype in [ResourceType.UTI]:
            if self.active is None or not self.config.gffSpecializedEditors:
                editor, external = useGFFEditor()
            else:
                editor = UTIEditor(self, self.active)

        if restype in [ResourceType.JRL]:
            if self.active is None or not self.config.gffSpecializedEditors:
                editor, external = useGFFEditor()
            else:
                editor = JRLEditor(self, self.active)

        if restype in [ResourceType.GFF, ResourceType.ITP,
                       ResourceType.GUI, ResourceType.ARE, ResourceType.IFO, ResourceType.GIT]:
            editor, external = useGFFEditor()

        if restype in [ResourceType.WAV, ResourceType.MP3]:
            editor = AudioPlayer(self)

        if restype in [ResourceType.MOD, ResourceType.ERF, ResourceType.RIM]:
            editor = ERFEditor(self, self.active)

        if editor is not None:
            editor.load(filepath, resref, restype, data)
            editor.show()
            return filepath, editor
        elif external is not None:
            try:
                if encapsulated:
                    modName = os.path.basename(filepath.replace(".rim", "").replace(".erf", "").replace(".mod", ""))
                    tempFilepath = "{}/{}-{}.{}".format(self.config.extractPath, modName, resref, restype.extension)
                    with open(tempFilepath, 'wb') as file:
                        file.write(data)
                    process = subprocess.Popen([external, tempFilepath])
                    return tempFilepath, process
                else:
                    process = subprocess.Popen([external, filepath])
                    return filepath, process
            except Exception as e:
                QMessageBox(QMessageBox.Critical, "Could not open editor", "Double check the file path in settings.",
                            QMessageBox.Ok, self).show()
        else:
            QMessageBox(QMessageBox.Critical, "Failed to open file", "The selected file is not yet supported.",
                        QMessageBox.Ok, self).show()
        return None, None

    def externalEncapsulatedSavedError(self, tempFilepath: str, modFilepath: str, error: Exception) -> None:
        """
        Opens a messagebox for when an error occurred trying to save a resource through an external editor into an
        encapsulated file.

        Attributes:
            error: The error that occurred.
        """
        QMessageBox(QMessageBox.Critical, "Could not saved resource to ERF/MOD/RIM",
                    "Tried to save a resource '{}' into ".format(tempFilepath) +
                    "'{}' using an external editor.".format(modFilepath), QMessageBox.Ok, self).exec_()

    def dropEvent(self, e: QtGui.QDropEvent) -> None:
        if e.mimeData().hasUrls():
            for url in e.mimeData().urls():
                filepath = url.toLocalFile()
                with open(filepath, 'rb') as file:
                    resref, restype = ResourceIdentifier.from_path(filepath)
                    data = file.read()
                    self.openResourceEditor(filepath, resref, restype, data)

    def dragEnterEvent(self, e: QtGui.QDragEnterEvent) -> None:
        if e.mimeData().hasUrls():
            for url in e.mimeData().urls():
                with suppress(Exception):
                    # Call from_path method as it will throw an error if the file extension is not recognized.
                    ResourceIdentifier.from_path(url.toLocalFile())
                    e.accept()


class ResourceModel(QStandardItemModel):
    """
    A data model used by the different trees (Core, Modules, Override). This class provides an easy way to add resources
    while sorting the into categories.
    """

    def __init__(self):
        super().__init__()
        self._categoryItems = {}
        self._proxyModel = QSortFilterProxyModel(self)
        self._proxyModel.setSourceModel(self)
        self._proxyModel.setRecursiveFilteringEnabled(True)
        self.setColumnCount(2)
        self.setHorizontalHeaderLabels(["ResRef", "Type"])

    def proxyModel(self) -> QSortFilterProxyModel:
        return self._proxyModel

    def clear(self) -> None:
        super().clear()
        self._categoryItems = {}
        self.setColumnCount(2)
        self.setHorizontalHeaderLabels(["ResRef", "Type"])

    def _getCategoryItem(self, resourceType: ResourceType) -> QStandardItem:
        if resourceType.category not in self._categoryItems:
            categoryItem = QStandardItem(resourceType.category)
            categoryItem.setSelectable(False)
            unusedItem = QStandardItem("")
            unusedItem.setSelectable(False)
            self._categoryItems[resourceType.category] = categoryItem
            self.appendRow([categoryItem, unusedItem])
        return self._categoryItems[resourceType.category]

    def addResource(self, resource: FileResource) -> None:
        item1 = QStandardItem(resource.resname())
        item1.resource = resource
        item2 = QStandardItem(resource.restype().extension.upper())
        self._getCategoryItem(resource.restype()).appendRow([item1, item2])

    def resourceFromIndexes(self, indexes: List[QModelIndex], proxy: bool = True) -> List[FileResource]:
        items = []
        for index in indexes:
            sourceIndex = self._proxyModel.mapToSource(index) if proxy else index
            items.append(self.itemFromIndex(sourceIndex))
        return self.resourceFromItems(items)

    def resourceFromItems(self, items: List[QStandardItem]) -> List[FileResource]:
        return [item.resource for item in items if hasattr(item, 'resource')]


class EncapsulatedExternalUpdateHandler(FileSystemEventHandler, QThread):
    errorOccurred = QtCore.pyqtSignal(object, object, object)
    fileModified = QtCore.pyqtSignal(object)

    def __init__(self, parent, tempFilepath: str, process: subprocess.Popen, modFilepath: str, resref: str, restype: ResourceType):
        super().__init__(parent)
        self._tempFilename = os.path.basename(tempFilepath)
        self._tempFilepath: str = tempFilepath
        self._modFilepath: str = modFilepath
        self._resref: str = resref
        self._restype: ResourceType = restype
        self._observer: Observer = Observer()
        self._closeListener = ProcessCloseListener(process)
        self._closeListener.closed.connect(self.stop)
        self._first: bool = True

    def observer(self) -> Observer:
        return self._observer

    def run(self) -> None:
        sleep(2)
        self._closeListener.start()
        self._observer.schedule(self, os.path.dirname(self._tempFilepath), recursive=False)
        self._observer.start()
        self._observer.join()

    def on_modified(self, event: FileModifiedEvent):
        if not event.is_directory and event.src_path.endswith(self._tempFilename):
            if self._first:
                self._first = False
                return

            try:
                with open(self._tempFilepath, 'rb') as file:
                    data = file.read()
                    if self._modFilepath.endswith(".erf") or self._modFilepath.endswith(".mod"):
                        erf = load_erf(self._modFilepath)
                        erf.erf_type = ERFType.ERF if self._modFilepath.endswith(".erf") else ERFType.MOD
                        if erf.get(self._resref, self._restype) != data:
                            erf.set(self._resref, self._restype, data)
                            write_erf(erf, self._modFilepath)
                    elif self._modFilepath.endswith(".rim"):
                        rim = load_rim(self._modFilepath)
                        if rim.get(self._resref, self._restype) != data:
                            rim.set(self._resref, self._restype, data)
                            write_rim(rim, self._modFilepath)
                    self.fileModified.emit(self._modFilepath)
            except Exception as e:
                self.errorOccurred.emit(self._tempFilepath, self._modFilepath, e)

    def stop(self) -> None:
        self._observer.stop()


class ProcessCloseListener(QThread):
    closed = QtCore.pyqtSignal()

    def __init__(self, process: subprocess.Popen):
        super().__init__()
        self._process = process

    def run(self):
        self._process.wait()
        self.closed.emit()


class TexturesView(QListView):
    iconUpdate = QtCore.pyqtSignal(object, object)

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.verticalScrollBar().valueChanged.connect(self.loadVisibleTextures)
        self._installation: Optional[HTInstallation] = None

        self._taskQueue = multiprocessing.JoinableQueue()
        self._resultQueue = multiprocessing.Queue()
        self._consumers: List[TextureListConsumer] = [TextureListConsumer(self._taskQueue, self._resultQueue) for i in range(multiprocessing.cpu_count())]
        [consumer.start() for consumer in self._consumers]
        self.iconUpdate.connect(self.onIconUpdate)

        self._scanner = QThread(self)
        self._scanner.run = self.scan
        self._scanner.start()

    def onIconUpdate(self, item, icon):
        item.setIcon(icon)

    def scan(self) -> None:
        while True:
            for row, resname, width, height, data in iter(self._resultQueue.get, None):
                image = QImage(data, width, height, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(image).transformed(QTransform().scale(1, -1))
                proxyModel: QSortFilterProxyModel = self.model()
                sourceModel: QStandardItemModel = proxyModel.sourceModel()
                item = sourceModel.item(row, 0)
                if item is not None:
                    self.iconUpdate.emit(item, QIcon(pixmap))

            sleep(0.1)

    def resizeEvent(self, e: QResizeEvent) -> None:
        super(TexturesView, self).resizeEvent(e)
        self.loadVisibleTextures()

    def stop(self):
        self._scanner.terminate()
        [consumer.terminate() for consumer in self._consumers]

    def setInstallation(self, installation: HTInstallation):
        self._installation = installation

        self.loadVisibleTextures()

    def loadVisibleTextures(self) -> None:
        for item in self.getVisibleItems():
            if item is None or item.data(QtCore.Qt.UserRole):
                continue

            tpc = self._installation.texture(item.text(), [SearchLocation.TEXTURES_GUI, SearchLocation.TEXTURES_TPA])
            tpc = TPC() if tpc is None else tpc

            task = TextureListTask(item.row(), tpc, item.text())
            self._taskQueue.put(task)
            item.setData(True, QtCore.Qt.UserRole)

    def getVisibleItems(self):
        if self.model().rowCount() == 0:
            return []

        scanWidth = self.parent().parent().width() if self.viewport().width() < 100 else self.viewport().width()
        scanHeight = self.parent().parent().height() if self.viewport().height() < 100 else self.viewport().height()

        proxyModel: QSortFilterProxyModel = self.model()
        model: QStandardItemModel = self.model().sourceModel()

        firstItem = None
        firstIndex = None

        for y in range(2, 92, 2):
            for x in range(2, 92, 2):
                proxyIndex = self.indexAt(QPoint(x, y))
                index = proxyModel.mapToSource(proxyIndex)
                item = model.itemFromIndex(index)
                if not firstItem and item:
                    firstItem = item
                    firstIndex = proxyIndex
                    break

        items = []

        if firstItem:
            startRow = firstItem.row()
            widthCount = scanWidth // 92
            heightCount = scanHeight // 92 + 2
            numVisible = min(proxyModel.rowCount(), widthCount * heightCount)

            for i in range(numVisible):
                proxyIndex = proxyModel.index(firstIndex.row() + i, 0)
                sourceIndex = proxyModel.mapToSource(proxyIndex)
                item = model.itemFromIndex(sourceIndex)
                items.append(item)

        return items


class TextureListModel(QStandardItemModel):
    def __init__(self):
        super().__init__()
        self._proxyModel = QSortFilterProxyModel(self)
        self._proxyModel.setSourceModel(self)
        self._proxyModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)

    def proxyModel(self) -> QSortFilterProxyModel:
        return self._proxyModel

    def resourceFromIndexes(self, indexes: List[QModelIndex], proxy: bool = True) -> List[FileResource]:
        items = []
        for index in indexes:
            sourceIndex = self._proxyModel.mapToSource(index) if proxy else index
            items.append(self.itemFromIndex(sourceIndex))
        return self.resourceFromItems(items)

    def resourceFromItems(self, items: List[QStandardItem]) -> List[FileResource]:
        return [item.resource for item in items if hasattr(item, 'resource')]


class TextureListConsumer(multiprocessing.Process):
    def __init__(self, taskQueue, resultQueue):
        multiprocessing.Process.__init__(self)
        self.taskQueue: multiprocessing.JoinableQueue = taskQueue
        self.resultQueue: multiprocessing.Queue = resultQueue

    def run(self):
        proc_name = self.name
        while True:
            next_task = self.taskQueue.get()

            answer = next_task()
            self.taskQueue.task_done()
            self.resultQueue.put(answer)


class TextureListTask:
    def __init__(self, row, tpc, resname):
        self.row = row
        self.tpc = tpc
        self.resname = resname

    def __repr__(self):
        return str(self.row)

    def __call__(self, *args, **kwargs):
        width, height, data = self.tpc.convert(TPCTextureFormat.RGB, self.bestMipmap(self.tpc))
        return self.row, self.resname, width, height, data

    def bestMipmap(self, tpc: TPC) -> int:
        for i in range(tpc.mipmap_count()):
            size = tpc.get(i).width
            if size <= 64:
                return i
        return 0
