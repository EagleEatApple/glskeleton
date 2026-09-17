# refer to https://registry.khronos.org/OpenGL/specs/gl/glspec46.core.pdf
from ctypes import c_int, c_uint

from OpenGL.GL import (
    GL_FRAMEBUFFER,
    glBindFramebuffer,
    glCreateFramebuffers,
    glDeleteFramebuffers,
    glIsFramebuffer,
    glNamedFramebufferRenderbuffer,
    glNamedFramebufferTexture,
)

from .renderbuffer import Renderbuffer
from .texture import Texture2D


class Framebuffer:
    def __init__(self) -> None:
        self.fbo_id = c_uint()
        glCreateFramebuffers(1, self.fbo_id)

    def bind(self) -> None:
        glBindFramebuffer(GL_FRAMEBUFFER, self.fbo_id)

    def unbind(self) -> None:
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def delete(self) -> None:
        if glIsFramebuffer(self.fbo_id):
            glDeleteFramebuffers(1, self.fbo_id)

    def attachTexture2D(self, attachment: c_uint, texture: Texture2D,	level: c_int) -> None:
        glNamedFramebufferTexture(
            self.fbo_id, attachment, texture.tex_id, level)

    def attachRenderbuffer(self, attachment: c_uint, renderbuffertarget:c_uint, renderbuffer: Renderbuffer) -> None:
        glNamedFramebufferRenderbuffer(self.fbo_id, attachment, renderbuffertarget, renderbuffer.rbo_id)
