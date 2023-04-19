import platform

from OpenGL.GL import glGetString, GL_VERSION, GL_RENDERER, GL_VENDOR, GL_SHADING_LANGUAGE_VERSION, glGetInteger, GL_MAJOR_VERSION, GL_MINOR_VERSION


class OpenGLInfo(object):
    def __init__(self) -> None:
        # platform.system() return "Linux", "Darwin", "Windows" etc.
        os = platform.system()
        if os == "Linux":
            self.os_name = "Linux family"
        elif os == "Darwin":
            self.os_name = "Apple macOS"
        elif os == "Windows":
            self.os_name = "Microsoft Windows"
        self.getOpenGLInformation()

    def getOpenGLInformation(self) -> None:
        version = glGetString(GL_VERSION)
        renderer = glGetString(GL_RENDERER)
        vendor = glGetString(GL_VENDOR)
        glsl_version = glGetString(GL_SHADING_LANGUAGE_VERSION)
        major = glGetInteger(GL_MAJOR_VERSION)
        minor = glGetInteger(GL_MINOR_VERSION)
        self.opengl_info = (f"Current OS is: {self.os_name}\n"
                            f"OpenGL Version : {version}\n"
                            f"Major is : {major}, minor is : {minor}\n"
                            f"Renderer : {renderer}\n"
                            f"Vendor: {vendor}\n"
                            f"GLSL Version : {glsl_version}\n")
