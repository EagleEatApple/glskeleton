### `2023-08-16`

Refactory py3gl4 to only support OpenGL 4.6, and includes major OpenGL objects
```python
class Program:
class class VertexShader(Shader):
class TessellationControlShader(Shader):
class TessellationEvaluationShader(Shader):
class GeometryShader(Shader):
class FragmentShader(Shader):
class ComputeShader(Shader):
class VertexArrayObject:
class VertexBufferObject:
class ElementBufferObject:
class Texture2D(Texture):
class Framebuffer:
class Renderbuffer:
```
Update 3 demos


### `2023-04-19`

Refactory the code by extracting more OpenGL classes.
```python
class BufferObject(OpenGLObject):
    def __init__(self, target: GLenum, usage: GLenum) -> None:
        self.name  = glGenBuffers(1)
        self.target = target
        self.usage = usage
		......

class VertexArrayObject(OpenGLObject):
    def __init__(self) -> None:
        self.name  = glGenVertexArrays(1)
        self.vbo = None
        self.ebo = None
		......		
```

### `2022-08-26`

Refactory the code by extracting Shader and Program classes.
```python
class Shader(object):
    def __init__(self, type: GL.Constant, source: str) -> None:
        self.type: GL.Constant = type
        self.shaderObject: GL.GLuint = GL.glCreateShader(type)
		......

class Program(object):
    def __init__(self, shaders: list[Shader]) -> None:
        self.programObject: GL.GLuint = GL.glCreateProgram()
		......		
```		

### `2022-08-25`

Implement dockable tree/tab view, and provide 3 demos:
- Rotating colorful cube
- Simple tessellation
- Mandelbrot fractal


### `2022-08-08`

Change images used by icons, all of images come from [iconfinder](https://www.iconfinder.com/).
Modify the code to use modern OpenGL, now it's using OpenGL 4.0 by default.
You're able to change the OpenGL version in baseapp.py:
```python
class BaseApplication(QApplication):
	def __init__(self, argv, bufferSize=24, samples=4, major=4, minor=0):
		super().__init__(argv)
		# initialize OpenGL profile, support OpenGL 4.0 by default
		self.format = QSurfaceFormat()
		self.format.setDepthBufferSize(bufferSize)
		self.format.setSamples(samples)
		self.format.setVersion(major, minor)
		self.format.setProfile(QSurfaceFormat.CoreProfile)
		QSurfaceFormat.setDefaultFormat(self.format)
```

Add About Dialog to show OpenGL information
![screenshot](./screenshot/aboutdialog.png)


### `2021-01-03`

Upload the code at first time.