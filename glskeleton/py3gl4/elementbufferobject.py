# refer to https://registry.khronos.org/OpenGL/specs/gl/glspec46.core.pdf
from ctypes import c_uint

import numpy as np
from OpenGL.GL import (
    GL_DYNAMIC_STORAGE_BIT,
    GL_ELEMENT_ARRAY_BUFFER,
    glBindBuffer,
    glCreateBuffers,
    glDeleteBuffers,
    glIsBuffer,
    glNamedBufferStorage,
)


class ElementBufferObject:
    def __init__(self, data: np.ndarray=None) -> None:
        self.ebo_id = c_uint()
        glCreateBuffers(1, self.ebo_id)
        if data is not None:
            self.setData(data)

    def bind(self) -> None:
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo_id)

    def unbind(self) -> None:
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

    def delete(self) -> None:
        if glIsBuffer(self.ebo_id):
            glDeleteBuffers(1, self.ebo_id)

    def setData(self, data: np.ndarray, flags: int = GL_DYNAMIC_STORAGE_BIT) -> None:
        glNamedBufferStorage(self.ebo_id, data.nbytes, data, flags)
