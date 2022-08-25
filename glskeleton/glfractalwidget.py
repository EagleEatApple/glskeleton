import sys

import numpy as np
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtCore import QTimerEvent
from OpenGL.GL import *

from baseapp import BaseApplication


# implement fractal - mandelbrot set
# atapt from https://github.com/denisenkom/mandelbrot-pyopengl/blob/master/mandelbrot.py
class GLFractalWidget(QOpenGLWidget):

    vs_source = """
    #version 410 core
    layout(location = 0) in vec3 vertexPosition_modelspace;
    out vec2 fragmentCoord;
    void main(){
        gl_Position = vec4(vertexPosition_modelspace, 1);
        fragmentCoord = vec2(vertexPosition_modelspace.x, vertexPosition_modelspace.y);
    }
    """

    fs_source = """
    #version 410 core
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

    def make_shader(self, shader_type: Constant, src: str) -> GLuint:
        shader = glCreateShader(shader_type)
        glShaderSource(shader, src)
        glCompileShader(shader)
        status = glGetShaderiv(shader, GL_COMPILE_STATUS)
        if status == GL_FALSE:
            strInfoLog = glGetShaderInfoLog(shader).decode('ascii')
            strShaderType = ""
            if shader_type is GL_VERTEX_SHADER:
                strShaderType = "vertex"
            elif shader_type is GL_GEOMETRY_SHADER:
                strShaderType = "geometry"
            elif shader_type is GL_FRAGMENT_SHADER:
                strShaderType = "fragment"
            raise Exception("Compilation failure for " +
                            strShaderType + " shader:\n" + strInfoLog)
        return shader

    def make_program(self, shader_list: list) -> GLuint:
        program = glCreateProgram()
        for shader in shader_list:
            glAttachShader(program, shader)
        glLinkProgram(program)
        status = glGetProgramiv(program, GL_LINK_STATUS)
        if status == GL_FALSE:
            strInfoLog = glGetProgramInfoLog(program)
            raise Exception("Linker failure: \n" + strInfoLog)
        for shader in shader_list:
            glDetachShader(program, shader)
        return program

    def __init__(self) -> None:
        super().__init__()
        self.startTimer(20)
        self.program = None

    def timerEvent(self, event: QTimerEvent) -> None:
        self.update()

    def initializeGL(self) -> None:
        self.aspect = 1.0 * self.width() / self.height()
        vertex_shader = self.make_shader(
            GL_VERTEX_SHADER, GLFractalWidget.vs_source)
        fragment_shader = self.make_shader(
            GL_FRAGMENT_SHADER, GLFractalWidget.fs_source)
        program = self.make_program([vertex_shader, fragment_shader])
        self.vert_values = np.array([-1, -1 * self.aspect, 0,
                                     1, -1 * self.aspect, 0,
                                     -1, 1 * self.aspect, 0,
                                     -1, 1 * self.aspect, 0,
                                     1, -1 * self.aspect, 0,
                                     1, 1 * self.aspect, 0,
                                     ], dtype='float64')

        # creating vertex array
        vert_array = glGenVertexArrays(1)
        glBindVertexArray(vert_array)

        vert_buffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vert_buffer)
        glBufferData(GL_ARRAY_BUFFER, self.vert_values, GL_STATIC_DRAW)

        glClearColor(0, 0, 0, 0)
        glClear(GL_COLOR_BUFFER_BIT)
        glUseProgram(program)

        # setup coordinate buffer
        glEnableVertexAttribArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, vert_buffer)
        glVertexAttribPointer(0, 3, GL_DOUBLE, GL_FALSE, 0, None)

        # setup uniforms for fragment shader
        self.transform_loc = glGetUniformLocation(program, 'transform')
        self.max_iters_loc = glGetUniformLocation(program, 'max_iters')

        self.state = {
            'zoom': 1,
            'pos_x': -0.7600189058857209,
            'pos_y': 0.0799516080512771,
            'max_iters': 100,
        }

    def paintGL(self) -> None:
        zoom = self.state['zoom']
        pos_x = self.state['pos_x']
        pos_y = self.state['pos_y']
        glUniformMatrix3dv(self.transform_loc, 1, False,
                           np.array([self.aspect * zoom, 0, pos_x, 0, 1 * zoom, pos_y, 0, 0, 1 * zoom], dtype='float64'))
        glUniform1i(self.max_iters_loc, int(self.state['max_iters']))
        glDrawArrays(GL_TRIANGLES, 0, int(len(self.vert_values) / 3))

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
