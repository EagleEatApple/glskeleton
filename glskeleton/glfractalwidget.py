# refer to https://github.com/denisenkom/mandelbrot-pyopengl/
# refer to https://github.com/jakubcerveny/gl-compute

"""Mandelbrot fractal via a compute shader — ported to gl46 + numpy.

The ImGui panel has been replaced by keyboard shortcuts: Up/Down adjust
max_iter. Mouse drag / wheel still pan and zoom as before.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from gl46.barrier import Barrier
from gl46.program import Program
from gl46.shader import Shader, ShaderStage
from gl46.texture import Texture2D
from gl46.vertexarray import VertexArray
from OpenGL.GL import (
    GL_RGBA32F,
    GL_TRIANGLE_FAN,
    GL_WRITE_ONLY,
    glDrawArrays,
    glGetProgramiv,
    glViewport,
)
from PySide6.QtCore import QPoint, Qt, QTimerEvent
from PySide6.QtGui import QCloseEvent, QKeyEvent, QMouseEvent, QWheelEvent
from PySide6.QtOpenGLWidgets import QOpenGLWidget

try:
    from OpenGL.GL import GL_COMPUTE_WORK_GROUP_SIZE
except ImportError:
    # Some PyOpenGL distributions do not export this constant; fall back to
    # the value from the OpenGL 4.3 core spec.
    GL_COMPUTE_WORK_GROUP_SIZE = 0x8267

SHADER_DIR = Path(__file__).resolve().parent / "shaders"


class GLFractalWidget(QOpenGLWidget):
    def __init__(self) -> None:
        super().__init__()
        self.startTimer(20)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.tex: Texture2D | None = None
        self.size_changed = False
        self.scale = 0.0
        self.panX = 0.0
        self.panY = 0.0
        self.lastPos = QPoint()
        self.centerPos = QPoint()
        self.max_iter = 100

    def timerEvent(self, event: QTimerEvent) -> None:
        self.update()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        key = event.key()
        if key == Qt.Key.Key_Up:
            self.max_iter = min(2000, self.max_iter + 10)
        elif key == Qt.Key.Key_Down:
            self.max_iter = max(50, self.max_iter - 10)
        else:
            super().keyPressEvent(event)
            return
        self.update()

    # ------------------------------------------------------------------ setup

    def initializeGL(self) -> None:
        # ---- display program (fullscreen quad) ----
        self.program = Program(
            [
                Shader.from_file(ShaderStage.VERTEX, SHADER_DIR / "fractal.vert"),
                Shader.from_file(ShaderStage.FRAGMENT, SHADER_DIR / "fractal.frag"),
            ]
        )

        # ---- compute shader program ----
        self.compute_program = Program(
            [
                Shader.from_file(ShaderStage.COMPUTE, SHADER_DIR / "fractal.comp"),
            ]
        )

        # ---- fullscreen quad VAO (4 vertices, no VBO; positions come from gl_VertexID) ----
        self.vao = VertexArray()

    # ------------------------------------------------------------------ draw

    def paintGL(self) -> None:
        if self.tex is None:
            return

        # ---- compute pass ----
        self.compute_program.use()
        self.compute_program.set_f("center", self.panX, self.panY)
        self.compute_program.set_f("scale", self.scale)
        self.compute_program.set_i("max_iter", self.max_iter)

        lsize = np.zeros(3, dtype=np.int32)
        glGetProgramiv(self.compute_program.id, GL_COMPUTE_WORK_GROUP_SIZE, lsize)

        w = self.size().width()
        h = self.size().height()
        ngroups = (
            int((w + lsize[0] - 1) / lsize[0]),
            int((h + lsize[1] - 1) / lsize[1]),
            1,
        )
        self.compute_program.dispatch(*ngroups)

        # The compute pass writes to an image that will be sampled as a texture;
        # post a barrier to make those writes visible to the draw pass.
        Barrier.image_to_texture()

        # ---- draw pass ----
        self.program.use()
        self.program.set_i("u_Texture", 0)
        self.tex.bind_to_unit(0)

        self.vao.bind()
        glDrawArrays(GL_TRIANGLE_FAN, 0, 4)

    def resizeGL(self, w: int, h: int) -> None:
        self.makeCurrent()
        if self.tex is not None:
            self.tex.delete()
        self.tex = Texture2D(w, h, internalformat=GL_RGBA32F)
        self.tex.bind_image(0, level=0, access=GL_WRITE_ONLY)
        glViewport(0, 0, w, h)
        if not self.size_changed:
            self.panX = w * 0.75
            self.panY = h * 0.5
            self.scale = 2.0 / float(h)
            self.size_changed = True

    # ------------------------------------------------------------- interaction

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.lastPos = event.position()
        self.centerPos = QPoint(
            int(self.lastPos.x()), self.height() - int(self.lastPos.y())
        )

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        deltaX = event.position().x() - self.lastPos.x()
        deltaY = event.position().y() - self.lastPos.y()
        button = event.buttons()
        if button & Qt.MouseButton.RightButton:
            self.zoom(float(deltaY / 2))
        elif button & Qt.MouseButton.LeftButton:
            self.panX += deltaX
            self.panY -= deltaY
        self.lastPos = event.position()

    def zoom(self, delta: float) -> None:
        cx = self.scale * (self.centerPos.x() - self.panX)
        cy = self.scale * (self.centerPos.y() - self.panY)
        self.scale *= pow(1.01, delta)
        self.panX = (self.scale * self.centerPos.x() - cx) / self.scale
        self.panY = (self.scale * self.centerPos.y() - cy) / self.scale

    def wheelEvent(self, event: QWheelEvent) -> None:
        pos = event.position()
        self.centerPos = QPoint(int(pos.x()), self.height() - int(pos.y()))
        delta = event.angleDelta().y()
        if delta != 0:
            self.zoom(-float(delta) / 30.0)

    def closeEvent(self, event: QCloseEvent) -> None:
        self.makeCurrent()
        self.vao.delete()
        self.program.delete()
        self.compute_program.delete()
        if self.tex is not None:
            self.tex.delete()
            self.tex = None
        return super().closeEvent(event)
