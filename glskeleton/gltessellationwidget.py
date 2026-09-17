# refer to https://github.com/byhj/OpenGL-Framework/blob/master/src/Tess-Triangle/TessTriangle.cpp

"""Tessellation demo — 5-stage pipeline (vertex -> TCS -> TES -> geometry -> fragment).

Ported to gl46 + numpy. The ImGui panel has been replaced by keyboard
shortcuts: Up/Down adjust the inner tessellation level, Left/Right the outer.
"""

from __future__ import annotations

import time

import numpy as np
from gl46.buffer import EBO, Buffer
from gl46.program import Program
from gl46.shader import Shader, ShaderStage
from gl46.vertexarray import VertexArray, VertexAttrib
from OpenGL.GL import (
    GL_COLOR_BUFFER_BIT,
    GL_CULL_FACE,
    GL_DEPTH_BUFFER_BIT,
    GL_DEPTH_TEST,
    GL_FLOAT,
    GL_PATCH_VERTICES,
    GL_PATCHES,
    GL_TRUE,
    GL_UNSIGNED_INT,
    glClear,
    glClearColor,
    glDrawElements,
    glEnable,
    glGetUniformLocation,
    glPatchParameteri,
    glUniformMatrix4fv,
    glViewport,
)
from PySide6.QtCore import Qt, QTimerEvent
from PySide6.QtGui import QCloseEvent, QKeyEvent
from PySide6.QtOpenGLWidgets import QOpenGLWidget

from .mathutils import look_at, perspective, rotation_x

vertex_shader_code = """
#version 460 core
layout (location = 0) in vec3 Position;
out VS_OUT
{
  vec3 Pos;
}vs_out;
void main(void)
{
   vs_out.Pos = Position;
}
"""

tessellation_control_shader_code = """
#version 460 core
layout (vertices = 3) out;
in VS_OUT
{
    vec3 Pos;
}vs_out[];
out TC_OUT
{
    vec3 Pos;
}tc_out[];
uniform int tessInner;
uniform int tessOuter;
void main(void)
{
    if (gl_InvocationID == 0)
    {
        gl_TessLevelInner[0] = tessInner;
        gl_TessLevelOuter[0] = tessOuter;
        gl_TessLevelOuter[1] = tessOuter;
        gl_TessLevelOuter[2] = tessOuter;
    }

    tc_out[gl_InvocationID].Pos = vs_out[gl_InvocationID].Pos;
}
"""

tessellation_evaluation_shader_code = """
#version 460 core
layout (triangles, equal_spacing, cw) in;
in TC_OUT
{
    vec3 Pos;
}tc_out[];
out TE_OUT
{
    vec3 Pos;
    vec3 PatchDistance;
}te_out;
uniform mat4 model;
uniform mat4 view;
uniform mat4 proj;
void main(void)
{
    vec3 p0 = gl_TessCoord.x * tc_out[0].Pos;
    vec3 p1 = gl_TessCoord.y * tc_out[1].Pos;
    vec3 p2 = gl_TessCoord.z * tc_out[2].Pos;
    te_out.PatchDistance = gl_TessCoord;
    te_out.Pos = normalize(p0 + p1 + p2);
    mat4 mvp = proj * view * model;
    gl_Position = mvp * vec4(te_out.Pos, 1.0f);
}
"""

geometry_shader_code = """
#version 460 core
layout (triangles) in;
layout (triangle_strip, max_vertices = 3) out;
in TE_OUT
{
    vec3 Pos;
    vec3 PatchDistance;
}te_out[3];
out GE_OUT
{
    vec3 FacetNormal;
    vec3 PatchDistance;
    vec3 TriDistance;
}ge_out;
uniform mat4 model;
uniform mat4 view;
void main(void)
{
    mat3 normal_mat = mat3(transpose(inverse(view * model) ) );
    vec3 A = te_out[2].Pos - te_out[0].Pos;
    vec3 B = te_out[1].Pos - te_out[0].Pos;
    ge_out.FacetNormal = normal_mat * normalize(cross(A, B));
    ge_out.PatchDistance = te_out[0].PatchDistance;
    ge_out.TriDistance  = vec3(1, 0, 0);
    gl_Position = gl_in[0].gl_Position;
    EmitVertex();
    ge_out.PatchDistance = te_out[1].PatchDistance;
    ge_out.TriDistance  = vec3(0, 1, 0);
    gl_Position = gl_in[1].gl_Position;
    EmitVertex();
    ge_out.PatchDistance = te_out[2].PatchDistance;
    ge_out.TriDistance  = vec3(0, 0, 1);
    gl_Position = gl_in[2].gl_Position;
    EmitVertex();
    EndPrimitive();
}
"""

fragment_shader_code = """
#version 460 core
layout (location = 0) out vec4  FragColor;
in GE_OUT
{
    vec3 FacetNormal;
    vec3 PatchDistance;
    vec3 TriDistance;
}ge_out;
uniform vec3 lightDir;
uniform vec4 diffuseMat;
uniform vec4 ambientMat;
float amplify(float d, float scale, float offset)
{
    d = scale * d + offset;
    d = clamp(d, 0, 1);
    d = 1 - exp2(-2 * d * d);
    return d;
}
void main(void)
{
    vec3 N = normalize(ge_out.FacetNormal);
    vec3 L = lightDir;
    float df = max(0.0f, dot(N, L) );
    vec4 color = ambientMat + df * diffuseMat;
    float d1 = min(min(ge_out.TriDistance.x, ge_out.TriDistance.y), ge_out.TriDistance.z);
    float d2 = min(min(ge_out.PatchDistance.x, ge_out.PatchDistance.y), ge_out.PatchDistance.z);
    color = amplify(d1, 40, -0.5) * amplify(d2, 60, -0.5) * color;
    FragColor = color;
}
"""


