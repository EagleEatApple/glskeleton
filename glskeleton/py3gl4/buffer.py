# refer to https://www.khronos.org/opengl/wiki/Buffer_Object


from OpenGL.GL import glGenBuffers, glBindBuffer, glBufferData, \
    GLenum, GL_STATIC_DRAW,GL_ARRAY_BUFFER, glDeleteBuffers, GL_ELEMENT_ARRAY_BUFFER
import numpy as np

from py3gl4.object import OpenGLObject

# general buffer object
class BufferObject(OpenGLObject):
    def __init__(self, target: GLenum, usage: GLenum) -> None:
        self.name  = glGenBuffers(1)
        self.target = target
        self.usage = usage
 
    def bind(self) -> None:
        glBindBuffer(self.target, self.name)
    
    def setData(self, data:np.ndarray)-> None:
        glBufferData(self.target, data.nbytes, data, self.usage)
    
    def unbind(self) -> None:
        glBindBuffer(self.target, 0)
    
    def delete(self)-> None:
        glDeleteBuffers(1, self.name)

# vertex buffer object - VBO
class VertexBufferObject(BufferObject):
    def __init__(self, usage=GL_STATIC_DRAW) -> None:
        super().__init__(GL_ARRAY_BUFFER, usage)

# element array buffer object - EBO
class ElementBufferObject(BufferObject):
    def __init__(self, usage=GL_STATIC_DRAW) -> None:
        super().__init__(GL_ELEMENT_ARRAY_BUFFER, usage)


