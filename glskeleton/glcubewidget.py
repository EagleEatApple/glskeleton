# refer to https://github.com/totex/PyOpenGL_season_02/blob/master/video_15_framebuffer_objects_p1.py

import sys
import time

import numpy as np
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtCore import QTimerEvent
from PySide6.QtGui import QCloseEvent, QSurfaceFormat
from OpenGL.GL import *
import glm

from py3gl4.program import Program
from py3gl4.shader import VertexShader, FragmentShader
from py3gl4.vertexarrayobject import VertexArrayObject, VertexAttribute
from py3gl4.vertexbufferobject import VertexBufferObject
from py3gl4.elementbufferobject import ElementBufferObject
from py3gl4.uniform import Uniform
from py3gl4.texture import Texture2D
from py3gl4.framebuffer import Framebuffer
from py3gl4.renderbuffer import Renderbuffer
from baseapp import BaseApplication


vertex_shader_code = """
#version 460 core
in layout(location = 0) vec3 position;
in layout(location = 1) vec2 textCoords;
uniform mat4 vp;
uniform mat4 model;
out vec2 outText;
void main()
{
    gl_Position =  vp * model * vec4(position, 1.0f);
    outText = textCoords;
}
"""

fragment_shader_code = """
#version 460 core
in vec2 outText;
out vec4 outColor;
uniform sampler2D renderedTexture;
void main()
{
    outColor = texture(renderedTexture, outText);
}
"""


