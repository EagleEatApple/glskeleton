# refer to https://www.khronos.org/opengl/wiki/Uniform_(GLSL)

from OpenGL.GL import *
import numpy as np


class Uniform:
    def __init__(self, name: str, type: GLenum):
        self.name = name
        self.location = 0
        self.type = type

    def setLocation(self, program_name:int):
        location = glGetUniformLocation(program_name, self.name)
        self.location = location

    def setBool(self, value: bool) -> None:
        glUniform1i(self.location, value)

    def setInt(self, value: int) -> None:
        glUniform1i(self.location, value)

    def setIVec2(self, x: int, y: int) -> None:
        glUniform2i(self.location, x, y)

    def setIVec3(self, x: int, y: int, z: int) -> None:
        glUniform3i(self.location, x, y, z)

    def setIVec4(self, x: int, y: int, z: int, w: int) -> None:
        glUniform4i(self.location, x, y, z, w)

    def setFloat(self, value: float) -> None:
        glUniform1f(self.location, value)

    def setVec2(self, x: float, y: float) -> None:
        glUniform2f(self.location, x, y)

    def setVec3(self, x: float, y: float, z: float) -> None:
        glUniform3f(self.location, x, y, z)

    def setVec4(self, x: float, y: float, z: float, w: float) -> None:
        glUniform4f(self.location, x, y, z, w)

    def setMat2(self, mat: np.ndarray):
        glUniformMatrix2fv(self.location, 1, GL_FALSE, mat)

    def setMat3(self, mat: np.ndarray):
        glUniformMatrix3fv(self.location, 1, GL_FALSE, mat)

    def setMat4(self, mat: np.ndarray):
        glUniformMatrix4fv(self.location, 1, GL_FALSE, mat)

    def setDMat3(self, mat: np.ndarray):
        glUniformMatrix3dv(self.location, 1, GL_FALSE, mat)
