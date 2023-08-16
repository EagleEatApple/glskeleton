# -*- coding: utf-8 -*-
# refer to https://github.com/pyimgui/pyimgui/tree/master/imgui/integrations
# refer to https://github.com/seanchas116/qtimgui
# refer to https://github.com/pedohorse/lifeblood/blob/dev/src/lifeblood_viewer/nodeeditor.py

from __future__ import absolute_import

import imgui
from imgui.integrations.opengl import ProgrammablePipelineRenderer

from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtCore import QObject, QEvent, Qt, QDateTime
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QMouseEvent, QWheelEvent, QKeyEvent, QCursor


class PySide6Renderer(QObject, ProgrammablePipelineRenderer):
    key_map = {
        Qt.Key_Tab: imgui.KEY_TAB,
        Qt.Key_Left: imgui.KEY_LEFT_ARROW,
        Qt.Key_Right: imgui.KEY_RIGHT_ARROW,
        Qt.Key_Up: imgui.KEY_UP_ARROW,
        Qt.Key_Down: imgui.KEY_DOWN_ARROW,
        Qt.Key_PageUp: imgui.KEY_PAGE_UP,
        Qt.Key_PageDown: imgui.KEY_PAGE_DOWN,
        Qt.Key_Home: imgui.KEY_HOME,
        Qt.Key_End: imgui.KEY_END,
        Qt.Key_Insert: imgui.KEY_INSERT,
        Qt.Key_Delete: imgui.KEY_DELETE,
        Qt.Key_Backspace: imgui.KEY_BACKSPACE,
        Qt.Key_Space: imgui.KEY_SPACE,
        Qt.Key_Enter: imgui.KEY_ENTER,
        Qt.Key_Return: imgui.KEY_ENTER,
        Qt.Key_Escape: imgui.KEY_ESCAPE,
        Qt.Key_A: imgui.KEY_A,
        Qt.Key_C: imgui.KEY_C,
        Qt.Key_V: imgui.KEY_V,
        Qt.Key_X: imgui.KEY_X,
        Qt.Key_Y: imgui.KEY_Y,
        Qt.Key_Z: imgui.KEY_Z,
    }
    cursor_map = {
        imgui.MOUSE_CURSOR_ARROW: Qt.CursorShape.ArrowCursor,
        imgui.MOUSE_CURSOR_TEXT_INPUT: Qt.CursorShape.IBeamCursor,
        imgui.MOUSE_CURSOR_RESIZE_ALL: Qt.CursorShape.SizeAllCursor,
        imgui.MOUSE_CURSOR_RESIZE_NS: Qt.CursorShape.SizeVerCursor,
        imgui.MOUSE_CURSOR_RESIZE_EW: Qt.CursorShape.SizeHorCursor,
        imgui.MOUSE_CURSOR_RESIZE_NESW: Qt.CursorShape.SizeBDiagCursor,
        imgui.MOUSE_CURSOR_RESIZE_NWSE: Qt.CursorShape.SizeFDiagCursor,
        imgui.MOUSE_CURSOR_HAND: Qt.CursorShape.PointingHandCursor,
        imgui.MOUSE_CURSOR_NOT_ALLOWED: Qt.CursorShape.ForbiddenCursor
    }

    def __init__(self, window: QOpenGLWidget) -> None:
        QObject.__init__(self)
        ProgrammablePipelineRenderer.__init__(self)
        self._gui_time: float = 0.0
        self._mouse_pressed: list[bool] = [False, False, False]
        self._mouse_wheel: float = 0.0
        self.widget = window
        for value in self.key_map.values():
            self.io.key_map[value] = value
        self.io.set_clipboard_text_fn = self.setClipboard
        self.io.get_clipboard_text_fn = self.getClipboard
        self.widget.installEventFilter(self)

    def process_inputs(self) -> None:
        io = self.io
        io.display_size = self.widget.size().width(), self.widget.size().height()
        io.display_fb_scale = self.widget.devicePixelRatioF(), self.widget.devicePixelRatioF()

        current_time = QDateTime().currentMSecsSinceEpoch()/1000.0
        if (self._gui_time > 0.0) and ((current_time - self._gui_time) > 0.0):
            io.delta_time = current_time - self._gui_time
        else:
            io.delta_time = 1.0/60.0
        self._gui_time = current_time

        if self.widget.isActiveWindow():
            pos = self.widget.mapFromGlobal(QCursor.pos())
            io.mouse_pos = pos.x(), pos.y()
        else:
            io.mouse_pos = -1, -1

        for i in range(3):
            io.mouse_down[i] = self._mouse_pressed[i]
        io.mouse_wheel = self._mouse_wheel
        self._mouse_wheel = 0.0
        self.updateCursorShape()

    def onMousePressedChange(self, event: QMouseEvent) -> None:
        button = event.buttons()
        if button & Qt.LeftButton:
            self._mouse_pressed[0] = True
        else:
            self._mouse_pressed[0] = False
        if button & Qt.RightButton:
            self._mouse_pressed[1] = True
        else:
            self._mouse_pressed[1] = False
        if button & Qt.MiddleButton:
            self._mouse_pressed[2] = True
        else:
            self._mouse_pressed[2] = False

    def onWheel(self, event: QWheelEvent) -> None:
        deltay = event.pixelDelta().y()
        if deltay != 0:
            self._mouse_wheel += float(deltay) / (5.0 * imgui.get_text_line_height())
        else:
            self._mouse_wheel += float(event.angleDelta().y()) / 120.0

    def onKeyPressRelease(self, event: QKeyEvent) -> None:
        key_pressed = (event.type() == QEvent.KeyPress)
        key = event.key()
        imgui_key = self.key_map.get(key)
        if imgui_key is not None:
            self.io.keys_down[imgui_key] = key_pressed

        if key_pressed:
            text = event.text()
            if len(text) == 1:
                self.io.add_input_character(ord(text))

        self.io.key_ctrl = event.modifiers() & Qt.ControlModifier
        self.io.key_shift = event.modifiers() & Qt.ShiftModifier
        self.io.key_alt = event.modifiers() & Qt.AltModifier
        self.io.key_super = event.modifiers() & Qt.MetaModifier

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if event.type() in (QEvent.MouseButtonPress, QEvent.MouseButtonRelease):
            self.onMousePressedChange(QMouseEvent(event))
        elif event.type() == QEvent.Wheel:
            self.onWheel(QWheelEvent(event))
        elif event.type() in (QEvent.KeyPress, QEvent.KeyRelease):
            self.onKeyPressRelease(QKeyEvent(event))
        return QObject.eventFilter(self, watched, event)

    def setClipboard(self, text: str) -> None:
        QApplication.clipboard().setText(text)

    def getClipboard(self) -> str:
        return QApplication.clipboard().text()

    def updateCursorShape(self) -> None:
        if self.io.config_flags & imgui.CONFIG_NO_MOUSE_CURSOR_CHANGE:
            return

        imgui_cursor = imgui.get_mouse_cursor()
        if self.io.mouse_draw_cursor or (imgui_cursor == imgui.MOUSE_CURSOR_NONE):
            self.widget.setCursor(Qt.CursorShape.BlankCursor)
        else:
            qt_cursor = self.cursor_map.get(imgui_cursor)
            if qt_cursor is not None:
                self.widget.setCursor(qt_cursor)
            else:
                self.widget.setCursor(Qt.CursorShape.ArrowCursor)
