# refer to https://github.com/totex/PyOpenGL_season_02/blob/master/video_15_framebuffer_objects_p1.py

from __future__ import annotations

import time
from pathlib import Path

import numpy as np
from gl46.buffer import Buffer
from gl46.framebuffer import Framebuffer
from gl46.gl import get_gl
from gl46.program import Program
from gl46.shader import Shader, ShaderStage
from gl46.texture import Texture2D
from gl46.vertexarray import VertexArray, VertexAttrib
from OpenGL.GL import (
    GL_COLOR_BUFFER_BIT,
    GL_DEPTH_BUFFER_BIT,
    GL_DEPTH_COMPONENT32F,
    GL_DEPTH_TEST,
    GL_FLOAT,
    GL_FRAMEBUFFER,
    GL_LINEAR,
    GL_NEAREST,
    GL_REPEAT,
    GL_RGB,
    GL_RGBA8,
    GL_SRGB8_ALPHA8,
    GL_TEXTURE_MAG_FILTER,
    GL_TEXTURE_MIN_FILTER,
    GL_TEXTURE_WRAP_S,
    GL_TEXTURE_WRAP_T,
    GL_TRIANGLES,
    GL_TRUE,
    GL_UNSIGNED_BYTE,
    GL_UNSIGNED_INT,
    glBindFramebuffer,
    glDrawElements,
    glGetUniformLocation,
    glUniformMatrix4fv,
)
from PIL import Image
from PySide6.QtCore import QTimerEvent
from PySide6.QtGui import QCloseEvent
from PySide6.QtOpenGLWidgets import QOpenGLWidget

from .mathutils import perspective, rotate_y_vector, rotation_y, translation

TEXTURE_DIR = Path(__file__).resolve().parent / "textures"

vertex_shader_code = """
#version 460 core
in layout(location = 0) vec3 position;
in layout(location = 1) vec2 textCoords;
uniform mat4 vp;
uniform mat4 model;
out vec2 outText;
void main()
{
    gl_Position =  vp * model * vec4(position, 1.0f);
    outText = textCoords;
}
"""

fragment_shader_code = """
#version 460 core
in vec2 outText;
out vec4 outColor;
uniform sampler2D renderedTexture;
void main()
{
    outColor = texture(renderedTexture, outText);
}
"""


def _load_image_rgb(path: str | Path) -> np.ndarray:
    """Load an image and return a bottom-up uint8 RGB array for OpenGL.

    The array is flipped vertically because image files use a top-left
    origin, whereas OpenGL texture coordinates use a bottom-left origin.
    """
    img = Image.open(path).convert("RGB")
    return np.ascontiguousarray(np.flipud(np.asarray(img, dtype=np.uint8)))


