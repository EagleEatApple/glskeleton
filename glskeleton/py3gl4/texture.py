# refer to https://registry.khronos.org/OpenGL/specs/gl/glspec46.core.pdf
from ctypes import c_uint, c_int
from pathlib import Path

from OpenGL.GL import glCreateTextures, glBindTextureUnit, glDeleteTextures, glIsTexture, \
    GL_TEXTURE_2D, glTextureStorage2D, glTextureParameteri, GL_TEXTURE_MIN_FILTER, \
    GL_TEXTURE_MAG_FILTER, GL_TEXTURE_WRAP_S, GL_TEXTURE_WRAP_T, glBindImageTexture, \
    GL_FALSE, GL_RGBA32F, GL_RED, GL_RGB, GL_RGBA, GL_LINEAR, GL_NEAREST, GL_REPEAT, \
    glTextureSubImage2D, GL_UNSIGNED_BYTE, glGenerateTextureMipmap, GL_R32F, GL_RGB32F
from PIL import Image


class Texture:
    def __init__(self, target: c_uint) -> None:
        self.tex_id = c_uint()
        glCreateTextures(target, 1, self.tex_id)

    def bind(self, index: c_uint) -> None:
        glBindTextureUnit(index, self.tex_id)

    def unbind(self, index: c_uint) -> None:
        glBindTextureUnit(index, 0)

    def delete(self) -> None:
        if glIsTexture(self.tex_id):
            glDeleteTextures(1, self.tex_id)

    def SetFiltering(self, min_filter: c_int, mag_filter: c_int) -> None:
        glTextureParameteri(self.tex_id, GL_TEXTURE_MIN_FILTER, min_filter)
        glTextureParameteri(self.tex_id, GL_TEXTURE_MAG_FILTER, mag_filter)


class Texture2D(Texture):
    def __init__(self, level: c_int=1, internalFormat: c_int=GL_RGBA32F, width: c_uint=1, height: c_uint=1, file_path:str=None) -> None:
        super().__init__(GL_TEXTURE_2D)
        if file_path is None:
            self.internalFormat = internalFormat
            glTextureStorage2D(self.tex_id, level, internalFormat, width, height)
        else:
            filename = Path(file_path)
            # image = Image.open(filename).transpose(Image.FLIP_TOP_BOTTOM)
            image = Image.open(filename)
            if image is not None:
                self.bind(0)
                width, height = image.size
                mode = image.mode
                image = image.tobytes("raw", mode, 0, -1)
                if mode == "L":
                    self.pixelFormat = GL_RED
                    self.internalFormat = GL_R32F
                elif mode == "RGB":
                    self.pixelFormat = GL_RGB
                    self.internalFormat = GL_RGB32F
                elif mode == "RGBA":
                    self.pixelFormat = GL_RGBA
                    self.internalFormat = GL_RGBA32F
                else:
                    self.pixelFormat = GL_RGBA
                    self.internalFormat = GL_RGBA32F
                glTextureStorage2D(self.tex_id, 1, self.internalFormat, width, height)
                self.SetFiltering(GL_LINEAR, GL_NEAREST)
                self.setWrapMode(GL_REPEAT, GL_REPEAT)
                glTextureSubImage2D(self.tex_id, 0, 0, 0, width, height, self.pixelFormat, GL_UNSIGNED_BYTE, image)
                # glGenerateTextureMipmap(self.tex_id)
                self.unbind(0)

    def setWrapMode(self, wrap_s: c_int, wrap_t: c_int) -> None:
        glTextureParameteri(self.tex_id, GL_TEXTURE_WRAP_S, wrap_s)
        glTextureParameteri(self.tex_id, GL_TEXTURE_WRAP_T, wrap_t)

    def bingImage(self, index: c_uint, level: c_int, access: c_uint) -> None:
        glBindImageTexture(index, self.tex_id, level,
                           GL_FALSE, 0, access, self.internalFormat)
