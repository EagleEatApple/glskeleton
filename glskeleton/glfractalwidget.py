import sys

import numpy as np
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtCore import QTimerEvent
from OpenGL.GL import *

from baseapp import BaseApplication
from py3gl4.shader import VertexShader, FragmentShader
from py3gl4.program import Program, Uniform, VertexAttribute
from py3gl4.vertexarrayobject import VertexArrayObject
from py3gl4.buffer import VertexBufferObject



# implement fractal - mandelbrot set
# atapt from https://github.com/denisenkom/mandelbrot-pyopengl/blob/master/mandelbrot.py
class GLFractalWidget(QOpenGLWidget):

    vs_source = """
    #version 430 core
    layout(location = 0) in vec3 vertexPosition_modelspace;
    out vec2 fragmentCoord;
    void main(){
        gl_Position = vec4(vertexPosition_modelspace, 1);
        fragmentCoord = vec2(vertexPosition_modelspace.x, vertexPosition_modelspace.y);
    }
    """

    fs_source = """
    #version 430 core
    in vec2 fragmentCoord;
    out vec3 color;
    uniform dmat3 transform;
    uniform int max_iters = 1000;
    vec3 hsv2rgb(vec3 c)
    {
        vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
        vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
        return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
    }
    vec3 map_color(int i, float r, float c) {
        float di = i;
        float zn = sqrt(r + c);
        float hue = (di + 1 - log(log2(abs(zn))))/max_iters;
        return hsv2rgb(vec3(hue, 0.8, 1));
    }
    void main(){
        dvec3 pointCoord = dvec3(fragmentCoord.xy, 1);
        pointCoord *= transform;
        double cx = pointCoord.x;
        double cy = pointCoord.y;
        int iter = 0;
        double zx = 0;
        double zy = 0;
        while (iter < max_iters) {
            double nzx = zx * zx - zy * zy + cx;
            double nzy = 2 * zx * zy + cy;
            zx = nzx;
            zy = nzy;
            if (zx*zx + zy*zy > 4.0) {
                break;
            }
            iter += 1;
        }
        if (iter == max_iters) {
            color = vec3(0,0,0);
        } else {
            color = map_color(iter, float(zx*zx), float(zy*zy));
        }
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self.startTimer(20)
        self.program = None

    def timerEvent(self, event: QTimerEvent) -> None:
        self.update()

    def initializeGL(self) -> None:
        self.aspect = 1.0 * self.width() / self.height()
        vertex_shader = VertexShader(GLFractalWidget.vs_source)
        fragment_shader = FragmentShader(GLFractalWidget.fs_source)
        self.program = Program([vertex_shader, fragment_shader])

        # setup vertex attributes and uniforms based on shader code
        self.program.addVertexAttribute(VertexAttribute("vertexPosition_modelspace", 0, 3, GL_DOUBLE, GL_FALSE, 0, 0))
        self.program.addUniform(Uniform('transform', GL_DOUBLE_MAT3))
        self.program.addUniform(Uniform('max_iters', GL_INT))

        self.vert_values = np.array([-1, -1 * self.aspect, 0,
                                     1, -1 * self.aspect, 0,
                                     -1, 1 * self.aspect, 0,
                                     -1, 1 * self.aspect, 0,
                                     1, -1 * self.aspect, 0,
                                     1, 1 * self.aspect, 0,
                                     ], dtype='float64')

        # creating vertex array
        self.vao = VertexArrayObject()
        vbo = VertexBufferObject()
        self.vao.setVBOVertexAttributes(vbo,self.vert_values, self.program)
        self.state = {
            'zoom': 1,
            'pos_x': -0.7600189058857209,
            'pos_y': 0.0799516080512771,
            'max_iters': 100,
        }

    def paintGL(self) -> None:
        glClearColor(0, 0, 0, 0)
        glClear(GL_COLOR_BUFFER_BIT)
        self.program.use()

        zoom = self.state['zoom']
        pos_x = self.state['pos_x']
        pos_y = self.state['pos_y']
        self.program.uniforms['transform'].setDMat3(np.array([self.aspect * zoom, 0, pos_x, 0, 1 * zoom, pos_y, 0, 0, 1 * zoom], dtype='float64'))
        iters = int(self.state['max_iters'])
        self.program.uniforms['max_iters'].setInt(iters)

        self.vao.bind()
        glDrawArrays(GL_TRIANGLES, 0, int(len(self.vert_values) / 3))
        self.vao.unbind()

    def resizeGL(self, width: int, height: int) -> None:
        self.aspect = 1.0 * self.width() / self.height()
        self.update()


def test():
    """Run GLWidget test"""
    app = BaseApplication(sys.argv)
    widget = GLFractalWidget()
    widget.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    test()
