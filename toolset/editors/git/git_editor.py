from __future__ import annotations

import operator
from abc import ABC, abstractmethod
from contextlib import suppress
from copy import deepcopy
from typing import Optional, Set, Dict

from PyQt5 import QtCore
from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QIcon, QColor, QKeySequence, QKeyEvent
from PyQt5.QtWidgets import QWidget, QMessageBox, QMenu, QListWidgetItem, QCheckBox, QAction
from pykotor.extract.file import ResourceIdentifier

from editors.git.git_settings import GITSettings
from pykotor.common.geometry import Vector2, SurfaceMaterial
from pykotor.extract.installation import SearchLocation
from pykotor.resource.formats.bwm import read_bwm
from pykotor.resource.formats.lyt import LYT, read_lyt
from pykotor.resource.generics.git import read_git, GIT, GITInstance, GITCreature, GITTrigger, GITEncounter, GITCamera, \
    GITWaypoint, GITSound, GITStore, GITPlaceable, GITDoor, bytes_git
from pykotor.resource.type import ResourceType

from data.installation import HTInstallation
from editors.editor import Editor
from editors.git.git_dialogs import openInstanceDialog
from pykotor.tools.template import extract_name, extract_tag
from utils.window import openResourceEditor


class GITEditor(Editor):
    settingsUpdated = QtCore.pyqtSignal(object)

    def __init__(self, parent: Optional[QWidget], installation: Optional[HTInstallation] = None):
        supported = [ResourceType.GIT]
        super().__init__(parent, "GIT Editor", "git", supported, supported, installation)

        from editors.git import ui_git_editor
        self.ui = ui_git_editor.Ui_MainWindow()
        self.ui.setupUi(self)
        self._setupMenus()
        self._setupSignals()
        self._setupHotkeys()

        self._git: GIT = GIT()
        self._mode: _Mode = _InstanceMode(self, installation)
        self._geomInstance: Optional[GITInstance] = None  # Used to track which trigger/encounter you are editing

        self.settings = GITSettings(self)

        self.materialColors: Dict[SurfaceMaterial, QColor] = {
            SurfaceMaterial.UNDEFINED: QColor(255, 0, 0, 40),
            SurfaceMaterial.OBSCURING: QColor(255, 0, 0, 40),
            SurfaceMaterial.DIRT: QColor(0x444444),
            SurfaceMaterial.GRASS: QColor(0x444444),
            SurfaceMaterial.STONE: QColor(0x444444),
            SurfaceMaterial.WOOD: QColor(0x444444),
            SurfaceMaterial.WATER: QColor(0x444444),
            SurfaceMaterial.NON_WALK: QColor(255, 0, 0, 40),
            SurfaceMaterial.TRANSPARENT: QColor(255, 0, 0, 40),
            SurfaceMaterial.CARPET: QColor(0x444444),
            SurfaceMaterial.METAL: QColor(0x444444),
            SurfaceMaterial.PUDDLES: QColor(0x444444),
            SurfaceMaterial.SWAMP: QColor(0x444444),
            SurfaceMaterial.MUD: QColor(0x444444),
            SurfaceMaterial.LEAVES: QColor(0x444444),
            SurfaceMaterial.LAVA: QColor(255, 0, 0, 40),
            SurfaceMaterial.BOTTOMLESS_PIT: QColor(255, 0, 0, 40),
            SurfaceMaterial.DEEP_WATER: QColor(255, 0, 0, 40),
            SurfaceMaterial.DOOR: QColor(0x444444),
            SurfaceMaterial.NON_WALK_GRASS: QColor(255, 0, 0, 40),
            SurfaceMaterial.TRIGGER: QColor(0x999900)
        }
        self.nameBuffer: Dict[ResourceIdentifier, str] = {}
        self.tagBuffer: Dict[ResourceIdentifier, str] = {}

        self.ui.renderArea.materialColors = self.materialColors
        self.ui.renderArea.hideWalkmeshEdges = True
        self.ui.renderArea.highlightBoundaries = False

        self.new()

    def _setupHotkeys(self) -> None:
        self.ui.actionDeleteSelected.setShortcut(QKeySequence("Del"))
        self.ui.actionZoomIn.setShortcut(QKeySequence("+"))
        self.ui.actionZoomOut.setShortcut(QKeySequence("-"))

    def _setupSignals(self) -> None:
        self.ui.renderArea.mousePressed.connect(self.onMousePressed)
        self.ui.renderArea.mouseMoved.connect(self.onMouseMoved)
        self.ui.renderArea.mouseScrolled.connect(self.onMouseScrolled)
        self.ui.renderArea.customContextMenuRequested.connect(self.onContextMenu)

        self.ui.filterEdit.textEdited.connect(self.onFilterEdited)
        self.ui.listWidget.itemSelectionChanged.connect(self.onItemSelectionChanged)
        self.ui.listWidget.customContextMenuRequested.connect(self.onItemContextMenu)

        self.ui.viewCreatureCheck.toggled.connect(self.updateInstanceVisibility)
        self.ui.viewPlaceableCheck.toggled.connect(self.updateInstanceVisibility)
        self.ui.viewDoorCheck.toggled.connect(self.updateInstanceVisibility)
        self.ui.viewSoundCheck.toggled.connect(self.updateInstanceVisibility)
        self.ui.viewTriggerCheck.toggled.connect(self.updateInstanceVisibility)
        self.ui.viewEncounterCheck.toggled.connect(self.updateInstanceVisibility)
        self.ui.viewWaypointCheck.toggled.connect(self.updateInstanceVisibility)
        self.ui.viewCameraCheck.toggled.connect(self.updateInstanceVisibility)
        self.ui.viewStoreCheck.toggled.connect(self.updateInstanceVisibility)

        self.ui.viewCreatureCheck.mouseDoubleClickEvent = lambda _: self.onInstanceVisibilityDoubleClick(self.ui.viewCreatureCheck)
        self.ui.viewPlaceableCheck.mouseDoubleClickEvent = lambda _: self.onInstanceVisibilityDoubleClick(self.ui.viewPlaceableCheck)
        self.ui.viewDoorCheck.mouseDoubleClickEvent = lambda _: self.onInstanceVisibilityDoubleClick(self.ui.viewDoorCheck)
        self.ui.viewSoundCheck.mouseDoubleClickEvent = lambda _: self.onInstanceVisibilityDoubleClick(self.ui.viewSoundCheck)
        self.ui.viewTriggerCheck.mouseDoubleClickEvent = lambda _: self.onInstanceVisibilityDoubleClick(self.ui.viewTriggerCheck)
        self.ui.viewEncounterCheck.mouseDoubleClickEvent = lambda _: self.onInstanceVisibilityDoubleClick(self.ui.viewEncounterCheck)
        self.ui.viewWaypointCheck.mouseDoubleClickEvent = lambda _: self.onInstanceVisibilityDoubleClick(self.ui.viewWaypointCheck)
        self.ui.viewCameraCheck.mouseDoubleClickEvent = lambda _: self.onInstanceVisibilityDoubleClick(self.ui.viewCameraCheck)
        self.ui.viewStoreCheck.mouseDoubleClickEvent = lambda _: self.onInstanceVisibilityDoubleClick(self.ui.viewStoreCheck)

        # Edit
        self.ui.actionDeleteSelected.triggered.connect(lambda: self._mode.removeSelected())
        # View
        self.ui.actionZoomIn.triggered.connect(lambda: self.ui.renderArea.zoomInCamera(1))
        self.ui.actionZoomOut.triggered.connect(lambda: self.ui.renderArea.zoomInCamera(-1))
        self.ui.actionRecentreCamera.triggered.connect(lambda: self.ui.renderArea.centerCamera())
        # View -> Creature Labels
        self.ui.actionUseCreatureResRef.triggered.connect(lambda: setattr(self.settings, "doorLabel", "resref"))
        self.ui.actionUseCreatureResRef.triggered.connect(self.updateInstanceVisibility)
        self.ui.actionUseCreatureTag.triggered.connect(lambda: setattr(self.settings, "doorLabel", "tag"))
        self.ui.actionUseCreatureTag.triggered.connect(self.updateInstanceVisibility)
        self.ui.actionUseCreatureName.triggered.connect(lambda: setattr(self.settings, "doorLabel", "name"))
        self.ui.actionUseCreatureName.triggered.connect(self.updateInstanceVisibility)
        # View -> Door Labels
        self.ui.actionUseDoorResRef.triggered.connect(lambda: setattr(self.settings, "doorLabel", "resref"))
        self.ui.actionUseDoorResRef.triggered.connect(self.updateInstanceVisibility)
        self.ui.actionUseDoorTag.triggered.connect(lambda: setattr(self.settings, "doorLabel", "tag"))
        self.ui.actionUseDoorTag.triggered.connect(self.updateInstanceVisibility)
        self.ui.actionUseDoorResName.triggered.connect(lambda: setattr(self.settings, "doorLabel", "res_name"))
        self.ui.actionUseDoorResName.triggered.connect(self.updateInstanceVisibility)
        self.ui.actionUseDoorResTag.triggered.connect(lambda: setattr(self.settings, "doorLabel", "res_tag"))
        self.ui.actionUseDoorResTag.triggered.connect(self.updateInstanceVisibility)
        # View -> Placeable Labels
        self.ui.actionUsePlaceableResRef.triggered.connect(lambda: setattr(self.settings, "placeableLabel", "resref"))
        self.ui.actionUsePlaceableResRef.triggered.connect(self.updateInstanceVisibility)
        self.ui.actionUsePlaceableResName.triggered.connect(lambda: setattr(self.settings, "placeableLabel", "res_name"))
        self.ui.actionUsePlaceableResName.triggered.connect(self.updateInstanceVisibility)
        self.ui.actionUsePlaceableResTag.triggered.connect(lambda: setattr(self.settings, "placeableLabel", "res_tag"))
        self.ui.actionUsePlaceableResTag.triggered.connect(self.updateInstanceVisibility)
        # View -> Waypoint Labels
        self.ui.actionUseWaypointResRef.triggered.connect(lambda: setattr(self.settings, "waypointLabel", "resref"))
        self.ui.actionUseWaypointResRef.triggered.connect(self.updateInstanceVisibility)
        self.ui.actionUseWaypointName.triggered.connect(lambda: setattr(self.settings, "waypointLabel", "name"))
        self.ui.actionUseWaypointName.triggered.connect(self.updateInstanceVisibility)
        self.ui.actionUseWaypointTag.triggered.connect(lambda: setattr(self.settings, "waypointLabel", "tag"))
        self.ui.actionUseWaypointTag.triggered.connect(self.updateInstanceVisibility)
        self.ui.actionUseWaypointResName.triggered.connect(lambda: setattr(self.settings, "waypointLabel", "res_name"))
        self.ui.actionUseWaypointResName.triggered.connect(self.updateInstanceVisibility)
        self.ui.actionUseWaypointResTag.triggered.connect(lambda: setattr(self.settings, "waypointLabel", "res_tag"))
        self.ui.actionUseWaypointResTag.triggered.connect(self.updateInstanceVisibility)
        # View -> Trigger Labels
        self.ui.actionUseTriggerResRef.triggered.connect(lambda: setattr(self.settings, "triggerLabel", "resref"))
        self.ui.actionUseTriggerResRef.triggered.connect(self.updateInstanceVisibility)
        self.ui.actionUseTriggerTag.triggered.connect(lambda: setattr(self.settings, "triggerLabel", "tag"))
        self.ui.actionUseTriggerTag.triggered.connect(self.updateInstanceVisibility)
        self.ui.actionUseTriggerResName.triggered.connect(lambda: setattr(self.settings, "triggerLabel", "res_name"))
        self.ui.actionUseTriggerResName.triggered.connect(self.updateInstanceVisibility)
        self.ui.actionUseTriggerResTag.triggered.connect(lambda: setattr(self.settings, "triggerLabel", "res_tag"))
        self.ui.actionUseTriggerResTag.triggered.connect(self.updateInstanceVisibility)

    def load(self, filepath: str, resref: str, restype: ResourceType, data: bytes) -> None:
        super().load(filepath, resref, restype, data)

        order = [SearchLocation.OVERRIDE, SearchLocation.CHITIN, SearchLocation.MODULES]
        result = self._installation.resource(resref, ResourceType.LYT, order)
        if result:
            m = QMessageBox(QMessageBox.Information,
                            "Found the corresponding LYT file.",
                            "Would you like to load it?\n" + result.filepath,
                            QMessageBox.Yes | QMessageBox.No,
                            self)
            if m.exec():
                self.loadLayout(read_lyt(result.data))

        self._git = read_git(data)
        self.ui.renderArea.setGit(self._git)
        self.updateInstanceVisibility()
        self.ui.renderArea.centerCamera()

    def build(self) -> bytes:
        return bytes_git(self._git)

    def new(self) -> None:
        super().new()

    def loadLayout(self, layout: LYT) -> None:
        walkmeshes = []
        for room in layout.rooms:
            order = [SearchLocation.OVERRIDE, SearchLocation.CHITIN, SearchLocation.MODULES]
            findBWM = self._installation.resource(room.model, ResourceType.WOK, order)
            if findBWM is not None:
                walkmeshes.append(read_bwm(findBWM.data))

        self.ui.renderArea.setWalkmeshes(walkmeshes)

    def git(self) -> GIT:
        return self._git

    def setMode(self, mode: _Mode) -> None:
        self._mode = mode

    def removeSelected(self) -> None:
        self._mode.removeSelected()

    def updateStatusBar(self) -> None:
        self._mode.updateStatusBar()

    def onInstanceVisibilityDoubleClick(self, checkbox: QCheckBox) -> None:
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

    # region Instance State Events
    def updateInstanceVisibility(self) -> None:
        self._mode.updateInstanceVisibility()

    def onContextMenu(self, point: QPoint) -> None:
        self._mode.onContextMenu(point)

    def onFilterEdited(self) -> None:
        self._mode.onFilterEdited()

    def onItemSelectionChanged(self) -> None:
        self._mode.onItemSelectionChanged()

    def onItemContextMenu(self, point: QPoint) -> None:
        self._mode.onItemContextMenu(point)

    def onMouseMoved(self, screen: Vector2, delta: Vector2, buttons: Set[int], keys: Set[int]) -> None:
        self._mode.onMouseMoved(screen, delta, buttons, keys)

    def onMouseScrolled(self, delta: Vector2, buttons: Set[int], keys: Set[int]) -> None:
        self._mode.onMouseScrolled(delta, buttons, keys)

    def onMousePressed(self, screen: Vector2, buttons: Set[int], keys: Set[int]) -> None:
        self._mode.onMousePressed(screen, buttons, keys)

    def keyPressEvent(self, e: QKeyEvent) -> None:
        super().keyPressEvent(e)
        self.ui.renderArea.keyPressEvent(e)

    def keyReleaseEvent(self, e: QKeyEvent) -> None:
        super().keyPressEvent(e)
        self.ui.renderArea.keyReleaseEvent(e)
    # endregion


