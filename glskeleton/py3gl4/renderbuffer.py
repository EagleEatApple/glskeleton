# refer to https://registry.khronos.org/OpenGL/specs/gl/glspec46.core.pdf
from ctypes import c_uint, c_int

from OpenGL.GL import glCreateRenderbuffers, glBindRenderbuffer, \
    GL_RENDERBUFFER, glNamedRenderbufferStorage, glDeleteRenderbuffers, glIsRenderbuffer


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
