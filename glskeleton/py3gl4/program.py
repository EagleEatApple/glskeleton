# refert to https://www.khronos.org/opengl/wiki/GLSL_Object#Program_objects
# refer to https://www.khronos.org/opengl/wiki/Shader_Compilation

from OpenGL.GL import glCreateProgram, glAttachShader, glLinkProgram, \
    glGetProgramiv, glGetProgramInfoLog, glDeleteProgram, glUseProgram, \
    GL_LINK_STATUS

from py3gl4.shader import Shader
from py3gl4.vertexarrayobject import VertexAttribute
from py3gl4.uniform import Uniform


class Program:
    def __init__(self, shaders: list[Shader]) -> None:
        self.program_id = glCreateProgram()
        self.attributes: dict[str, VertexAttribute] = {}
        self.uniforms: dict[str, Uniform] = {}
        if self.program_id == 0:
            raise ValueError(
                "glCreateProgram failed to create a valid  program object")
        for shader in shaders:
            glAttachShader(self.program_id, shader.shader_id)
        glLinkProgram(self.program_id)
        result = glGetProgramiv(self.program_id, GL_LINK_STATUS)
        if not result:
            error = glGetProgramInfoLog(self.program_id)
            # free resources
            self.delete()
            raise RuntimeError(
                "glLinkProgram failed to link (%s): %s", result, error)

    def use(self) -> None:
        glUseProgram(self.program_id)

    def addVertexAttribute(self, attribute: VertexAttribute) -> None:
        self.attributes[attribute.name] = attribute

    def addUniform(self, uniform: Uniform) -> None:
        uniform.getLocation(self.program_id)
        self.uniforms[uniform.name] = uniform

    def delete(self) -> None:
        if self.program_id > -1:
            glDeleteProgram(self.program_id)

