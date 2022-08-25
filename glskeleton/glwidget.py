import sys

import numpy as np
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtCore import QTimerEvent
from OpenGL.GL import *

from baseapp import BaseApplication


# implement tessellation
# refer to OpenGL SuperBible Chapter 3
# the original source code from:
# https://github.com/openglsuperbible/sb7code/blob/master/src/tessellatedtri/tessellatedtri.cpp
class GLWidget(QOpenGLWidget):

    vs_source = """
    #version 410 core
    void main(void)
    {
        const vec4 vertices[] = vec4[](vec4(0.25, -0.25, 0.5, 1.0),
                                        vec4(-0.25, -0.25, 0.5, 1.0),
                                        vec4(0.25, 0.25, 0.5, 1.0));
        gl_Position = vertices[gl_VertexID];
    }
    """

    tcs_source = """
    #version 410 core
    layout(vertices = 3) out;
    void main(void)
    {
        if (gl_InvocationID == 0)
        {
            gl_TessLevelInner[0] = 5.0;
            gl_TessLevelOuter[0] = 5.0;
            gl_TessLevelOuter[1] = 5.0;
            gl_TessLevelOuter[2] = 5.0;
        }
        gl_out[gl_InvocationID].gl_Position = gl_in[gl_InvocationID].gl_Position;
    }
    """

    tes_source = """
    #version 410 core
    layout(triangles, equal_spacing, cw) in;
    void main(void)
    {
        gl_Position = (gl_TessCoord.x * gl_in[0].gl_Position +
                        gl_TessCoord.y * gl_in[1].gl_Position +
                        gl_TessCoord.z * gl_in[2].gl_Position);
    }
    """

    fs_source = """
    #version 410 core
    out vec4 color;
    void main(void)
    {
        color = vec4(0.0, 0.8, 1.0, 1.0);
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self.startTimer(20)
        self.program = None

    def timerEvent(self, event: QTimerEvent) -> None:
        self.update()

    def initializeGL(self) -> None:
        self.program = glCreateProgram()
        vs = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(vs, GLWidget.vs_source)
        glCompileShader(vs)

        tcs = glCreateShader(GL_TESS_CONTROL_SHADER)
        glShaderSource(tcs, GLWidget.tcs_source)
        glCompileShader(tcs)

        tes = glCreateShader(GL_TESS_EVALUATION_SHADER)
        glShaderSource(tes, GLWidget.tes_source)
        glCompileShader(tes)

        fs = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(fs, GLWidget.fs_source)
        glCompileShader(fs)

        glAttachShader(self.program, vs)
        glAttachShader(self.program, tcs)
        glAttachShader(self.program, tes)
        glAttachShader(self.program, fs)

        glLinkProgram(self.program)

        vao = glGenVertexArrays(1)
        glBindVertexArray(vao)

        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

    def paintGL(self) -> None:
        green = np.array([0.0, 0.25, 0.0, 1.0], 'f')
        glClearBufferfv(GL_COLOR, 0, green)

        glUseProgram(self.program)
        glDrawArrays(GL_PATCHES, 0, 3)


def test() -> None:
    """Run GLWidget test"""
    app = BaseApplication(sys.argv)
    widget = GLWidget()
    widget.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    test()
