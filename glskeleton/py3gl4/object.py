# refert to https://www.khronos.org/opengl/wiki/OpenGL_Object
# An object name is always a GLuint. They can be any 32-bit unsigned integer
# except 0. The object number 0 is reserved for special use cases

from OpenGL.GL import GLuint


class OpenGLObject:
    def __init__(self) -> None:
        self.name: GLuint = 0
