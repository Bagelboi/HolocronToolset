import math
import os
from abc import ABC, abstractmethod
from typing import Optional, Set

from PyQt5 import QtCore
from PyQt5.QtCore import QPoint, QTimer
from PyQt5.QtGui import QPixmap, QIcon, QWheelEvent, QMouseEvent, QKeyEvent, QResizeEvent
from PyQt5.QtWidgets import QMainWindow, QWidget, QOpenGLWidget, QTreeWidgetItem, QMenu, QAction, QListWidgetItem, \
    QMessageBox, QDialog, QDialogButtonBox, QCheckBox
from pykotor.common.geometry import Vector3, Vector2
from pykotor.common.misc import ResRef
from pykotor.common.module import Module, ModuleResource
from pykotor.common.stream import BinaryWriter
from pykotor.extract.file import ResourceIdentifier
from pykotor.resource.formats.bwm import BWMFace
from pykotor.resource.formats.erf import read_erf, write_erf
from pykotor.resource.formats.rim import read_rim, write_rim
from pykotor.resource.generics.git import GITCreature, GITPlaceable, GITDoor, GITTrigger, GITEncounter, GITWaypoint, \
    GITSound, GITStore, GITCamera, GITInstance
from pykotor.resource.generics.utc import bytes_utc, UTC
from pykotor.resource.generics.utd import bytes_utd, UTD
from pykotor.resource.generics.ute import bytes_ute, UTE
from pykotor.resource.generics.utm import UTM, bytes_utm
from pykotor.resource.generics.utp import bytes_utp, UTP
from pykotor.resource.generics.uts import bytes_uts, UTS
from pykotor.resource.generics.utt import bytes_utt, UTT
from pykotor.resource.generics.utw import bytes_utw, UTW
from pykotor.resource.type import ResourceType

from data.installation import HTInstallation
from pykotor.gl.scene import Scene, RenderObject

from tools.module.me_controls import ModuleEditorControls, DynamicModuleEditorControls, HolocronModuleEditorControls


