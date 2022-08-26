# refer to https://www.khronos.org/opengl/wiki/Shader
from OpenGL import GL


class Shader(object):
    def __init__(self, type: GL.Constant, source: str) -> None:
        self.type: GL.Constant = type
        self.shaderObject: GL.GLuint = GL.glCreateShader(type)
        if self.shaderObject == 0:
            raise ValueError(
                "glCreateShader failed to create an empty shader object")
        if source is not None:
            GL.glShaderSource(self.shaderObject, source)
            GL.glCompileShader(self.shaderObject)
            result = GL.glGetShaderiv(self.shaderObject, GL.GL_COMPILE_STATUS)
            if not result:
                error = GL.glGetShaderInfoLog(self.shaderObject)
                # free resources
                GL.glDeleteShader(self.shaderObject)
                raise RuntimeError(
                    "glCompileShader failed to compile (%s): %s", result, error)
        else:
            raise ValueError("Shader source is empty")


class VertexShader(Shader):
    def __init__(self, source: str) -> None:
        super().__init__(GL.GL_VERTEX_SHADER, source)


class TessellationControlShader(Shader):
    def __init__(self, source: str) -> None:
        super().__init__(GL.GL_TESS_CONTROL_SHADER, source)


class TessellationEvaluationShader(Shader):
    def __init__(self, source: str) -> None:
        super().__init__(GL.GL_TESS_EVALUATION_SHADER, source)


class GeometryShader(Shader):
    def __init__(self, source: str) -> None:
        super().__init__(GL.GL_GEOMETRY_SHADER, source)


class FragmentShader(Shader):
    def __init__(self, source: str) -> None:
        super().__init__(GL.GL_FRAGMENT_SHADER, source)


class ComputeShader(Shader):
    def __init__(self, source: str) -> None:
        super().__init__(GL.GL_COMPUTE_SHADER, source)
