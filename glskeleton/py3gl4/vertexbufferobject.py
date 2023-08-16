# refer to https://registry.khronos.org/OpenGL/specs/gl/glspec46.core.pdf
from ctypes import c_uint

from OpenGL.GL import glCreateBuffers, glBindBuffer, GL_ARRAY_BUFFER, \
    glNamedBufferStorage, GL_DYNAMIC_STORAGE_BIT, glIsBuffer, glDeleteBuffers
import numpy as np


class VertexBufferObject:
    def __init__(self, data: np.ndarray=None) -> None:
        self.vbo_id = c_uint()
        glCreateBuffers(1, self.vbo_id)
        if data is not None:
            self.setData(data)

    def bind(self) -> None:
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_id)

    def unbind(self) -> None:
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def delete(self) -> None:
        if glIsBuffer(self.vbo_id):
            glDeleteBuffers(1, self.vbo_id)

    def setData(self, data: np.ndarray, flags: int = GL_DYNAMIC_STORAGE_BIT) -> None:
        glNamedBufferStorage(self.vbo_id, data.nbytes, data, flags)
