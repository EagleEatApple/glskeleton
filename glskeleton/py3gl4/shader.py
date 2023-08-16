# refer to https://www.khronos.org/opengl/wiki/Shader
# https://www.khronos.org/opengl/wiki/Shader_Compilation
import platform
from ctypes import c_uint

from OpenGL.GL import glCreateShader, glShaderSource, \
    glCompileShader, glGetShaderiv, glGetShaderInfoLog, glDeleteShader, \
    GL_VERTEX_SHADER, GL_FRAGMENT_SHADER, GL_COMPILE_STATUS, \
    GL_TESS_CONTROL_SHADER, GL_TESS_EVALUATION_SHADER, GL_GEOMETRY_SHADER, \
    GL_COMPUTE_SHADER


class Shader:
    def __init__(self, type: c_uint, source: str=None, file_path:str = None) -> None:
        self.type = type
        self.shader_id = glCreateShader(type)
        if self.shader_id == 0:
            raise ValueError(
                "glCreateShader failed to create a valid shader object")
        if source is not None:
            self.createShader(source)
        if file_path is not None:
            file = open(file_path)
            content = file.read()
            file.close()
            self.createShader(content)

    def delete(self)-> None:
        if self.shader_id > -1:
            glDeleteShader(self.shader_id)

    def createShader(self, source:str)->None:
        glShaderSource(self.shader_id, source)
        glCompileShader(self.shader_id)
        result = glGetShaderiv(self.shader_id, GL_COMPILE_STATUS)
        if not result:
            error = glGetShaderInfoLog(self.shader_id)
            # free resources
            self.delete()
            raise RuntimeError(
                "glCompileShader failed to compile (%s): %s", result, error)

class VertexShader(Shader):
    def __init__(self, source: str=None, file_path:str = None) -> None:
        super().__init__(GL_VERTEX_SHADER, source, file_path)

# refer to https://www.khronos.org/opengl/wiki/Tessellation
# Tessellation control shader and Tessellation evaluation shader are indtroduced in in OpenGL 4.0


class TessellationControlShader(Shader):
    def __init__(self, source: str=None, file_path:str = None) -> None:
        super().__init__(GL_TESS_CONTROL_SHADER, source, file_path)


class TessellationEvaluationShader(Shader):
    def __init__(self, source: str=None, file_path:str = None) -> None:
        super().__init__(GL_TESS_EVALUATION_SHADER, source, file_path)


class GeometryShader(Shader):
    def __init__(self, source: str=None, file_path:str = None) -> None:
        super().__init__(GL_GEOMETRY_SHADER, source, file_path)


class FragmentShader(Shader):
    def __init__(self, source: str=None, file_path:str = None) -> None:
        super().__init__(GL_FRAGMENT_SHADER, source, file_path)

# refert to https://www.khronos.org/opengl/wiki/Compute_Shader
# Compute Shader is introduced in OpenGL 4.3, and macOS only supports OpenGL 4.1
# https://support.apple.com/en-us/HT202823


class ComputeShader(Shader):
    def __init__(self, source: str=None, file_path:str = None) -> None:
        super().__init__(GL_COMPUTE_SHADER, source, file_path)
        os = platform.system()
        if os == "Darwin":
            raise RuntimeError("Can't run compute shader on macOS!")
