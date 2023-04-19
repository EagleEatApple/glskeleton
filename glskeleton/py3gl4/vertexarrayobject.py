# refer to https://www.khronos.org/opengl/wiki/OpenGL_Object
# https://www.khronos.org/opengl/wiki/Vertex_Specification#Vertex_Array_Object
# Vertex array objects are container objects including 
# references to buffer objects

from OpenGL.GL import glGenVertexArrays, glBindVertexArray, glDeleteVertexArrays
import numpy as np

from py3gl4.object import OpenGLObject
from py3gl4.program import Program
from py3gl4.buffer import VertexBufferObject, ElementBufferObject

# vertex array object - VAO
class VertexArrayObject(OpenGLObject):
    def __init__(self) -> None:
        self.name  = glGenVertexArrays(1)
        self.vbo = None
        self.ebo = None

    def bind(self) -> None:
        glBindVertexArray(self.name)

    def unbind(self) -> None:
        glBindVertexArray(0)

    def delete(self)-> None:
        glDeleteVertexArrays(1, self.name)

    #def setVBOVertexAttributes(self, vbo:VertexBufferObject, vertices:np.ndarray, attributes:list[VertexAttribute]):
    def setVBOVertexAttributes(self, vbo:VertexBufferObject, vertices:np.ndarray, program:Program):
        if len(program.attributes) > 0:
            self.vbo = vbo
            self.bind()
            vbo.bind()
            vbo.setData(vertices)
            for attribute in program.attributes.values():
                attribute.enable()
            self.unbind()
        else:
            raise RuntimeError("Please add a few vertex attributes!")

