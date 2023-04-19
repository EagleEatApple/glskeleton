# refer to https://www.khronos.org/opengl/wiki/Shader
# https://www.khronos.org/opengl/wiki/Shader_Compilation
import platform

from OpenGL.GL import GLenum, glCreateShader, glShaderSource, \
    glCompileShader, glGetShaderiv, glGetShaderInfoLog, glDeleteShader, \
    GL_VERTEX_SHADER, GL_FRAGMENT_SHADER, GL_COMPILE_STATUS, \
    GL_TESS_CONTROL_SHADER, GL_TESS_EVALUATION_SHADER, GL_GEOMETRY_SHADER, \
    GL_COMPUTE_SHADER, GLuint

from py3gl4.object import OpenGLObject

class Shader(OpenGLObject):
    def __init__(self, type: GLenum, source: str) -> None:
        self.type = type
        self.name:GLuint = glCreateShader(type)
        if self.name == 0:
            raise ValueError(
                "glCreateShader failed to create an empty shader object")
        if source is not None:
            glShaderSource(self.name, source)
            glCompileShader(self.name)
            result = glGetShaderiv(self.name, GL_COMPILE_STATUS)
            if not result:
                error = glGetShaderInfoLog(self.name)
                # free resources
                glDeleteShader(self.name)
                raise RuntimeError(
                    "glCompileShader failed to compile (%s): %s", result, error)
        else:
            raise ValueError("Shader source is empty")

    def __del__(self):
        if self.name != 0:
            glDeleteShader(self.name)
            self.name = 0


class VertexShader(Shader):
    def __init__(self, source: str) -> None:
        super().__init__(GL_VERTEX_SHADER, source)

# refer to https://www.khronos.org/opengl/wiki/Tessellation
# Tessellation control shader and Tessellation evaluation shader are indtroduced in in OpenGL 4.0
class TessellationControlShader(Shader):
    def __init__(self, source: str) -> None:
        super().__init__(GL_TESS_CONTROL_SHADER, source)


class TessellationEvaluationShader(Shader):
    def __init__(self, source: str) -> None:
        super().__init__(GL_TESS_EVALUATION_SHADER, source)

class GeometryShader(Shader):
    def __init__(self, source: str) -> None:
        super().__init__(GL_GEOMETRY_SHADER, source)

class FragmentShader(Shader):
    def __init__(self, source: str) -> None:
        super().__init__(GL_FRAGMENT_SHADER, source)

# refert to https://www.khronos.org/opengl/wiki/Compute_Shader
# Compute Shader is introduced in OpenGL 4.3, and macOS only supports OpenGL 4.1
# https://support.apple.com/en-us/HT202823
class ComputeShader(Shader):
    def __init__(self, source: str) -> None:
        super().__init__(GL_COMPUTE_SHADER, source)
        os = platform.system()
        if os == "Darwin":
            raise RuntimeError("Can't run compute shader on macOS!")


