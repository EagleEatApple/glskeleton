from OpenGL import GL

from shader import *


class Program(object):
    def __init__(self, shaders: list[Shader]) -> None:
        self.programObject: GL.GLuint = GL.glCreateProgram()
        if self.programObject == 0:
            raise ValueError(
                "glCreateProgram failed to create an empty  program object")

        for shader in shaders:
            GL.glAttachShader(self.programObject, shader.shaderObject)

        GL.glLinkProgram(self.programObject)
        result = GL.glGetProgramiv(self.programObject, GL.GL_LINK_STATUS)
        if not result:
            error = GL.glGetProgramInfoLog(self.programObject)
            # free resources
            GL.glDeleteProgram(self.programObject)
            raise RuntimeError(
                "glLinkProgram failed to link (%s): %s", result, error)
        # free resources
        for shader in shaders:
            GL.glDeleteShader(shader.shaderObject)

    def useProgram(self) -> None:
        GL.glUseProgram(self.programObject)
