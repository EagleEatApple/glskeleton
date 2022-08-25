from OpenGL.GL import *


class OpenGLTools(object):

    def __init__(self) -> None:
        self.version = glGetString(GL_VERSION)
        self.renderer = glGetString(GL_RENDERER)
        self.vendor = glGetString(GL_VENDOR)
        self.glsl_version = glGetString(GL_SHADING_LANGUAGE_VERSION)
        self.major = glGetInteger(GL_MAJOR_VERSION)
        self.minor = glGetInteger(GL_MINOR_VERSION)
        self.numOfExtensions = glGetInteger(GL_NUM_EXTENSIONS)
        self.extensions = []
        for i in range(self.numOfExtensions):
            self.extensions.append(glGetStringi(GL_EXTENSIONS, i))
        self.gl_information = (f"OpenGL Version : {self.version}\n"
                               f"Major is : {self.major}, minor is : {self.minor}\n"
                               f"Renderer : {self.renderer}\n"
                               f"Vendor: {self.vendor}\n"
                               f"GLSL Version : {self.glsl_version}\n")
