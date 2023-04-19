import sys
import math

from numpy import array, dot, eye, float64, ndarray, zeros, float32, uint32
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtCore import QTimerEvent
import OpenGL.GL as GL

from baseapp import BaseApplication
from py3gl4.shader import *
from py3gl4.program import Program, Uniform, VertexAttribute
from py3gl4.vertexarrayobject import VertexArrayObject
from py3gl4.buffer import VertexBufferObject, ElementBufferObject


# draw a cube on the screen
# adapt from https://github.com/pygame/pygame/blob/main/examples/glcube.py


class Rotation:
    """
    Data class that stores rotation angles in three axes.
    """

    def __init__(self) -> None:
        self.theta: float = 20.0
        self.phi: float = 40.0
        self.psi: float = 25.0


# implement tessellation
class GLCubeWidget(QOpenGLWidget):
    def __init__(self) -> None:
        super().__init__()
        self.startTimer(20)

    def translate(self, matrix: ndarray, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> ndarray:
        """
        Translate (move) a matrix in the x, y and z axes.
        :param matrix: Matrix to translate.
        :param x: direction and magnitude to translate in x axis. Defaults to 0.
        :param y: direction and magnitude to translate in y axis. Defaults to 0.
        :param z: direction and magnitude to translate in z axis. Defaults to 0.
        :return: The translated matrix.
        """
        translation_matrix = array(
            [
                [1.0, 0.0, 0.0, x],
                [0.0, 1.0, 0.0, y],
                [0.0, 0.0, 1.0, z],
                [0.0, 0.0, 0.0, 1.0],
            ],
            dtype=matrix.dtype,
        ).T
        matrix[...] = dot(matrix, translation_matrix)
        return matrix

    def frustum(self, left: float, right: float, bottom: float, top: float, znear: float, zfar: float) -> ndarray:
        """
        Build a perspective matrix from the clipping planes, or camera 'frustrum'
        volume.
        :param left: left position of the near clipping plane.
        :param right: right position of the near clipping plane.
        :param bottom: bottom position of the near clipping plane.
        :param top: top position of the near clipping plane.
        :param znear: z depth of the near clipping plane.
        :param zfar: z depth of the far clipping plane.
        :return: A perspective matrix.
        """
        perspective_matrix = zeros((4, 4), dtype=float32)
        perspective_matrix[0, 0] = +2.0 * znear / (right - left)
        perspective_matrix[2, 0] = (right + left) / (right - left)
        perspective_matrix[1, 1] = +2.0 * znear / (top - bottom)
        perspective_matrix[3, 1] = (top + bottom) / (top - bottom)
        perspective_matrix[2, 2] = -(zfar + znear) / (zfar - znear)
        perspective_matrix[3, 2] = -2.0 * znear * zfar / (zfar - znear)
        perspective_matrix[2, 3] = -1.0
        return perspective_matrix

    def perspective(self, fovy: float, aspect: float, znear: float, zfar: float) -> ndarray:
        """
        Build a perspective matrix from field of view, aspect ratio and depth
        planes.
        :param fovy: the field of view angle in the y axis.
        :param aspect: aspect ratio of our view port.
        :param znear: z depth of the near clipping plane.
        :param zfar: z depth of the far clipping plane.
        :return: A perspective matrix.
        """
        h = math.tan(fovy / 360.0 * math.pi) * znear
        w = h * aspect
        return self.frustum(-w, w, -h, h, znear, zfar)

    def rotate(self, matrix: ndarray, angle: float, x: float, y: float, z: float) -> ndarray:
        """
        Rotate a matrix around an axis.
        :param matrix: The matrix to rotate.
        :param angle: The angle to rotate by.
        :param x: x of axis to rotate around.
        :param y: y of axis to rotate around.
        :param z: z of axis to rotate around.
        :return: The rotated matrix
        """
        angle = math.pi * angle / 180
        c, s = math.cos(angle), math.sin(angle)
        n = math.sqrt(x * x + y * y + z * z)
        x, y, z = x / n, y / n, z / n
        cx, cy, cz = (1 - c) * x, (1 - c) * y, (1 - c) * z
        rotation_matrix = array(
            [
                [cx * x + c, cy * x - z * s, cz * x + y * s, 0],
                [cx * y + z * s, cy * y + c, cz * y - x * s, 0],
                [cx * z - y * s, cy * z + x * s, cz * z + c, 0],
                [0, 0, 0, 1],
            ],
            dtype=matrix.dtype,
        ).T
        matrix[...] = dot(matrix, rotation_matrix)
        return matrix

    def timerEvent(self, event: QTimerEvent) -> None:
        self.update()

    def initializeGL(self) -> None:
        self.rotation = Rotation()

        """
        Initialise open GL in the 'modern' open GL style for open GL versions
        greater than 3.1.
        :param display_size: Size of the window/viewport.
        """
        # Create shaders
        # --------------------------------------
        vertex_code = """
        #version 430 core
        uniform mat4   model;
        uniform mat4   view;
        uniform mat4   projection;
        uniform vec4   colour_mul;
        uniform vec4   colour_add;
        layout(location = 0)in vec3 vertex_position;
        layout(location = 1)in vec4 vertex_colour;         // vertex colour in

        out vec4   vertex_color_out;            // vertex colour out
        void main()
        {
            vertex_color_out = (colour_mul * vertex_colour) + colour_add;
            gl_Position = projection * view * model * vec4(vertex_position, 1.0);
        }
        """
        fragment_code = """
        #version 430 core
        in vec4 vertex_color_out;  // vertex colour from vertex shader
        out vec4 fragColor;
        void main()
        {
            fragColor = vertex_color_out;
        }
        """
        vertex = VertexShader(vertex_code)
        fragment = FragmentShader(fragment_code)
        self.program = Program([vertex, fragment])

        # Create vertex buffers and shader constants
        # ------------------------------------------
        # Cube Data
        vertices = zeros(
            8, [("vertex_position", float32, 3), ("vertex_colour", float32, 4)]
        )
        vertices["vertex_position"] = [
            [1, 1, 1],
            [-1, 1, 1],
            [-1, -1, 1],
            [1, -1, 1],
            [1, -1, -1],
            [1, 1, -1],
            [-1, 1, -1],
            [-1, -1, -1],
        ]
        vertices["vertex_colour"] = [
            [0, 1, 1, 1],
            [0, 0, 1, 1],
            [0, 0, 0, 1],
            [0, 1, 0, 1],
            [1, 1, 0, 1],
            [1, 1, 1, 1],
            [1, 0, 1, 1],
            [1, 0, 0, 1],
        ]
        self.filled_cube_indices = array(
            [0, 1, 2, 0, 2, 3, 0, 3, 4, 0, 4, 5, 0, 5, 6,
                0, 6, 1, 1, 6, 7, 1, 7, 2, 7, 4, 3, 7,
                3, 2, 4, 7, 6, 4, 6, 5],
            dtype=uint32,
        )
        self.outline_cube_indices = array(
            [0, 1, 1, 2, 2, 3, 3, 0, 4, 7, 7, 6, 6,
                5, 5, 4, 0, 5, 1, 6, 2, 7, 3, 4],
            dtype=uint32,
        )

        # setup vertex attributes and uniforms based on shader code
        stride = vertices.strides[0]
        offset = 0
        self.program.addVertexAttribute(VertexAttribute(
            "vertex_position", 0, 3, GL.GL_FLOAT, False, stride, offset))
        offset = vertices.dtype["vertex_position"].itemsize
        self.program.addVertexAttribute(VertexAttribute(
            "vertex_colour", 1, 3, GL.GL_FLOAT, False, stride, offset))
        self.program.addUniform(Uniform("model", GL.GL_FLOAT_MAT4))
        self.program.addUniform(Uniform("view",  GL.GL_FLOAT_MAT4))
        self.program.addUniform(Uniform("projection", GL.GL_FLOAT_MAT4))
        self.program.addUniform(Uniform("colour_mul",GL.GL_FLOAT_VEC4))
        self.program.addUniform(Uniform("colour_add", GL.GL_FLOAT_VEC4))

        self.vao = VertexArrayObject()
        vertices_buffer = VertexBufferObject()
        self.vao.setVBOVertexAttributes(vertices_buffer, vertices, self.program)
        self.filled_buffer = ElementBufferObject()
        self.filled_buffer.bind()
        self.filled_buffer.setData(self.filled_cube_indices)
        self.outline_buffer = ElementBufferObject()
        self.outline_buffer.bind()
        self.outline_buffer.setData(self.outline_cube_indices)

        # Set GL drawing data
        # -------------------
        GL.glClearColor(0, 0, 0, 0)
        GL.glPolygonOffset(1, 1)
        GL.glEnable(GL.GL_LINE_SMOOTH)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        GL.glDepthFunc(GL.GL_LESS)
        GL.glHint(GL.GL_LINE_SMOOTH_HINT, GL.GL_NICEST)
        GL.glLineWidth(1.0)

    def paintGL(self) -> None:
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        GL.glEnable(GL.GL_DEPTH_TEST)
        self.program.use()
        
        view = self.translate(eye(4), z=-6)
        self.program.uniforms["view"].setMat4(view)
        projection = self.perspective(
            45.0, self.width() / float(self.height()), 2.0, 300.0)
        self.program.uniforms["projection"].setMat4(projection)

        # Rotate cube
        self.rotation.theta += 1.0  # degrees
        self.rotation.phi += 1.0  # degrees
        self.rotation.psi += 1.0  # degrees
        model = eye(4, dtype=float32)
        self.rotate(model, self.rotation.theta, 0, 0, 1)
        self.rotate(model, self.rotation.phi, 0, 1, 0)
        self.rotate(model, self.rotation.psi, 1, 0, 0)
        self.program.uniforms["model"].setMat4(model)

        self.vao.bind()
        # Filled cube
        GL.glEnable(GL.GL_POLYGON_OFFSET_FILL)
        GL.glDisable(GL.GL_BLEND)
        self.program.uniforms["colour_mul"].setVec4(1, 1, 1, 1)
        self.program.uniforms["colour_add"].setVec4(0, 0, 0, 0.0)
        self.filled_buffer.bind()
        GL.glDrawElements(GL.GL_TRIANGLES, len(
            self.filled_cube_indices), GL.GL_UNSIGNED_INT, None)

        # Outlined cube
        GL.glDisable(GL.GL_POLYGON_OFFSET_FILL)
        GL.glEnable(GL.GL_BLEND)
        self.program.uniforms["colour_mul"].setVec4(0, 0, 0, 0.0)
        self.program.uniforms["colour_add"].setVec4(1, 1, 1, 1.0)
        self.outline_buffer.bind()
        GL.glDrawElements(GL.GL_LINES, len(
            self.outline_cube_indices), GL.GL_UNSIGNED_INT, None)
        self.vao.unbind()


def test() -> None:
    """Run GLWidget test"""
    app = BaseApplication(sys.argv)
    widget = GLCubeWidget()
    widget.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    test()
