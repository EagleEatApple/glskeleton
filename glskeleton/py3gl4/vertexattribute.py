# refer to https://www.khronos.org/opengl/wiki/Vertex_Specification#Vertex_Array_Object

from ctypes import c_void_p

from OpenGL.GL import glEnableVertexAttribArray, glDisableVertexAttribArray, glVertexAttribPointer


class VertexAttribute:
    def __init__(self, name: str, index: int, size: int, type: int, normalized: bool, stride: int, offset: int) -> None:
        self.name = name
        self.index = index
        self.type = type
        self.size = size
        self.normalized = normalized
        self.stride = stride
        self.offset = offset

    def enable(self) -> None:
        glEnableVertexAttribArray(self.index)
        glVertexAttribPointer(
            self.index, self.size, self.type, self.normalized, self.stride, c_void_p(self.offset))

    def disable(self) -> None:
        glDisableVertexAttribArray(self.index)
