# Ensure PySide6 and PyOpenGL had been installed
try:
    from PySide6.QtWidgets import QApplication
except ImportError:
    print("PySide6 must be installed to run this application!")
    print("Please run:\npip install PySide6")
from PySide6.QtGui import QSurfaceFormat, QOffscreenSurface, QOpenGLContext
try:
    from OpenGL.GL import *
except ImportError:
    print("PyOpenGL must be installed to run this application!")
    print("Please run:\npip install PyOpenGL PyOpenGL_accelerate")

from opengl_info import OpenGLInfo

class BaseApplication(QApplication):
    def __init__(self, argv: list[str], bufferSize: int = 24, samples: int = 4, major: int = 4, minor: int = 3) -> None:
        super().__init__(argv)
        # get supported opengl information from current OS
        surface = QOffscreenSurface()
        surface.create()
        context = QOpenGLContext()
        context.create()
        context.makeCurrent(surface)
        info = OpenGLInfo()
        self.system_info = info.opengl_info
        context.doneCurrent()
        del context
        del surface

        # initialize OpenGL profile, support OpenGL 4.3 by default on Windows and Linux
        self.format = QSurfaceFormat()
        self.format.setDepthBufferSize(bufferSize)
        self.format.setSamples(samples)
        # if OS is macOS, must setup OpenGL core profile is 4.1
        if info.os_name == "Darwin":
            self.format.setVersion(4, 1)
        else:
            self.format.setVersion(major, minor)
        self.format.setProfile(QSurfaceFormat.CoreProfile)
        QSurfaceFormat.setDefaultFormat(self.format)