class _Mode(ABC):
    def __init__(self, editor: GITEditor, installation: HTInstallation):
        self._editor: GITEditor = editor
        self._installation: HTInstallation = installation

        from editors.git import ui_git_editor
        self._ui: ui_git_editor = editor.ui

    @abstractmethod
    def removeSelected(self) -> None:
        ...

    @abstractmethod
    def updateStatusBar(self) -> None:
        ...

    @abstractmethod
    def updateInstanceVisibility(self) -> None:
        ...

    @abstractmethod
    def onMouseMoved(self, screen: Vector2, delta: Vector2, buttons: Set[int], keys: Set[int]) -> None:
        ...

    @abstractmethod
    def onMousePressed(self, screen: Vector2, buttons: Set[int], keys: Set[int]) -> None:
        ...

    @abstractmethod
    def onMouseScrolled(self, delta: Vector2, buttons: Set[int], keys: Set[int]) -> None:
        ...

    @abstractmethod
    def onContextMenu(self, point: QPoint) -> None:
        ...

    @abstractmethod
    def onFilterEdited(self) -> None:
        ...

    @abstractmethod
    def onItemSelectionChanged(self) -> None:
        ...

    @abstractmethod
    def onItemContextMenu(self, point: QPoint) -> None:
        ...


class _InstanceMode(_Mode):
    def __init__(self, editor: GITEditor, installation: HTInstallation):
        super(_InstanceMode, self).__init__(editor, installation)
        self._ui.renderArea.hideGeomPoints = True
        self.updateInstanceVisibility()

    def _getBufferedName(self, resid: ResourceIdentifier) -> str:
        if resid not in self._editor.nameBuffer:
            res = self._installation.resource(resid.resname, resid.restype)
            if res is not None:
                self._editor.nameBuffer[resid] = self._installation.string(extract_name(res.data))
        return self._editor.nameBuffer[resid] if resid in self._editor.nameBuffer else resid.resname

    def _getBufferedTag(self, resid: ResourceIdentifier) -> str:
        if resid not in self._editor.tagBuffer:
            res = self._installation.resource(resid.resname, resid.restype)
            if res is not None:
                self._editor.tagBuffer[resid] = extract_tag(res.data)
        return self._editor.tagBuffer[resid] if resid in self._editor.tagBuffer else resid.resname

    def getInstanceLabel(self, instance: GITInstance) -> str:
        index = self._editor.git().index(instance)
        resid = None if instance.identifier() is None else instance.identifier()

        if isinstance(instance, GITCamera):
            label = "CameraID=" + str(instance.camera_id)
        else:
            label = resid.resname

        if isinstance(instance, GITCreature):
            if self._editor.settings.doorLabel == "tag":
                label = self._getBufferedTag(resid)
            elif self._editor.settings.doorLabel == "name":
                label = self._getBufferedName(resid)
        elif isinstance(instance, GITDoor):
            if self._editor.settings.doorLabel == "tag":
                label = instance.tag
            elif self._editor.settings.doorLabel == "res_name":
                label = self._getBufferedName(resid)
            elif self._editor.settings.doorLabel == "res_tag":
                label = self._getBufferedTag(resid)
        elif isinstance(instance, GITPlaceable):
            if self._editor.settings.placeableLabel == "res_name":
                label = self._getBufferedName(resid)
            elif self._editor.settings.placeableLabel == "res_tag":
                label = self._getBufferedTag(resid)
        elif isinstance(instance, GITWaypoint):
            if self._editor.settings.waypointLabel == "tag":
                label = instance.tag
            elif self._editor.settings.waypointLabel == "name":
                label = self._installation.string(instance.name)
            elif self._editor.settings.waypointLabel == "res_name":
                label = self._getBufferedName(resid)
            elif self._editor.settings.waypointLabel == "res_tag":
                label = self._getBufferedTag(resid)
        elif isinstance(instance, GITTrigger):
            if self._editor.settings.triggerLabel == "tag":
                label = instance.tag
            elif self._editor.settings.triggerLabel == "res_name":
                label = self._getBufferedName(resid)
            elif self._editor.settings.triggerLabel == "res_tag":
                label = self._getBufferedTag(resid)

        return "[{}] {}".format(index, label)

    def updateStatusBar(self) -> None:
        screen = self._ui.renderArea.mapFromGlobal(self._editor.cursor().pos())
        world = self._ui.renderArea.toWorldCoords(screen.x(), screen.y())

        reference = ""
        if self._ui.renderArea.instancesUnderMouse():
            instance = self._ui.renderArea.instancesUnderMouse()[0]
            reference = "" if instance.identifier() is None else instance.identifier().resname

        statusFormat = "Mode: Instance Mode, X: {:.2f}, Y: {:.2f}, Z: {:.2f}, ResRef: {}"
        status = statusFormat.format(world.x, world.y, world.z, reference)

        self._editor.statusBar().showMessage(status)

    def updateInstanceVisibility(self):
        self._ui.renderArea.hideCreatures = not self._ui.viewCreatureCheck.isChecked()
        self._ui.renderArea.hidePlaceables = not self._ui.viewPlaceableCheck.isChecked()
        self._ui.renderArea.hideDoors = not self._ui.viewDoorCheck.isChecked()
        self._ui.renderArea.hideTriggers = not self._ui.viewTriggerCheck.isChecked()
        self._ui.renderArea.hideEncounters = not self._ui.viewEncounterCheck.isChecked()
        self._ui.renderArea.hideWaypoints = not self._ui.viewWaypointCheck.isChecked()
        self._ui.renderArea.hideSounds = not self._ui.viewSoundCheck.isChecked()
        self._ui.renderArea.hideStores = not self._ui.viewStoreCheck.isChecked()
        self._ui.renderArea.hideCameras = not self._ui.viewCameraCheck.isChecked()
        self.rebuildInstanceList()

    def rebuildInstanceList(self) -> None:
        self._ui.listWidget.clear()

        # We will split cameras from the rest of the instances so they can be sorted seperately
        cameras = [camera for camera in self._editor.git().instances() if isinstance(camera, GITCamera)]
        instances = [instance for instance in self._editor.git().instances() if not isinstance(instance, GITCamera)]

        cameras = sorted(cameras, key=operator.attrgetter('camera_id'))

        # Join the two lists back together and add all items to the list
        for instance in instances + cameras:
            if (
                    self._ui.renderArea.isInstanceVisible(instance)
                    and (instance.identifier() is None
                         or self._ui.filterEdit.text() in instance.identifier().resname
                         or instance.identifier().resname == "")
            ):
                icon = QIcon(self._ui.renderArea.instancePixmap(instance))
                text = self.getInstanceLabel(instance)
                item = QListWidgetItem(icon, text)
                item.setData(QtCore.Qt.UserRole, instance)
                self._ui.listWidget.addItem(item)

    def selectInstanceItem(self, instance: GITInstance) -> None:
        # Block signals to prevent the camera from snapping to the instance every time the player clicks on an instance
        # see: onItemSelectionChanged()
        self._ui.listWidget.blockSignals(True)
        for i in range(self._ui.listWidget.count()):
            item = self._ui.listWidget.item(i)
            if item.data(QtCore.Qt.UserRole) is instance:
                self._ui.listWidget.setCurrentItem(item)
        self._ui.listWidget.blockSignals(False)

    def removeSelected(self) -> None:
        for instance in self._ui.renderArea.selectedInstances():
            self._editor.git().remove(instance)
        self._ui.renderArea.clearSelectedInstances()
        self.rebuildInstanceList()

    def addInstance(self, instance: GITInstance):
        self._editor.git().add(instance)
        self.rebuildInstanceList()

    def editSelectedInstance(self) -> None:
        instance = self._ui.renderArea.selectedInstances()[0]
        openInstanceDialog(self._editor, instance, self._installation)
        self.rebuildInstanceList()

    def editResource(self, instance: GITInstance) -> None:
        res = self._installation.resource(instance.identifier().resname, instance.identifier().restype)
        if not res:
            filepath = "{}/{}.{}".format(self._installation.override_path(), instance.identifier().resname, instance.identifier().restype.extension)
            with open(filepath, "wb") as f:
                f.write(instance.blank())
            self._installation.reload_override("")
            res = self._installation.resource(instance.identifier().resname, instance.identifier().restype)
        openResourceEditor(res.filepath, res.resname, res.restype, res.data, self._installation, self._editor)

    def onMouseMoved(self, screen: Vector2, delta: Vector2, buttons: Set[int], keys: Set[int]) -> None:
        worldDelta = self._ui.renderArea.toWorldDelta(delta.x, delta.y)

        if QtCore.Qt.LeftButton in buttons and QtCore.Qt.Key_Control in keys:
            self._ui.renderArea.panCamera(-worldDelta.x, -worldDelta.y)
        elif QtCore.Qt.MiddleButton in buttons and QtCore.Qt.Key_Control in keys:
            self._ui.renderArea.rotateCamera(delta.x / 50)
        elif QtCore.Qt.LeftButton in buttons and not QtCore.Qt.Key_Control in keys and not self._ui.lockInstancesCheck.isChecked():
            for instance in self._ui.renderArea.selectedInstances():
                instance.move(worldDelta.x, worldDelta.y, 0.0)
                # Snap the instance on top of the walkmesh, if there is no walkmesh underneath it will snap Z to 0
                getZ = self._ui.renderArea.getZCoord(instance.position.x, instance.position.y)
                instance.position.z = getZ if getZ != 0.0 else instance.position.z

        self.updateStatusBar()

    def onMousePressed(self, screen: Vector2, buttons: Set[int], keys: Set[int]) -> None:
        underMouse = self._ui.renderArea.instancesUnderMouse()
        currentSelecton = self._ui.renderArea.selectedInstances()

        if QtCore.Qt.LeftButton in buttons and QtCore.Qt.Key_Alt in keys:
            if self._ui.renderArea.instancesUnderMouse():
                original = self._ui.renderArea.instancesUnderMouse()[0]
                duplicate = deepcopy(original)
                self._editor.git().add(duplicate)
                self.rebuildInstanceList()
                self.selectInstanceItem(original)

        # Do not change the selection if the selected instance if its still underneath the mouse
        if currentSelecton and currentSelecton[0] in underMouse:
            return

        self._ui.renderArea.clearSelectedInstances()
        if self._ui.renderArea.instancesUnderMouse():
            instance = self._ui.renderArea.instancesUnderMouse()[0]
            self._ui.renderArea.selectInstances([instance])
            self.selectInstanceItem(instance)

    def onMouseScrolled(self, delta: Vector2, buttons: Set[int], keys: Set[int]) -> None:
        if QtCore.Qt.Key_Control in keys:
            self._ui.renderArea.zoomInCamera(delta.y / 50)

    def onContextMenu(self, point: QPoint) -> None:
        menu = QMenu(self._editor)
        world = self._ui.renderArea.toWorldCoords(point.x(), point.y())

        # Show "Remove" action if instances are selected
        if self._ui.renderArea.selectedInstances():
            menu.addAction("Remove").triggered.connect(self.removeSelected)

        # Show "Edit Instance"+"Edit Geometry" action if a single instance is selected
        if len(self._ui.renderArea.selectedInstances()) == 1:
            instance = self._ui.renderArea.selectedInstances()[0]

            menu.addAction("Edit Instance").triggered.connect(self.editSelectedInstance)

            actionEditResource = menu.addAction("Edit Resource")
            actionEditResource.triggered.connect(lambda: self.editResource(instance))
            actionEditResource.setEnabled(not isinstance(instance, GITCamera))
            menu.addAction(actionEditResource)

            if isinstance(instance, GITEncounter) or isinstance(instance, GITTrigger):
                menu.addAction("Edit Geometry").triggered.connect(lambda: self._editor.setMode(_GeometryMode(self._editor, self._installation)))

        # If no instances are selected then show the actions to add new instances
        if len(self._ui.renderArea.selectedInstances()) == 0:
            menu.addAction("Insert Creature").triggered.connect(lambda: self.addInstance(GITCreature(world.x, world.y)))
            menu.addAction("Insert Door").triggered.connect(lambda: self.addInstance(GITDoor(world.x, world.y)))
            menu.addAction("Insert Placeable").triggered.connect(lambda: self.addInstance(GITPlaceable(world.x, world.y)))
            menu.addAction("Insert Store").triggered.connect(lambda: self.addInstance(GITStore(world.x, world.y)))
            menu.addAction("Insert Sound").triggered.connect(lambda: self.addInstance(GITSound(world.x, world.y)))
            menu.addAction("Insert Waypoint").triggered.connect(lambda: self.addInstance(GITWaypoint(world.x, world.y)))
            menu.addAction("Insert Camera").triggered.connect(lambda: self.addInstance(GITCamera(world.x, world.y)))
            menu.addAction("Insert Encounter").triggered.connect(lambda: self.addInstance(GITEncounter(world.x, world.y)))
            menu.addAction("Insert Trigger").triggered.connect(lambda: self.addInstance(GITTrigger(world.x, world.y)))

        menu.addSeparator()

        # If there are instances under the mouse, add actions for each one of them. If the player triggers on of them
        # the selection will change appropriately.
        for instance in self._ui.renderArea.instancesUnderMouse():
            icon = QIcon(self._ui.renderArea.instancePixmap(instance))
            reference = "" if instance.identifier().resname is None else instance.identifier().resname
            index = self._editor.git().index(instance)
            onTriggered = lambda checked, inst=instance: self._ui.renderArea.selectInstance(inst)
            menu.addAction(icon, "[{}] {}".format(index, reference)).triggered.connect(onTriggered)

        menu.popup(self._ui.renderArea.mapToGlobal(point))

    def onFilterEdited(self) -> None:
        self._ui.renderArea.instanceFilter = self._ui.filterEdit.text()
        self.rebuildInstanceList()

    def onItemSelectionChanged(self) -> None:
        if self._ui.listWidget.selectedItems():
            item = self._ui.listWidget.selectedItems()[0]
            instance = item.data(QtCore.Qt.UserRole)
            self._ui.renderArea.setCameraPosition(instance.position.x, instance.position.y)
            self._ui.renderArea.selectInstance(instance)

    def onItemContextMenu(self, point: QPoint) -> None:
        if not self._ui.listWidget.selectedItems():
            return

        instance = self._ui.listWidget.selectedItems()[0].data(QtCore.Qt.UserRole)
        menu = QMenu(self._ui.listWidget)

        menu.addAction("Remove").triggered.connect(self.removeSelected)
        menu.addAction("Edit Instance").triggered.connect(self.editSelectedInstance)

        actionEditResource = menu.addAction("Edit Resource")
        actionEditResource.triggered.connect(lambda: self.editResource(instance))
        actionEditResource.setEnabled(not isinstance(instance, GITCamera))
        menu.addAction(actionEditResource)

        menu.popup(self._ui.listWidget.mapToGlobal(point))