class ModuleEditor(QMainWindow):
    def __init__(self, parent: QWidget, installation: HTInstallation, module: Module):
        super().__init__(parent)

        self._installation: HTInstallation = installation
        self._module: Module = module

        from tools.module import moduleeditor_ui
        self.ui = moduleeditor_ui.Ui_MainWindow()
        self.ui.setupUi(self)
        self._setupSignals()

        self.ui.mainRenderer.init(installation, module)

        self.hideCreatures: bool = False
        self.hidePlaceables: bool = False
        self.hideDoors: bool = False
        self.hideTriggers: bool = False
        self.hideEncounters: bool = False
        self.hideWaypoints: bool = False
        self.hideSounds: bool = False
        self.hideStores: bool = False
        self.hideCameras: bool = False

        self.cameraControls: ModuleEditorControls = HolocronModuleEditorControls(self.ui.mainRenderer)
        if os.path.exists("./controls/3d/aurora.json"):
            self.cameraControls = DynamicModuleEditorControls(self.ui.mainRenderer)
            self.cameraControls.load("./controls/3d/aurora.json")

        self.snapToWalkmesh: bool = True

        self._refreshWindowTitle()
        self.rebuildResourceTree()
        self.rebuildInstanceList()

    def _setupSignals(self) -> None:
        self.ui.actionSave.triggered.connect(self.saveGit)

        self.ui.resourceTree.customContextMenuRequested.connect(self.onResourceTreeContextMenu)

        self.ui.viewCreatureCheck.toggled.connect(self.updateInstanceVisibility)
        self.ui.viewPlaceableCheck.toggled.connect(self.updateInstanceVisibility)
        self.ui.viewDoorCheck.toggled.connect(self.updateInstanceVisibility)
        self.ui.viewSoundCheck.toggled.connect(self.updateInstanceVisibility)
        self.ui.viewTriggerCheck.toggled.connect(self.updateInstanceVisibility)
        self.ui.viewEncounterCheck.toggled.connect(self.updateInstanceVisibility)
        self.ui.viewWaypointCheck.toggled.connect(self.updateInstanceVisibility)
        self.ui.viewCameraCheck.toggled.connect(self.updateInstanceVisibility)
        self.ui.viewStoreCheck.toggled.connect(self.updateInstanceVisibility)

        self.ui.viewCreatureCheck.mouseDoubleClickEvent = lambda _: self.onInstanceVisiblityDoubleClick(self.ui.viewCreatureCheck)
        self.ui.viewPlaceableCheck.mouseDoubleClickEvent = lambda _: self.onInstanceVisiblityDoubleClick(self.ui.viewPlaceableCheck)
        self.ui.viewDoorCheck.mouseDoubleClickEvent = lambda _: self.onInstanceVisiblityDoubleClick(self.ui.viewDoorCheck)
        self.ui.viewSoundCheck.mouseDoubleClickEvent = lambda _: self.onInstanceVisiblityDoubleClick(self.ui.viewSoundCheck)
        self.ui.viewTriggerCheck.mouseDoubleClickEvent = lambda _: self.onInstanceVisiblityDoubleClick(self.ui.viewTriggerCheck)
        self.ui.viewEncounterCheck.mouseDoubleClickEvent = lambda _: self.onInstanceVisiblityDoubleClick(self.ui.viewEncounterCheck)
        self.ui.viewWaypointCheck.mouseDoubleClickEvent = lambda _: self.onInstanceVisiblityDoubleClick(self.ui.viewWaypointCheck)
        self.ui.viewCameraCheck.mouseDoubleClickEvent = lambda _: self.onInstanceVisiblityDoubleClick(self.ui.viewCameraCheck)
        self.ui.viewStoreCheck.mouseDoubleClickEvent = lambda _: self.onInstanceVisiblityDoubleClick(self.ui.viewStoreCheck)

        self.ui.instanceList.doubleClicked.connect(self.onInstanceListDoubleClicked)

        self.ui.mainRenderer.mousePressed.connect(self.onRendererMousePressed)
        self.ui.mainRenderer.mouseMoved.connect(self.onRendererMouseMoved)
        self.ui.mainRenderer.mouseScrolled.connect(self.onRendererMouseScrolled)
        self.ui.mainRenderer.objectSelected.connect(self.onRendererObjectSelected)
        self.ui.mainRenderer.customContextMenuRequested.connect(self.onRendererContextMenu)

    def _refreshWindowTitle(self) -> None:
        title = "{} - {} - Module Editor".format(self._module._id, self._installation.name)
        self.setWindowTitle(title)

    def saveGit(self) -> None:
        self._module.git().save()

    def rebuildResourceTree(self) -> None:
        self.ui.resourceTree.clear()
        categories = {
            ResourceType.UTC: QTreeWidgetItem(["Creatures"]),
            ResourceType.UTP: QTreeWidgetItem(["Placeables"]),
            ResourceType.UTD: QTreeWidgetItem(["Doors"]),
            ResourceType.UTI: QTreeWidgetItem(["Items"]),
            ResourceType.UTE: QTreeWidgetItem(["Encounters"]),
            ResourceType.UTT: QTreeWidgetItem(["Triggers"]),
            ResourceType.UTW: QTreeWidgetItem(["Waypoints"]),
            ResourceType.UTS: QTreeWidgetItem(["Sounds"]),
            ResourceType.UTM: QTreeWidgetItem(["Merchants"]),
            ResourceType.DLG: QTreeWidgetItem(["Dialogs"]),
            ResourceType.FAC: QTreeWidgetItem(["Factions"]),
            ResourceType.MDL: QTreeWidgetItem(["Models"]),
            ResourceType.TGA: QTreeWidgetItem(["Textures"]),
            ResourceType.NCS: QTreeWidgetItem(["Scripts"]),
            ResourceType.IFO: QTreeWidgetItem(["Module Data"]),
            ResourceType.INVALID: QTreeWidgetItem(["Other"])
        }
        categories[ResourceType.MDX] = categories[ResourceType.MDL]
        categories[ResourceType.WOK] = categories[ResourceType.MDL]
        categories[ResourceType.TPC] = categories[ResourceType.TGA]
        categories[ResourceType.IFO] = categories[ResourceType.IFO]
        categories[ResourceType.ARE] = categories[ResourceType.IFO]
        categories[ResourceType.GIT] = categories[ResourceType.IFO]
        categories[ResourceType.LYT] = categories[ResourceType.IFO]
        categories[ResourceType.VIS] = categories[ResourceType.IFO]
        categories[ResourceType.PTH] = categories[ResourceType.IFO]
        categories[ResourceType.NSS] = categories[ResourceType.NCS]

        for category in categories:
            self.ui.resourceTree.addTopLevelItem(categories[category])

        for resource in self._module.resources.values():
            item = QTreeWidgetItem([resource.resname() + "." + resource.restype().extension])
            item.setData(0, QtCore.Qt.UserRole, resource)
            category = categories[resource.restype()] if resource.restype() in categories else categories[ResourceType.INVALID]
            category.addChild(item)

        self.ui.resourceTree.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.ui.resourceTree.setSortingEnabled(True)

    def openModuleResource(self, resource: ModuleResource) -> None:
        editor = self.parent().openResourceEditor(resource.active(), resource.resname(), resource.restype(),
                                                  resource.data())[1]

        if editor is None:
            QMessageBox(QMessageBox.Critical,
                        "Failed to open editor",
                        "Failed to open editor for file: {}.{}".format(resource.resname(), resource.restype().extension))
        else:
            editor.savedFile.connect(lambda: self._onSavedResource(resource))

    def _onSavedResource(self, resource: ModuleResource) -> None:
        resource.reload()
        self.ui.mainRenderer.scene.clearCacheBuffer.append(ResourceIdentifier(resource.resname(), resource.restype()))

    def copyResourceToOverride(self, resource: ModuleResource) -> None:
        location = "{}/{}.{}".format(self._installation.override_path(), resource.resname(), resource.restype().extension)
        BinaryWriter.dump(location, resource.data())
        resource.add_locations([location])
        resource.activate(location)
        self.ui.mainRenderer.scene.clearCacheBuffer.append(ResourceIdentifier(resource.resname(), resource.restype()))

    def activateResourceFile(self, resource: ModuleResource, location: str) -> None:
        resource.activate(location)
        self.ui.mainRenderer.scene.clearCacheBuffer.append(ResourceIdentifier(resource.resname(), resource.restype()))

    def selectResouceItem(self, instance: GITInstance, clearExisting: bool = True) -> None:
        if clearExisting:
            self.ui.resourceTree.clearSelection()

        for i in range(self.ui.resourceTree.topLevelItemCount()):
            parent = self.ui.resourceTree.topLevelItem(i)
            for j in range(parent.childCount()):
                item = parent.child(j)
                res: ModuleResource = item.data(0, QtCore.Qt.UserRole)
                if res.resname() == instance.reference() and res.restype() == instance.extension():
                    parent.setExpanded(True)
                    item.setSelected(True)
                    self.ui.resourceTree.scrollToItem(item)

    def onResourceTreeContextMenu(self, point: QPoint) -> None:
        menu = QMenu(self)

        data = self.ui.resourceTree.currentItem().data(0, QtCore.Qt.UserRole)
        if isinstance(data, ModuleResource):
            copyToOverrideAction = QAction("Copy To Override", self)
            copyToOverrideAction.triggered.connect(lambda _, r=data: self.copyResourceToOverride(r))

            menu.addAction("Edit Active File").triggered.connect(lambda _, r=data: self.openModuleResource(r))
            menu.addAction("Reload Active File").triggered.connect(lambda _: data.reload())
            menu.addAction(copyToOverrideAction)
            menu.addSeparator()
            for location in data.locations():
                locationAciton = QAction(location, self)
                locationAciton.triggered.connect(lambda _, l=location: self.activateResourceFile(data, l))
                if location == data.active():
                    locationAciton.setEnabled(False)
                if "override" in location.lower():
                    copyToOverrideAction.setEnabled(False)
                menu.addAction(locationAciton)

        menu.exec_(self.ui.resourceTree.mapToGlobal(point))

    def rebuildInstanceList(self) -> None:
        visibleMapping = {
            GITCreature: self.hideCreatures,
            GITPlaceable: self.hidePlaceables,
            GITDoor: self.hideDoors,
            GITTrigger: self.hideTriggers,
            GITEncounter: self.hideEncounters,
            GITWaypoint: self.hideWaypoints,
            GITSound: self.hideSounds,
            GITStore: self.hideStores,
            GITCamera: self.hideCameras,
            GITInstance: False
        }

        iconMapping = {
            GITCreature: QPixmap(":/images/icons/k1/creature.png"),
            GITPlaceable: QPixmap(":/images/icons/k1/placeable.png"),
            GITDoor: QPixmap(":/images/icons/k1/door.png"),
            GITSound: QPixmap(":/images/icons/k1/sound.png"),
            GITTrigger: QPixmap(":/images/icons/k1/trigger.png"),
            GITEncounter: QPixmap(":/images/icons/k1/encounter.png"),
            GITWaypoint: QPixmap(":/images/icons/k1/waypoint.png"),
            GITCamera: QPixmap(":/images/icons/k1/camera.png"),
            GITStore: QPixmap(":/images/icons/k1/merchant.png"),
            GITInstance: QPixmap(32, 32)
        }

        self.ui.instanceList.clear()
        for instance in self._module.git().resource().instances():
            if visibleMapping[type(instance)]:
                continue

            if instance.reference():
                resource = self._module.resource(instance.reference().get(), instance.extension())
                text = resource.localized_name()
                if text is None or text.isspace():
                    text = "[{}]".format(resource.resname())
            else:
                text = "Camera #{}".format(self._module.git().resource().index(instance))

            icon = QIcon(iconMapping[type(instance)])
            item = QListWidgetItem(icon, text)
            item.setToolTip("" if instance.reference() is None else instance.reference().get())
            item.setData(QtCore.Qt.UserRole, instance)
            self.ui.instanceList.addItem(item)

    def selectInstanceItemOnList(self, instance: GITInstance) -> None:
        self.ui.instanceList.clearSelection()
        for i in range(self.ui.instanceList.count()):
            item = self.ui.instanceList.item(i)
            data: GITInstance = item.data(QtCore.Qt.UserRole)
            if data is instance:
                item.setSelected(True)
                self.ui.instanceList.scrollToItem(item)

    def onInstanceVisiblityDoubleClick(self, checkbox: QCheckBox) -> None:
        """
        This method should be called whenever one of the instance visibility checkboxes have been double clicked. The
        resulting affect should be that all checkboxes become unchecked except for the one that was pressed.
        """
        self.ui.viewCreatureCheck.setChecked(False)
        self.ui.viewPlaceableCheck.setChecked(False)
        self.ui.viewDoorCheck.setChecked(False)
        self.ui.viewSoundCheck.setChecked(False)
        self.ui.viewTriggerCheck.setChecked(False)
        self.ui.viewEncounterCheck.setChecked(False)
        self.ui.viewWaypointCheck.setChecked(False)
        self.ui.viewCameraCheck.setChecked(False)
        self.ui.viewStoreCheck.setChecked(False)

        checkbox.setChecked(True)

    def updateInstanceVisibility(self) -> None:
        self.hideCreatures = self.ui.mainRenderer.scene.hide_creatures = not self.ui.viewCreatureCheck.isChecked()
        self.hidePlaceables = self.ui.mainRenderer.scene.hide_placeables = not self.ui.viewPlaceableCheck.isChecked()
        self.hideDoors = self.ui.mainRenderer.scene.hide_doors = not self.ui.viewDoorCheck.isChecked()
        self.hideTriggers = self.ui.mainRenderer.scene.hide_triggers = not self.ui.viewTriggerCheck.isChecked()
        self.hideEncounters = self.ui.mainRenderer.scene.hide_encounters = not self.ui.viewEncounterCheck.isChecked()
        self.hideWaypoints = self.ui.mainRenderer.scene.hide_waypoints = not self.ui.viewWaypointCheck.isChecked()
        self.hideSounds = self.ui.mainRenderer.scene.hide_sounds = not self.ui.viewSoundCheck.isChecked()
        self.hideStores = self.ui.mainRenderer.scene.hide_stores = not self.ui.viewStoreCheck.isChecked()
        self.hideCameras = self.ui.mainRenderer.scene.hide_cameras = not self.ui.viewCameraCheck.isChecked()
        self.rebuildInstanceList()

    def onInstanceListDoubleClicked(self) -> None:
        if self.ui.instanceList.selectedItems():
            item = self.ui.instanceList.selectedItems()[0]
            instance: GITInstance = item.data(QtCore.Qt.UserRole)
            self.ui.mainRenderer.scene.select(instance)

            self.selectResouceItem(item.data(QtCore.Qt.UserRole))

            camera = self.ui.mainRenderer.scene.camera
            newCamPos = Vector3.from_vector3(instance.position)

            ax = -math.cos(camera.yaw)*math.sin(camera.pitch)*math.sin(0) - math.sin(camera.yaw)*math.cos(0)
            ay = -math.sin(camera.yaw)*math.sin(camera.pitch)*math.sin(0) + math.cos(camera.yaw)*math.cos(0)
            az = math.cos(camera.pitch)*math.sin(0)
            angleVec3 = Vector3(ax, ay, az).normal()

            newCamPos -= angleVec3*2
            camera.x, camera.y, camera.z = newCamPos.x, newCamPos.y, newCamPos.z+1

    def addInstance(self, instance: GITInstance) -> None:
        instance.position.z = self.ui.mainRenderer.walkmeshPoint(instance.position.x, instance.position.y,
                                                                 self.ui.mainRenderer.scene.camera.z).z

        if not isinstance(instance, GITCamera):
            dialog = InsertInstanceDialog(self, self._installation, self._module, instance.extension())

            if dialog.exec_():
                self.rebuildResourceTree()
                instance.resref = ResRef(dialog.resname)
                self._module.git().resource().add(instance)
        else:
            self._module.git().resource().add(instance)
        self.rebuildInstanceList()

    def removeSelectedInstances(self) -> None:
        for selected in self.ui.mainRenderer.scene.selection:
            if isinstance(selected.data, GITInstance):
                self._module.git().resource().remove(selected.data)
        self.ui.mainRenderer.scene.selection.clear()

    def onRendererMouseMoved(self, screen: Vector2, delta: Vector2, buttons: Set[int], keys: Set[int]) -> None:
        self.cameraControls.onMouseMoved(screen, delta, buttons, keys)

    def onRendererMouseScrolled(self, delta: Vector2, buttons: Set[int], keys: Set[int]) -> None:
        self.cameraControls.onMouseScrolled(delta, buttons, keys)

    def onRendererMousePressed(self, screen: Vector2, buttons: Set[int], keys: Set[int]) -> None:
        self.cameraControls.onMousePressed(screen, buttons, keys)

    def onRendererObjectSelected(self, obj: RenderObject) -> None:
        if obj is not None:
            data = obj.data
            self.selectInstanceItemOnList(data)
            self.selectResouceItem(data)

    def onRendererContextMenu(self, point: QPoint) -> None:
        menu = QMenu(self)
        world = self.ui.mainRenderer.walkmeshPoint(self.ui.mainRenderer.scene.camera.x, self.ui.mainRenderer.scene.camera.y)

        if len(self.ui.mainRenderer.scene.selection) == 0:
            menu.addAction("Insert Creature").triggered.connect(lambda: self.addInstance(GITCreature(world.x, world.y)))
            menu.addAction("Insert Door").triggered.connect(lambda: self.addInstance(GITDoor(world.x, world.y)))
            menu.addAction("Insert Placeable").triggered.connect(lambda: self.addInstance(GITPlaceable(world.x, world.y)))
            menu.addAction("Insert Store").triggered.connect(lambda: self.addInstance(GITStore(world.x, world.y)))
            menu.addAction("Insert Sound").triggered.connect(lambda: self.addInstance(GITSound(world.x, world.y)))
            menu.addAction("Insert Waypoint").triggered.connect(lambda: self.addInstance(GITWaypoint(world.x, world.y)))
            menu.addAction("Insert Camera").triggered.connect(lambda: self.addInstance(GITCamera(world.x, world.y)))
            menu.addAction("Insert Encounter").triggered.connect(lambda: self.addInstance(GITEncounter(world.x, world.y)))
            menu.addAction("Insert Trigger").triggered.connect(lambda: self.addInstance(GITTrigger(world.x, world.y)))
        else:
            menu.addAction("Remove").triggered.connect(self.removeSelectedInstances)

        menu.popup(self.ui.mainRenderer.mapToGlobal(point))
        menu.aboutToHide.connect(self.ui.mainRenderer.resetMouseButtons)

    def keyPressEvent(self, e: QKeyEvent) -> None:
        super().keyPressEvent(e)
        self.cameraControls.onKeyPressed(self.ui.mainRenderer.mouseDown(), self.ui.mainRenderer.keysDown())

    def keyReleaseEvent(self, e: QKeyEvent) -> None:
        super().keyPressEvent(e)
        self.cameraControls.onKeyReleased(self.ui.mainRenderer.mouseDown(), self.ui.mainRenderer.keysDown())


