# refer to https://registry.khronos.org/OpenGL/specs/gl/glspec46.core.pdf
from ctypes import c_int, c_uint

from OpenGL.GL import (
    GL_RENDERBUFFER,
    glBindRenderbuffer,
    glCreateRenderbuffers,
    glDeleteRenderbuffers,
    glIsRenderbuffer,
    glNamedRenderbufferStorage,
)


class Renderbuffer:
    def __init__(self, internalFormat: c_int, width: c_uint, height: c_uint) -> None:
        self.rbo_id = c_uint()
        self.internalFormat = internalFormat
        glCreateRenderbuffers(1, self.rbo_id)
        glNamedRenderbufferStorage(self.rbo_id, internalFormat, width, height)

    def bind(self) -> None:
        glBindRenderbuffer(GL_RENDERBUFFER, self.rbo_id)

    def unbind(self) -> None:
        glBindRenderbuffer(GL_RENDERBUFFER, 0)

    def delete(self) -> None:
        if glIsRenderbuffer(self.rbo_id):
            glDeleteRenderbuffers(1, self.rbo_id)
