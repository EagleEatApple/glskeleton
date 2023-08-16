# refer to https://github.com/denisenkom/mandelbrot-pyopengl/
# refer to https://github.com/jakubcerveny/gl-compute
import sys

import numpy as np
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtCore import QTimerEvent, QPoint, Qt
from PySide6.QtGui import QCloseEvent, QSurfaceFormat, QMouseEvent, QWheelEvent
from OpenGL.GL import *
import imgui

from py3gl4.program import Program
from py3gl4.shader import VertexShader, FragmentShader, ComputeShader
from py3gl4.vertexarrayobject import VertexArrayObject
from py3gl4.texture import Texture2D
from qtimgui.pyside6 import PySide6Renderer
from baseapp import BaseApplication


class GLFractalWidget(QOpenGLWidget):
    def __init__(self) -> None:
        super().__init__()
        self.startTimer(20)
        self.tex = None
        self.size_changed = False
        self.scale = 0.0
        self.panX = 0.0
        self.panY = 0.0
        self.lastPos = QPoint()
        self.centerPos = QPoint()
        self.max_iter = 100

    def timerEvent(self, event: QTimerEvent) -> None:
        self.update()

    def initializeGL(self) -> None:
        # initialize opengl pipeline
        vertex_shader = VertexShader(None, "shaders/fractal.vert")
        fragment_shader = FragmentShader(None, "shaders/fractal.frag")
        self.program = Program([vertex_shader, fragment_shader])
        vertex_shader.delete()
        fragment_shader.delete()

        compute_shader = ComputeShader(None, "shaders/fractal.comp")
        self.compute_program = Program([compute_shader])
        compute_shader.delete()

        # initialize vao
        self.vao = VertexArrayObject()

        # initialize imgui
        imgui.create_context()
        self.impl = PySide6Renderer(self)

    def paintGL(self) -> None:
        self.compute_program.use()
        loc = glGetUniformLocation(self.compute_program.program_id, "center")
        glUniform2f(loc, self.panX, self.panY)
        loc = glGetUniformLocation(self.compute_program.program_id, "scale")
        glUniform1f(loc, self.scale)
        loc = glGetUniformLocation(self.compute_program.program_id, "max_iter")
        glUniform1i(loc, self.max_iter)
        lsize = np.zeros(3, dtype=np.int32)
        glGetProgramiv(self.compute_program.program_id,
                       GL_COMPUTE_WORK_GROUP_SIZE, lsize)
        ngroups = [0] * 3
        ngroups[0] = int((self.width() + lsize[0]-1) / lsize[0])
        ngroups[1] = int((self.height() + lsize[1]-1) / lsize[1])
        ngroups[2] = 1
        glDispatchCompute(ngroups[0], ngroups[1], ngroups[2])
        glMemoryBarrier(GL_SHADER_IMAGE_ACCESS_BARRIER_BIT)

        self.program.use()
        loc = glGetUniformLocation(self.program.program_id, "u_Texture")
        glUniform1i(loc, 0)
        self.tex.bind(0)

        self.vao.bind()
        glDrawArrays(GL_TRIANGLE_FAN, 0, 4)

        # define imgui elements
        self.impl.process_inputs()
        imgui.new_frame()

        imgui.set_next_window_position(1, 1, condition=imgui.FIRST_USE_EVER)
        imgui.set_next_window_size(500, 180, condition=imgui.FIRST_USE_EVER)
        imgui.begin("Settings")

        imgui.text("Press the left mouse button and move to pan")
        imgui.text("Press the right mouse button and move to zoom")
        imgui.text("Use the mouse wheel to zoom")
        changed, iter = imgui.slider_int(
            "Maximum Iterations", self.max_iter, 50, 1000)
        self.max_iter = iter
        imgui.end()

        # render imgui
        imgui.render()
        self.impl.render(imgui.get_draw_data())

    def resizeGL(self, w: int, h: int) -> None:
        self.makeCurrent()
        if self.tex is not None:
            self.tex.delete()
        self.tex = Texture2D(1, GL_RGBA32F, w, h)
        self.tex.bingImage(0, 0, GL_WRITE_ONLY)
        glViewport(0, 0, w, h)
        if not self.size_changed:
            self.panX = w * 0.75
            self.panY = h * 0.5
            self.scale = 2.0 / float(h)
            self.size_changed = True

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.lastPos = event.position()
        self.centerPos = QPoint(
            self.lastPos.x(), self.height() - self.lastPos.y())

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if imgui.is_any_item_active():
            return

        deltaX = event.position().x() - self.lastPos.x()
        deltaY = event.position().y() - self.lastPos.y()
        button = event.buttons()
        if button & Qt.RightButton:
            self.zoom(float(deltaY/2))
        elif button & Qt.LeftButton:
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
        self.centerPos = QPoint(event.pixelDelta().x(),
                                self.height() - event.pixelDelta().y())
        self.zoom(-float(event.angleDelta().y()) / 30.0)

    def closeEvent(self, event: QCloseEvent) -> None:
        self.makeCurrent()
        self.vao.delete()
        self.program.delete()
        self.compute_program.delete()
        if self.tex is not None:
            self.tex.delete()
        return super().closeEvent(event)


def test():
    """Run GLWidget test"""
    app = BaseApplication(sys.argv)
    widget = GLFractalWidget()
    widget.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    test()