class GLCubeWidget(QOpenGLWidget):
    def __init__(self) -> None:
        super().__init__()
        self.startTimer(20)
        self.cube_positions = [(1.0, 1.0, 0.0), (0.0, 0.0, 0.0), (2.0, 0.0, 0.0)]
        self.plane_position = translation(-3.0, 1.0, 0.0)

    def timerEvent(self, event: QTimerEvent) -> None:
        self.update()

    # ------------------------------------------------------------------ setup

    def initializeGL(self) -> None:
        self.gl = get_gl()
        self.elapsedTime = 0.0
        self.last_time = time.time()
        self.aspect = float(self.size().width()) / self.size().height()

        self.view = translation(0.0, 0.0, -5.0)

        # ---- shader program ----
        self.program = Program(
            [
                Shader(ShaderStage.VERTEX, vertex_shader_code),
                Shader(ShaderStage.FRAGMENT, fragment_shader_code),
            ]
        )

        # ---- cube geometry ----
        cube = np.array(
            [
                -0.5, -0.5,  0.5, 0.0, 0.0,
                 0.5, -0.5,  0.5, 1.0, 0.0,
                 0.5,  0.5,  0.5, 1.0, 1.0,
                -0.5,  0.5,  0.5, 0.0, 1.0,
                -0.5, -0.5, -0.5, 0.0, 0.0,
                 0.5, -0.5, -0.5, 1.0, 0.0,
                 0.5,  0.5, -0.5, 1.0, 1.0,
                -0.5,  0.5, -0.5, 0.0, 1.0,
                 0.5, -0.5, -0.5, 0.0, 0.0,
                 0.5,  0.5, -0.5, 1.0, 0.0,
                 0.5,  0.5,  0.5, 1.0, 1.0,
                 0.5, -0.5,  0.5, 0.0, 1.0,
                -0.5,  0.5, -0.5, 0.0, 0.0,
                -0.5, -0.5, -0.5, 1.0, 0.0,
                -0.5, -0.5,  0.5, 1.0, 1.0,
                -0.5,  0.5,  0.5, 0.0, 1.0,
                -0.5, -0.5, -0.5, 0.0, 0.0,
                 0.5, -0.5, -0.5, 1.0, 0.0,
                 0.5, -0.5,  0.5, 1.0, 1.0,
                -0.5, -0.5,  0.5, 0.0, 1.0,
                 0.5,  0.5, -0.5, 0.0, 0.0,
                -0.5,  0.5, -0.5, 1.0, 0.0,
                -0.5,  0.5,  0.5, 1.0, 1.0,
                 0.5,  0.5,  0.5, 0.0, 1.0,
            ],
            dtype=np.float32,
        )

        self.cube_indices = np.array(
            [
                0,  1,  2,  2,  3,  0,
                4,  5,  6,  6,  7,  4,
                8,  9, 10, 10, 11,  8,
                12, 13, 14, 14, 15, 12,
                16, 17, 18, 18, 19, 16,
                20, 21, 22, 22, 23, 20,
            ],
            dtype=np.uint32,
        )

        plane = np.array(
            [
                -0.5, -0.5, 0.0, 0.0, 0.0,
                 2.0, -0.5, 0.0, 1.0, 0.0,
                 2.0,  1.0, 0.0, 1.0, 1.0,
                -0.5,  1.0, 0.0, 0.0, 1.0,
            ],
            dtype=np.float32,
        )

        self.plane_indices = np.array([0, 1, 2, 2, 3, 0], dtype=np.uint32)

        stride = 5 * 4  # 5 floats * 4 bytes per float

        # ---- cube VAO ----
        self.cube_vbo = Buffer.from_data(cube)
        self.cube_ebo = Buffer.from_data(self.cube_indices)
        self.cube_vao = VertexArray()
        self.cube_vao.set_vertex_buffer(self.cube_vbo, stride=stride)
        self.cube_vao.set_attributes(
            VertexAttrib(index=0, size=3, type_=GL_FLOAT, relative_offset=0),
            VertexAttrib(index=1, size=2, type_=GL_FLOAT, relative_offset=3 * 4),
        )
        self.cube_vao.set_element_buffer(self.cube_ebo)

        # ---- cube texture (loaded from file, uploaded manually) ----
        crate_rgb = _load_image_rgb(TEXTURE_DIR / "crate.jpg")
        h, w, _ = crate_rgb.shape
        self.cube_tex = Texture2D(w, h, internalformat=GL_RGBA8)
        self.cube_tex.upload(crate_rgb, format_=GL_RGB, type_=GL_UNSIGNED_BYTE)
        self.cube_tex.set_param(GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        self.cube_tex.set_param(GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        self.cube_tex.set_param(GL_TEXTURE_WRAP_S, GL_REPEAT)
        self.cube_tex.set_param(GL_TEXTURE_WRAP_T, GL_REPEAT)

        # ---- plane VAO ----
        self.plane_vbo = Buffer.from_data(plane)
        self.plane_ebo = Buffer.from_data(self.plane_indices)
        self.plane_vao = VertexArray()
        self.plane_vao.set_vertex_buffer(self.plane_vbo, stride=stride)
        self.plane_vao.set_attributes(
            VertexAttrib(index=0, size=3, type_=GL_FLOAT, relative_offset=0),
            VertexAttrib(index=1, size=2, type_=GL_FLOAT, relative_offset=3 * 4),
        )
        self.plane_vao.set_element_buffer(self.plane_ebo)

        # ---- offscreen render target ----
        w = self.size().width()
        h = self.size().height()

        self.plane_tex = Texture2D(w, h, internalformat=GL_SRGB8_ALPHA8)
        self.plane_tex.set_param(GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        self.plane_tex.set_param(GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        self.plane_tex.set_param(GL_TEXTURE_WRAP_S, GL_REPEAT)
        self.plane_tex.set_param(GL_TEXTURE_WRAP_T, GL_REPEAT)

        self.depth_tex = Texture2D(w, h, internalformat=GL_DEPTH_COMPONENT32F)
        self.depth_tex.set_param(GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        self.depth_tex.set_param(GL_TEXTURE_MAG_FILTER, GL_NEAREST)

        self.fbo = Framebuffer()
        self.fbo.attach_color_index(0, self.plane_tex)
        self.fbo.attach_depth(self.depth_tex)
        self.fbo.require_complete()

    # ---------------------------------------------------------------- helpers

    def _set_uniform_mat4(self, name: str, mat: np.ndarray) -> None:
        """Upload a 4x4 matrix uniform via PyOpenGL's native call.

        ``mathutils`` returns row-major matrices, so we pass ``transpose=GL_TRUE``.
        If gl46 later exposes a convenience API such as ``program.set_mat4``,
        replace this helper with it.
        """
        loc = glGetUniformLocation(self.program.id, name)
        glUniformMatrix4fv(loc, 1, GL_TRUE, mat)

    # ------------------------------------------------------------------ draw

    def drawCube(self) -> None:
        self.cube_vao.bind()
        self.cube_tex.bind_to_unit(0)

        for i, base_pos in enumerate(self.cube_positions):
            if i == 0:
                angle = -self.elapsedTime * 2.0
                rotated_pos = rotate_y_vector(base_pos, angle)
                model = translation(*rotated_pos) @ rotation_y(angle)
            else:
                model = translation(*base_pos)

            self._set_uniform_mat4("model", model)
            glDrawElements(
                GL_TRIANGLES, len(self.cube_indices), GL_UNSIGNED_INT, None
            )

        self.cube_vao.unbind()

    def paintGL(self) -> None:
        self.deltaTime = time.time() - self.last_time
        self.elapsedTime += self.deltaTime
        self.last_time = time.time()

        self.program.use()

        self.projection = perspective(45.0, self.aspect, 0.1, 100.0)
        self.vp = self.projection @ self.view
        self._set_uniform_mat4("vp", self.vp)

        # ---- pass 1: render the cubes into the offscreen texture ----
        self.fbo.bind()
        self.gl.viewport(0, 0, self.size().width(), self.size().height())
        self.gl.clear_color(0.0, 0.0, 0.0, 1.0)
        self.gl.clear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.gl.enable(GL_DEPTH_TEST)
        self.drawCube()

        # ---- pass 2: switch back to Qt's default FBO and draw the plane ----
        glBindFramebuffer(GL_FRAMEBUFFER, self.defaultFramebufferObject())
        self.gl.viewport(0, 0, self.size().width(), self.size().height())
        self.gl.clear_color(0.9, 0.9, 0.9, 1.0)
        self.gl.clear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.plane_tex.bind_to_unit(0)
        self.plane_vao.bind()
        self._set_uniform_mat4("model", self.plane_position)
        glDrawElements(
            GL_TRIANGLES, len(self.plane_indices), GL_UNSIGNED_INT, None
        )
        self.plane_vao.unbind()

        # ---- pass 3: draw the cubes to the screen as well ----
        self.drawCube()

    def resizeGL(self, w: int, h: int) -> None:
        self.makeCurrent()
        self.aspect = float(w) / h
        self.gl.viewport(0, 0, w, h)

    def closeEvent(self, event: QCloseEvent) -> None:
        self.makeCurrent()
        self.program.delete()
        self.cube_vao.delete()
        self.cube_ebo.delete()
        self.cube_vbo.delete()
        self.cube_tex.delete()
        self.plane_vao.delete()
        self.plane_vbo.delete()
        self.plane_ebo.delete()
        self.plane_tex.delete()
        self.depth_tex.delete()
        self.fbo.delete()
        return super().closeEvent(event)
