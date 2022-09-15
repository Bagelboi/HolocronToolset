import math
from copy import copy
from typing import Optional, Set

from PyQt5 import QtCore
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QWheelEvent, QResizeEvent, QMouseEvent, QKeyEvent
from PyQt5.QtWidgets import QOpenGLWidget, QWidget
from pykotor.common.geometry import Vector2, Vector3
from pykotor.common.module import Module
from pykotor.gl.scene import Scene, Camera
from pykotor.resource.formats.bwm import BWMFace
from pykotor.resource.generics.git import GITInstance
from pykotor.resource.type import ResourceType

from data.installation import HTInstallation


class ModuleRenderer(QOpenGLWidget):
    sceneInitalized = QtCore.pyqtSignal()
    """Signal emitted when scene has been initialized."""

    mouseMoved = QtCore.pyqtSignal(object, object, object, object)  # screen coords, screen delta, mouse, keys
    """Signal emitted when mouse is moved over the widget."""

    mouseScrolled = QtCore.pyqtSignal(object, object, object)  # screen delta, mouse, keys
    """Signal emitted when mouse is scrolled over the widget."""

    mouseReleased = QtCore.pyqtSignal(object, object, object)  # screen coords, mouse, keys
    """Signal emitted when a mouse button is released after being pressed on the widget."""

    mousePressed = QtCore.pyqtSignal(object, object, object)  # screen coords, mouse, keys
    """Signal emitted when a mouse button is pressed on the widget."""

    keyboardPressed = QtCore.pyqtSignal(object, object)  # mouse, keys

    keyboardReleased = QtCore.pyqtSignal(object, object)  # mouse, keys

    objectSelected = QtCore.pyqtSignal(object)
    """Signal emitted when an object has been selected through the renderer."""

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        from gui.windows.module_designer import ModuleDesignerSettings

        self.scene: Optional[Scene] = None
        self.settings: ModuleDesignerSettings = ModuleDesignerSettings()
        self._module: Optional[Module] = None
        self._installation: Optional[HTInstallation] = None
        self._init = False

        self._keysDown: Set[int] = set()
        self._mouseDown: Set[int] = set()
        self._mousePrev: Vector2 = Vector2(self.cursor().pos().x(), self.cursor().pos().y())

        self.doSelect: bool = False  # Set to true to select object at mouse pointer

    def init(self, installation: HTInstallation, module: Module) -> None:
        self._installation = installation
        self._module = module

        QTimer.singleShot(33, self.loop)

    def loop(self) -> None:
        self.repaint()
        QTimer.singleShot(33, self.loop)

    def walkmeshPoint(self, x: float, y: float, default_z: float = 0.0) -> Vector3:
        face: Optional[BWMFace] = None
        for walkmesh in [res.resource() for res in self._module.resources.values() if
                         res.restype() == ResourceType.WOK]:
            if walkmesh is None:
                continue
            if over := walkmesh.faceAt(x, y):
                if face is None:
                    face = over
                elif not face.material.walkable() and over.material.walkable():
                    face = over
        z = default_z if face is None else face.determine_z(x, y)
        return Vector3(x, y, z)

    def resetMouseButtons(self) -> None:
        self._mouseDown.clear()

    def snapCameraToPoint(self, point: Vector3, distance: float = 5.0):
        camera = self.scene.camera
        newCamPos = Vector3.from_vector3(point)

        camera.x, camera.y, camera.z = point.x, point.y, point.z+1.0
        camera.distance = distance

    def paintGL(self) -> None:
        if not self._init:
            self._init = True
            self.scene = Scene(installation=self._installation, module=self._module)

            self.scene.camera.fov = self.settings.fieldOfView
            self.scene.camera.width = self.width()
            self.scene.camera.height = self.height()

            self.sceneInitalized.emit()

        if self.doSelect:
            self.doSelect = False
            obj = self.scene.pick(self._mousePrev.x, self.height() - self._mousePrev.y)

            if obj is not None and isinstance(obj.data, GITInstance):
                self.objectSelected.emit(obj.data)
            else:
                self.scene.selection.clear()
                self.objectSelected.emit(None)

        screenCursor = self.mapFromGlobal(self.cursor().pos())
        worldCursor = self.scene.screenToWorld(screenCursor.x(), screenCursor.y())
        if screenCursor.x() < self.width() and screenCursor.x() >= 0 and screenCursor.y() < self.height() and screenCursor.y() >= 0:
            self.scene.cursor.set_position(worldCursor.x, worldCursor.y, worldCursor.z)

        self.scene.render()

    # region Accessors
    def keysDown(self) -> Set[int]:
        return copy(self._keysDown)

    def mouseDown(self) -> Set[int]:
        return copy(self._mouseDown)
    # endregion

    # region Camera Transformations
    def panCamera(self, x: float, y: float, z: float) -> None:
        """
        Moves the camera by the specified amount. The movement takes into account both the rotation and zoom of the
        camera on the x/y plane.

        Args:
            x: Units to move the x coordinate.
            y: Units to move the y coordinate.
            z: Units to move the z coordinate.
        """
        forward = y * self.scene.camera.forward()
        sideward = x * self.scene.camera.sideward()

        self.scene.camera.x += (forward.x + sideward.x)
        self.scene.camera.y += (forward.y + sideward.y)
        self.scene.camera.z += z

    def rotateCamera(self, yaw: float, pitch: float) -> None:
        """
        Rotates the camera by the angles (radians) specified.

        Args:
            yaw:
            pitch:
        """
        self.scene.camera.rotate(yaw, pitch)
    # endregion

    # region Events
    def resizeEvent(self, e: QResizeEvent) -> None:
        super().resizeEvent(e)

        self.scene.camera.width = e.size().width()
        self.scene.camera.height = e.size().height()

    def wheelEvent(self, e: QWheelEvent) -> None:
        self.mouseScrolled.emit(Vector2(e.angleDelta().x(), e.angleDelta().y()), self._mouseDown, self._keysDown)

    def mouseMoveEvent(self, e: QMouseEvent) -> None:
        coords = Vector2(e.x(), e.y())
        coordsDelta = Vector2(coords.x - self._mousePrev.x, coords.y - self._mousePrev.y)
        self._mousePrev = coords
        self.mouseMoved.emit(coords, coordsDelta, self._mouseDown, self._keysDown)

    def mousePressEvent(self, e: QMouseEvent) -> None:
        self._mouseDown.add(e.button())
        coords = Vector2(e.x(), e.y())
        self.mousePressed.emit(coords, self._mouseDown, self._keysDown)

    def mouseReleaseEvent(self, e: QMouseEvent) -> None:
        self._mouseDown.discard(e.button())

        coords = Vector2(e.x(), e.y())
        self.mouseReleased.emit(coords, e.buttons(), self._keysDown)

    def keyPressEvent(self, e: QKeyEvent, bubble: bool = True) -> None:
        self._keysDown.add(e.key())
        self.keyboardPressed.emit(self._mouseDown, self._keysDown)
        if bubble:
            self.window().keyPressEvent(e, False)

    def keyReleaseEvent(self, e: QKeyEvent, bubble: bool = True) -> None:
        self._keysDown.discard(e.key())
        if bubble:
            self.window().keyReleaseEvent(e, False)
    # endregion