class GLTessellationWidget(QOpenGLWidget):
    def __init__(self) -> None:
        super().__init__()
        self.startTimer(20)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.m_TessInner = 3
        self.m_TessOuter = 2
        self.m_AmbientMat = (0.04, 0.04, 0.04, 1.0)
        self.m_DiffuseMat = (0.0, 0.75, 0.75, 1.0)
        self.m_LightDir = (0.25, 0.25, -1.0)

    def timerEvent(self, event: QTimerEvent) -> None:
        self.update()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        key = event.key()
        if key == Qt.Key.Key_Up:
            self.m_TessInner = min(64, self.m_TessInner + 1)
        elif key == Qt.Key.Key_Down:
            self.m_TessInner = max(1, self.m_TessInner - 1)
        elif key == Qt.Key.Key_Right:
            self.m_TessOuter = min(64, self.m_TessOuter + 1)
        elif key == Qt.Key.Key_Left:
            self.m_TessOuter = max(1, self.m_TessOuter - 1)
        else:
            super().keyPressEvent(event)
            return
        self.update()

    # ------------------------------------------------------------------ setup

    def initializeGL(self) -> None:
        self.elapsedTime = 0.0
        self.last_time = time.time()
        self.aspect = float(self.size().width()) / self.size().height()

        # ---- five-stage shader program ----
        self.program = Program(
            [
                Shader(ShaderStage.VERTEX, vertex_shader_code),
                Shader(ShaderStage.TESS_CONTROL, tessellation_control_shader_code),
                Shader(ShaderStage.TESS_EVALUATION, tessellation_evaluation_shader_code),
                Shader(ShaderStage.GEOMETRY, geometry_shader_code),
                Shader(ShaderStage.FRAGMENT, fragment_shader_code),
            ]
        )

        # ---- geometry data ----
        vertices = np.array(
            [
                 0.000,  0.000,  1.000,
                 0.894,  0.000,  0.447,
                 0.276,  0.851,  0.447,
                -0.724,  0.526,  0.447,
                -0.724, -0.526,  0.447,
                 0.276, -0.851,  0.447,
                 0.724,  0.526, -0.447,
                -0.276,  0.851, -0.447,
                -0.894,  0.000, -0.447,
                -0.276, -0.851, -0.447,
                 0.724, -0.526, -0.447,
                 0.000,  0.000, -1.000,
            ],
            dtype=np.float32,
        )

        self.indices = np.array(
            [
                2, 1, 0,
                3, 2, 0,
                4, 3, 0,
                5, 4, 0,
                1, 5, 0,

                11, 6,  7,
                11, 7,  8,
                11, 8,  9,
                11, 9,  10,
                11, 10, 6,

                1, 2, 6,
                2, 3, 7,
                3, 4, 8,
                4, 5, 9,
                5, 1, 10,

                2,  7, 6,
                3,  8, 7,
                4,  9, 8,
                5, 10, 9,
                1, 6, 10,
            ],
            dtype=np.uint32,
        )

        stride = 3 * 4  # 3 floats * 4 bytes per float
        self.vao = VertexArray()
        self.vbo = Buffer.from_data(vertices)
        self.ebo = EBO(self.indices)
        self.vao.set_vertex_buffer(self.vbo, stride=stride)
        self.vao.set_attributes(
            VertexAttrib(index=0, size=3, type_=GL_FLOAT, relative_offset=0),
        )
        self.vao.set_element_buffer(self.ebo)

        glClearColor(0.4, 0.4, 0.4, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glPatchParameteri(GL_PATCH_VERTICES, 3)

    # ------------------------------------------------------------------ draw

    def _set_uniform_mat4(self, name: str, mat: np.ndarray) -> None:
        """Upload a 4x4 matrix uniform via PyOpenGL's native call.

        ``mathutils`` returns row-major matrices, so we pass ``transpose=GL_TRUE``.
        """
        loc = glGetUniformLocation(self.program.id, name)
        glUniformMatrix4fv(loc, 1, GL_TRUE, np.ascontiguousarray(mat, dtype=np.float32))

    def paintGL(self) -> None:
        self.deltaTime = time.time() - self.last_time
        self.elapsedTime += self.deltaTime
        self.last_time = time.time()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.program.use()
        self.program.set_i("tessInner", self.m_TessInner)
        self.program.set_i("tessOuter", self.m_TessOuter)
        self.program.set_f("lightDir", *self.m_LightDir)
        self.program.set_f("diffuseMat", *self.m_DiffuseMat)
        self.program.set_f("ambientMat", *self.m_AmbientMat)

        model = rotation_x(-self.elapsedTime / 3.0)
        view = look_at((0.0, 0.0, 3.0), (0.0, 0.0, 0.0), (0.0, 1.0, 0.0))
        proj = perspective(45.0, self.aspect, 0.1, 1000.0)

        self._set_uniform_mat4("model", model)
        self._set_uniform_mat4("view", view)
        self._set_uniform_mat4("proj", proj)

        self.vao.bind()
        glDrawElements(GL_PATCHES, self.indices.size, GL_UNSIGNED_INT, None)
        self.vao.unbind()

    def resizeGL(self, w: int, h: int) -> None:
        self.makeCurrent()
        self.aspect = float(w) / h
        glViewport(0, 0, w, h)

    def closeEvent(self, event: QCloseEvent) -> None:
        self.makeCurrent()
        self.vbo.delete()
        self.vao.delete()
        self.ebo.delete()
        self.program.delete()
        return super().closeEvent(event)