class GLCubeWidget(QOpenGLWidget):
    def __init__(self) -> None:
        super().__init__()
        self.startTimer(20)
        self.cube_positions = [
            (1.0, 1.0, 0.0), (0.0, 0.0, 0.0), (2.0, 0.0, 0.0)]
        self.plane_position = glm.translate(
            glm.mat4(1.0), glm.vec3(-3.0, 1.0, 0.0))

    def timerEvent(self, event: QTimerEvent) -> None:
        self.update()

    def initializeGL(self) -> None:
        self.elapsedTime = 0.0
        self.last_time = time.time()
        self.aspect = float(self.size().width()) / self.size().height()

        # initialize opengl pipeline
        vertex_shader = VertexShader(vertex_shader_code)
        fragment_shader = FragmentShader(fragment_shader_code)
        self.program = Program([vertex_shader, fragment_shader])
        self.program.addUniform(Uniform("vp", GL_FLOAT_MAT4))
        self.program.addUniform(Uniform("model", GL_FLOAT_MAT4))
        vertex_shader.delete()
        fragment_shader.delete

        # initialize vao, vbo
        cube = np.array([
            -0.5, -0.5,  0.5, 0.0, 0.0,
            0.5, -0.5,  0.5, 1.0, 0.0,
            0.5,  0.5,  0.5, 1.0, 1.0,
            -0.5,  0.5,  0.5, 0.0, 1.0,
            -0.5, -0.5, -0.5, 0.0, 0.0,
            0.5, -0.5, -0.5, 1.0, 0.0,
            0.5,  0.5, -0.5, 1.0, 1.0,
            -0.5,  0.5, -0.5, 0.0, 1.0,
            0.5, -0.5, -0.5, 0.0, 0.0,
            0.5,  0.5, -0.5, 1.0, 0.0,
            0.5,  0.5,  0.5, 1.0, 1.0,
            0.5, -0.5,  0.5, 0.0, 1.0,
            -0.5,  0.5, -0.5, 0.0, 0.0,
            -0.5, -0.5, -0.5, 1.0, 0.0,
            -0.5, -0.5,  0.5, 1.0, 1.0,
            -0.5,  0.5,  0.5, 0.0, 1.0,
            -0.5, -0.5, -0.5, 0.0, 0.0,
            0.5, -0.5, -0.5, 1.0, 0.0,
            0.5, -0.5,  0.5, 1.0, 1.0,
            -0.5, -0.5,  0.5, 0.0, 1.0,
            0.5, 0.5, -0.5,  0.0, 0.0,
            -0.5, 0.5, -0.5,  1.0, 0.0,
            -0.5, 0.5,  0.5,  1.0, 1.0,
            0.5, 0.5,  0.5,  0.0, 1.0
        ], dtype=GLfloat)

        self.cube_indices = np.array([
            0,  1,  2,  2,  3,  0,
            4,  5,  6,  6,  7,  4,
            8,  9, 10, 10, 11,  8,
            12, 13, 14, 14, 15, 12,
            16, 17, 18, 18, 19, 16,
            20, 21, 22, 22, 23, 20
        ], dtype=GLuint)

        plane = np.array([
            -0.5, -0.5, 0.0, 0.0, 0.0,
            2.0, -0.5, 0.0, 1.0, 0.0,
            2.0,  1.0, 0.0, 1.0, 1.0,
            -0.5,  1.0, 0.0, 0.0, 1.0
        ], dtype=GLfloat)

        self.plane_indices = np.array([
            0, 1, 2, 2, 3, 0
        ], dtype=GLuint)

        attribute_position = VertexAttribute(
            "position", 0, 3, GL_FLOAT, False, 0)
        attribute_textCoords = VertexAttribute(
            "textCoords", 1, 2, GL_FLOAT, False, 3 * sizeof(GLfloat))

        self.cube_vao = VertexArrayObject()
        self.cube_vbo = VertexBufferObject(cube)
        self.cube_ebo = ElementBufferObject(self.cube_indices)
        self.cube_vao.setVertexBuffer(self.cube_vbo, 0, 0, 5 * sizeof(GLfloat))
        self.cube_vao.setVertexAttribute(0, attribute_position)
        self.cube_vao.setVertexAttribute(0, attribute_textCoords)
        self.cube_vao.setElementBuffer(self.cube_ebo)
        self.cube_tex = Texture2D(file_path="textures/crate.jpg")

        self.plane_vao = VertexArrayObject()
        self.plane_vbo = VertexBufferObject(plane)
        self.plane_ebo = ElementBufferObject(self.plane_indices)
        self.plane_vao.setVertexBuffer(
            self.plane_vbo, 0, 0, 5 * sizeof(GLfloat))
        self.plane_vao.setVertexAttribute(0, attribute_position)
        self.plane_vao.setVertexAttribute(0, attribute_textCoords)
        self.plane_vao.setElementBuffer(self.plane_ebo)
        self.plane_tex = Texture2D(1, GL_RGBA8, self.width(), self.height())
        self.plane_tex.SetFiltering(GL_LINEAR, GL_LINEAR)
        self.plane_tex.setWrapMode(GL_REPEAT, GL_REPEAT)
        self.rbo = Renderbuffer(GL_DEPTH24_STENCIL8, self.width(), self.height())
        self.fbo = Framebuffer()
        self.fbo.attachTexture2D(GL_COLOR_ATTACHMENT0, self.plane_tex, 0)
        self.fbo.attachRenderbuffer(
            GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, self.rbo)

        self.view = glm.translate(glm.mat4(1.0), glm.vec3(0.0, 0.0, -5.0))

    def drawCube(self) -> None:
        self.cube_vao.bind()
        self.cube_tex.bind(0)
        for i in range(len(self.cube_positions)):
            model = glm.translate(
                glm.mat4(1.0), glm.vec3(self.cube_positions[i]))
            if i == 0:
                pos = self.cube_positions[i]
                pos = glm.rotateY(pos, -self.elapsedTime * 2)
                model = glm.translate(glm.mat4(1.0), pos)
                model = glm.rotate(model, -self.elapsedTime *
                                   2, glm.vec3(0.0, 1.0, 0.0))
                self.program.uniforms["model"].setMat4(glm.value_ptr(model))
            elif i == 1:
                self.program.uniforms["model"].setMat4(glm.value_ptr(model))
            else:
                self.program.uniforms["model"].setMat4(glm.value_ptr(model))
            glDrawElements(GL_TRIANGLES, len(
                self.cube_indices), GL_UNSIGNED_INT, None)
        self.cube_vao.unbind()
        self.cube_tex.unbind(0)

    def paintGL(self) -> None:
        self.deltaTime = time.time() - self.last_time
        self.elapsedTime += self.deltaTime
        self.last_time = time.time()

        self.program.use()
        self.projection = glm.perspective(
            glm.radians(45.0), self.aspect, 0.1, 100.0)
        self.vp = self.projection * self.view
        self.program.uniforms["vp"].setMat4(glm.value_ptr(self.vp))

        # draw the cube to the texture in the custom frame buffer
        self.fbo.bind()
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)
        self.drawCube()

        # now, back to draw to the default frame buffer
        glBindFramebuffer(GL_FRAMEBUFFER, self.defaultFramebufferObject())

        # draw the plane on the screend, the contents of the plane are from the texture of above frame buffer
        glClearColor(0.9, 0.9, 0.9, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.plane_tex.bind(0)
        self.plane_vao.bind()
        self.program.uniforms["model"].setMat4(
            glm.value_ptr(self.plane_position))
        glDrawElements(GL_TRIANGLES, len(
            self.plane_indices), GL_UNSIGNED_INT, None)
        self.plane_vao.unbind()
        self.plane_tex.unbind(0)

        # draw the cube on the screend
        self.drawCube()

    def resizeGL(self, w: int, h: int) -> None:
        self.makeCurrent()
        self.aspect = float(w) / h
        glViewport(0, 0, w, h)

    def closeEvent(self, event: QCloseEvent) -> None:
        self.makeCurrent()
        self.program.delete()
        self.cube_vao.delete()
        self.cube_ebo.delete()
        self.cube_vbo.delete()
        self.cube_tex.delete()
        self.plane_vao.delete()
        self.plane_vbo.delete()
        self.plane_ebo.delete()
        self.plane_tex.delete()
        self.rbo.delete()
        self.fbo.delete()
        return super().closeEvent(event)


def test() -> None:
    """Run GLWidget test"""
    app = BaseApplication(sys.argv)
    widget = GLCubeWidget()
    widget.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    test()