class InsertInstanceDialog(QDialog):
    def __init__(self, parent: QWidget, installation: HTInstallation, module: Module, restype: ResourceType):
        super().__init__(parent)

        self._installation: HTInstallation = installation
        self._module: Module = module
        self._restype: ResourceType = restype

        self.resname: str = ""
        self.data: bytes = b''
        self.filepath: str = ""

        from tools.module import insert_instance_ui
        self.ui = insert_instance_ui.Ui_Dialog()
        self.ui.setupUi(self)
        self._setupSignals()
        self._setupSelect()
        self._setupList()

    def _setupSignals(self) -> None:
        self.ui.templateCheck.toggled.connect(self.onTemplateCheckToggled)
        self.ui.resrefEdit.textEdited.connect(self.onResRefEdited)

    def _setupSelect(self) -> None:
        self.ui.locationSelect.addItem(self._installation.override_path())
        for capsule in self._module.capsules():
            self.ui.locationSelect.addItem(capsule.path())

    def _setupList(self) -> None:
        for resource in self._installation.chitin_resources():
            if resource.restype() == self._restype:
                item = QListWidgetItem(resource.resname())
                item.setData(QtCore.Qt.UserRole, resource)
                self.ui.templateList.addItem(item)
        if self.ui.templateList.count() > 0:
            self.ui.templateList.item(0).setSelected(True)
        self.ui.templateCheck.setChecked(self.ui.templateList.count() > 0)

    def accept(self) -> None:
        super().accept()

        if self.ui.templateCheck.isChecked():
            self.data = self.ui.templateList.selectedItems()[0].data(QtCore.Qt.UserRole).data()
        elif self._restype == ResourceType.UTC:
            self.data = bytes_utc(UTC())
        elif self._restype == ResourceType.UTP:
            self.data = bytes_utp(UTP())
        elif self._restype == ResourceType.UTD:
            self.data = bytes_utd(UTD())
        elif self._restype == ResourceType.UTE:
            self.data = bytes_ute(UTE())
        elif self._restype == ResourceType.UTT:
            self.data = bytes_utt(UTT())
        elif self._restype == ResourceType.UTS:
            self.data = bytes_uts(UTS())
        elif self._restype == ResourceType.UTM:
            self.data = bytes_utm(UTM())
        elif self._restype == ResourceType.UTW:
            self.data = bytes_utw(UTW())
        else:
            self.data = b''

        self.resname = self.ui.resrefEdit.text()
        self.filepath = self.ui.locationSelect.currentText()

        if self.filepath.endswith(".erf") or self.filepath.endswith(".mod"):
            erf = read_erf(self.filepath)
            erf.set(self.resname, self._restype, self.data)
            write_erf(erf, self.filepath)
        elif self.filepath.endswith(".rim"):
            rim = read_rim(self.filepath)
            rim.set(self.resname, self._restype, self.data)
            write_rim(rim, self.filepath)
        else:
            self.filepath = "{}/{}.{}".format(self.filepath, self.resname, self._restype.extension)
            BinaryWriter.dump(self.filepath, self.data)

        self._module.add_locations(self.resname, self._restype, [self.filepath])

    def onTemplateCheckToggled(self, checked: bool) -> None:
        self.ui.templateList.setEnabled(checked)

    def onResRefEdited(self, text: str) -> None:
        valid = self._module.resource(text, self._restype) is None and text != ""
        self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(valid)
