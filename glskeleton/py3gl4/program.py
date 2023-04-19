# refert to https://www.khronos.org/opengl/wiki/GLSL_Object#Program_objects
# refer to https://www.khronos.org/opengl/wiki/Shader_Compilation

from OpenGL.GL import glCreateProgram, glAttachShader, glLinkProgram, \
    glGetProgramiv, glGetProgramInfoLog, glDeleteProgram, glDeleteShader, \
    glUseProgram, GL_LINK_STATUS, GL_ACTIVE_UNIFORMS, glGetActiveUniform

from py3gl4.object import OpenGLObject
from py3gl4.shader import Shader
from py3gl4.vertexattribute import VertexAttribute
from py3gl4.uniform import Uniform


class Program(OpenGLObject):
    def __init__(self, shaders: list[Shader]) -> None:
        self.name = glCreateProgram()
        self.attributes:dict[str, VertexAttribute] = {}
        self.uniforms:dict[str, Uniform] = {}
        if self.name == 0:
            raise ValueError(
                "glCreateProgram failed to create an empty  program object")

        for shader in shaders:
            glAttachShader(self.name, shader.name)

        glLinkProgram(self.name)
        result = glGetProgramiv(self.name, GL_LINK_STATUS)
        if not result:
            error = glGetProgramInfoLog(self.name)
            # free resources
            glDeleteProgram(self.name)
            raise RuntimeError(
                "glLinkProgram failed to link (%s): %s", result, error)
        # free resources
        for shader in shaders:
            glDeleteShader(shader.name)

    def use(self) -> None:
        glUseProgram(self.name)

    def addVertexAttribute(self, attribute:VertexAttribute):
        self.attributes[attribute.name] = attribute

    def addUniform(self, uniform:Uniform):
        uniform.setLocation(self.name)
        self.uniforms[uniform.name] = uniform