class _GeometryMode(_Mode):
    def __init__(self, editor: GITEditor, installation: HTInstallation):
        super(_GeometryMode, self).__init__(editor, installation)

        self._ui.renderArea.hideCreatures = True
        self._ui.renderArea.hideDoors = True
        self._ui.renderArea.hidePlaceables = True
        self._ui.renderArea.hideSounds = True
        self._ui.renderArea.hideStores = True
        self._ui.renderArea.hideCameras = True
        self._ui.renderArea.hideTriggers = True
        self._ui.renderArea.hideEncounters = True
        self._ui.renderArea.hideWaypoints = True
        self._ui.renderArea.hideGeomPoints = False

    def removeSelected(self) -> None:
        geomPoints = self._ui.renderArea.selectedGeomPoints()
        for geomPoint in geomPoints:
            geomPoint.instance.geometry.remove(geomPoint.point)

    def insertPointAtMouse(self) -> None:
        screen = self._ui.renderArea.mapFromGlobal(self._editor.cursor().pos())
        world = self._ui.renderArea.toWorldCoords(screen.x(), screen.y())

        instance = self._ui.renderArea.selectedInstances()[0]
        point = world - instance.position
        instance.geometry.points.append(point)

    def editSelectedPoint(self) -> None:
        raise NotImplementedError()

    def updateStatusBar(self) -> None:
        screen = self._ui.renderArea.mapFromGlobal(self._editor.cursor().pos())
        world = self._ui.renderArea.toWorldCoords(screen.x(), screen.y())

        pointIndex = ""
        if self._ui.renderArea.geomPointsUnderMouse():
            with suppress(ValueError):
                instance = self._ui.renderArea.selectedInstances()[0]
                pointIndex = instance.geometry.points.index(self._ui.renderArea.geomPointsUnderMouse()[0].point)

        statusFormat = "Mode: Geometry Mode, X: {:.2f}, Y: {:.2f}, Z: {:.2f}, Point: {}"
        status = statusFormat.format(world.x, world.y, world.z, pointIndex)

        self._editor.statusBar().showMessage(status)

    def updateInstanceVisibility(self) -> None:
        ...

    def onMouseMoved(self, screen: Vector2, delta: Vector2, buttons: Set[int], keys: Set[int]) -> None:
        worldDelta = self._ui.renderArea.toWorldDelta(delta.x, delta.y)

        if QtCore.Qt.LeftButton in buttons and QtCore.Qt.Key_Control in keys:
            self._ui.renderArea.panCamera(-worldDelta.x, -worldDelta.y)
        elif QtCore.Qt.MiddleButton in buttons and QtCore.Qt.Key_Control in keys:
            self._ui.renderArea.rotateCamera(delta.x / 50)
        elif QtCore.Qt.LeftButton in buttons and not QtCore.Qt.Key_Control in keys and self._ui.renderArea.selectedGeomPoints():
            instance, point = self._ui.renderArea.selectedGeomPoints()[0]
            point.x += worldDelta.x
            point.y += worldDelta.y
            point.z = self._ui.renderArea.toWorldCoords(instance.position.x, instance.position.y).z

        self.updateStatusBar()

    def onMousePressed(self, screen: Vector2, buttons: Set[int], keys: Set[int]) -> None:
        if self._ui.renderArea.geomPointsUnderMouse():
            point = self._ui.renderArea.geomPointsUnderMouse()[0]
            self._ui.renderArea.selectGeomPoint(point)
        else:
            self._ui.renderArea.clearSelectedGeomPoints()

    def onMouseScrolled(self, delta: Vector2, buttons: Set[int], keys: Set[int]) -> None:
        if QtCore.Qt.Key_Control in keys:
            self._ui.renderArea.zoomInCamera(delta.y / 50)

    def onContextMenu(self, point: QPoint) -> None:
        menu = QMenu(self._editor)

        if self._ui.renderArea.selectedGeomPoints():
            menu.addAction("Remove").triggered.connect(self.removeSelected)

        if len(self._ui.renderArea.selectedGeomPoints()) == 1:
            menu.addAction("Edit").triggered.connect(self.editSelectedPoint)

        if len(self._ui.renderArea.selectedGeomPoints()) == 0:
            menu.addAction("Insert").triggered.connect(self.insertPointAtMouse)

        menu.addSeparator()
        menu.addAction("Finish Editing").triggered.connect(lambda: self._editor.setMode(_InstanceMode(self._editor, self._installation)))

        menu.popup(self._ui.renderArea.mapToGlobal(point))

    def onFilterEdited(self) -> None:
        ...

    def onItemSelectionChanged(self) -> None:
        ...

    def onItemContextMenu(self, point: QPoint) -> None:
        ...
