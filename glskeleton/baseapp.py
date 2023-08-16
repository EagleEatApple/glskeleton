import platform as localOS

# Ensure PySide6 and PyOpenGL had been installed
try:
    from PySide6.QtWidgets import QApplication
except ImportError:
    print("PySide6 must be installed to run this application!")
    print("Please run:\npip install PySide6")
from PySide6.QtGui import QSurfaceFormat, QOffscreenSurface, QOpenGLContext
try:
    from OpenGL.GL import glGetString, GL_VERSION, GL_RENDERER, GL_VENDOR, GL_SHADING_LANGUAGE_VERSION, glGetInteger, GL_MAJOR_VERSION, GL_MINOR_VERSION
except ImportError:
    print("PyOpenGL must be installed to run this application!")
    print("Please run:\npip install PyOpenGL PyOpenGL_accelerate")


class BaseApplication(QApplication):
    def __init__(self, argv: list[str], bufferSize: int = 24, samples: int = 4, major: int = 4, minor: int = 6) -> None:
        super().__init__(argv)
        # get supported opengl information from current OS
        surface = QOffscreenSurface()
        surface.create()
        context = QOpenGLContext()
        context.create()
        context.makeCurrent(surface)
        self.getOpenGLInformation()
        context.doneCurrent()
        del context
        del surface

        # initialize OpenGL profile, support OpenGL 4.6 by default on Windows and Linux
        self.format = QSurfaceFormat()
        self.format.setDepthBufferSize(bufferSize)
        self.format.setSamples(samples)
        self.format.setVersion(major, minor)
        self.format.setProfile(QSurfaceFormat.CoreProfile)
        QSurfaceFormat.setDefaultFormat(self.format)

    def getOpenGLInformation(self) -> None:
        # platform.system() return "Linux", "Darwin", "Windows" etc.
        os = localOS.system()
        if os == "Linux":
            self.os_name = "Linux family"
        elif os == "Windows":
            self.os_name = "Microsoft Windows"
        version = glGetString(GL_VERSION).decode()
        renderer = glGetString(GL_RENDERER).decode()
        vendor = glGetString(GL_VENDOR).decode()
        glsl_version = glGetString(GL_SHADING_LANGUAGE_VERSION).decode()
        major = glGetInteger(GL_MAJOR_VERSION)
        minor = glGetInteger(GL_MINOR_VERSION)
        self.opengl_info = (f"Current OS is: {self.os_name}\n"
                            f"OpenGL Version : {version}\n"
                            f"Major is : {major}, minor is : {minor}\n"
                            f"Renderer : {renderer}\n"
                            f"Vendor: {vendor}\n"
                            f"GLSL Version : {glsl_version}\n")
