# refer to https://registry.khronos.org/OpenGL/specs/gl/glspec46.core.pdf
# Vertex array objects are container objects including references to buffer objects
from ctypes import c_uint

from OpenGL.GL import glCreateVertexArrays, glBindVertexArray, glDeleteVertexArrays, \
    glVertexArrayElementBuffer, glVertexArrayVertexBuffer, glEnableVertexArrayAttrib, \
    glVertexArrayAttribFormat, glVertexArrayAttribBinding, glIsVertexArray

from py3gl4.vertexbufferobject import VertexBufferObject
from py3gl4.elementbufferobject import ElementBufferObject


class VertexAttribute:
    def __init__(self, name: str, index: int, size: int, type: int, normalized: bool, offset: int) -> None:
        self.name = name
        self.index = index
        self.size = size
        self.type = type
        self.normalized = normalized
        self.offset = offset


class VertexArrayObject:
    def __init__(self) -> None:
        self.vao_id = c_uint()
        glCreateVertexArrays(1, self.vao_id)

    def bind(self) -> None:
        glBindVertexArray(self.vao_id)

    def unbind(self) -> None:
        glBindVertexArray(0)

    def delete(self) -> None:
        if glIsVertexArray(self.vao_id):
            glDeleteVertexArrays(1, self.vao_id)

    def setElementBuffer(self, buffer: ElementBufferObject) -> None:
        glVertexArrayElementBuffer(self.vao_id, buffer.ebo_id)

    def setVertexBuffer(self, buffer: VertexBufferObject, bindingindex: int, offset: int, stride: int) -> None:
        glVertexArrayVertexBuffer(
            self.vao_id, bindingindex, buffer.vbo_id, offset, stride)

    def setVertexAttribute(self, bindingindex: int, attrib: VertexAttribute) -> None:
        glEnableVertexArrayAttrib(self.vao_id, attrib.index)
        glVertexArrayAttribFormat(
            self.vao_id, attrib.index, attrib.size, attrib.type, attrib.normalized, attrib.offset)
        glVertexArrayAttribBinding(self.vao_id, attrib.index, bindingindex)
