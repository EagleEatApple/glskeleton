# refer to https://github.com/byhj/OpenGL-Framework/blob/master/src/Tess-Triangle/TessTriangle.cpp

import sys
import time

import numpy as np
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtCore import QTimerEvent
from PySide6.QtGui import QCloseEvent, QSurfaceFormat
from OpenGL.GL import *
import imgui
import glm


from py3gl4.program import Program
from py3gl4.shader import VertexShader, FragmentShader, TessellationControlShader, TessellationEvaluationShader, GeometryShader
from py3gl4.vertexarrayobject import VertexArrayObject, VertexAttribute
from py3gl4.vertexbufferobject import VertexBufferObject
from py3gl4.elementbufferobject import ElementBufferObject
from py3gl4.uniform import Uniform
from qtimgui.pyside6 import PySide6Renderer
from baseapp import BaseApplication

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
  vec4 color = ambientMat + df * diffuseMat;// + pow(sp, 32) * diffuseMat;
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

    def timerEvent(self, event: QTimerEvent) -> None:
        self.update()

    def initializeGL(self)-> None:
        self.elapsedTime = 0.0
        self.last_time = time.time()
        self.aspect = float(self.size().width()) / self.size().height()
        self.m_TessInner = 3
        self.m_TessOuter = 2
        self.m_AmbientMat = glm.vec4(0.04, 0.04, 0.04, 1.0)
        self.m_DiffuseMat = glm.vec4(0.0, 0.75, 0.75, 1.0)
        self.m_LightDir = glm.vec3(0.25, 0.25, -1.0)
        # initialize opengl pipeline
        vertex_shader = VertexShader(vertex_shader_code)
        tcs_shader = TessellationControlShader(tessellation_control_shader_code)
        tes_shader = TessellationEvaluationShader(tessellation_evaluation_shader_code)
        geometry_shader = GeometryShader(geometry_shader_code)
        fragment_shader = FragmentShader(fragment_shader_code)
        self.program = Program([vertex_shader,tcs_shader, tes_shader, geometry_shader, fragment_shader])
        self.program.addUniform(Uniform("tessInner", GL_INT))
        self.program.addUniform(Uniform("tessOuter", GL_INT))
        self.program.addUniform(Uniform("model", GL_FLOAT_MAT4))
        self.program.addUniform(Uniform("view", GL_FLOAT_MAT4))
        self.program.addUniform(Uniform("proj", GL_FLOAT_MAT4))
        self.program.addUniform(Uniform("lightDir", GL_FLOAT_VEC3))
        self.program.addUniform(Uniform("diffuseMat", GL_FLOAT_VEC4))
        self.program.addUniform(Uniform("ambientMat", GL_FLOAT_VEC4))
        vertex_shader.delete()
        tcs_shader.delete()
        tes_shader.delete()
        geometry_shader.delete()
        fragment_shader.delete()


        # initialize vao, vbo
        vertices = np.array([
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
         0.000,  0.000, -1.000
        ], dtype=GLfloat)

        self.indices = np.array([
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
        1, 6, 10            
        ], dtype=GLuint)

        attribute_position = VertexAttribute("Position", 0, 3, GL_FLOAT, False, 0)
        vaoBindingPoint = 0
        self.vao = VertexArrayObject()
        self.vbo = VertexBufferObject(vertices)
        self.ebo = ElementBufferObject(self.indices)
        self.vao.setVertexBuffer(self.vbo, vaoBindingPoint, 0, 3 * sizeof(GLfloat))
        self.vao.setVertexAttribute(vaoBindingPoint, attribute_position)
        self.vao.setElementBuffer(self.ebo)

        glClearColor(0.4, 0.4, 0.4, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glPatchParameteri(GL_PATCH_VERTICES, 3)

        # initialize imgui
        imgui.create_context()
        self.impl = PySide6Renderer(self)

    def paintGL(self):
        self.deltaTime = time.time() - self.last_time
        self.elapsedTime += self.deltaTime
        self.last_time = time.time()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.program.use()
        self.program.uniforms["tessInner"].setInt(self.m_TessInner)
        self.program.uniforms["tessOuter"].setInt(self.m_TessOuter)
        self.program.uniforms["lightDir"].setVec3(self.m_LightDir.x,self.m_LightDir.y,self.m_LightDir.z)
        self.program.uniforms["diffuseMat"].setVec4(self.m_DiffuseMat.x, self.m_DiffuseMat.y, self.m_DiffuseMat.z, self.m_DiffuseMat.w)
        self.program.uniforms["ambientMat"].setVec4(self.m_AmbientMat.x, self.m_AmbientMat.y, self.m_AmbientMat.z, self.m_AmbientMat.w)
        model = glm.rotate( glm.mat4(1.0), -self.elapsedTime/5.0, glm.vec3(1.0, 0.0, 0.0) )
        view = glm.lookAt(glm.vec3(0.0, 0.0, 3.0), glm.vec3(0.0, 0.0, 0.0), glm.vec3(0.0, 1.0, 0.0))
        proj = glm.perspective(45.0, self.aspect, 0.1, 1000)
        self.program.uniforms["model"].setMat4(glm.value_ptr(model))
        self.program.uniforms["view"].setMat4(glm.value_ptr(view))
        self.program.uniforms["proj"].setMat4(glm.value_ptr(proj))

        self.vao.bind()        
        glDrawElements(GL_PATCHES, self.indices.size, GL_UNSIGNED_INT,None)

        # define imgui elements
        self.impl.process_inputs()
        imgui.new_frame()
        imgui.set_next_window_position(0, 0, condition=imgui.FIRST_USE_EVER)
        imgui.set_next_window_size(200, 100, condition=imgui.FIRST_USE_EVER)
        imgui.begin("Settings")
        _, self.m_TessInner =  imgui.slider_int("Inner Tess", self.m_TessInner, 1, 4)
        _, self.m_TessOuter =  imgui.slider_int("Outer Tess", self.m_TessOuter, 1, 4)
        imgui.end()

        # render imgui
        imgui.render()
        self.impl.render(imgui.get_draw_data())


    def resizeGL(self, w: int, h: int) -> None:
        self.makeCurrent()
        self.aspect = float(w) / h 
        glViewport(0,0,w,h)

    def closeEvent(self, event: QCloseEvent) -> None:
        self.makeCurrent()
        self.vbo.delete()
        self.vao.delete()
        self.ebo.delete()
        self.program.delete()
        return super().closeEvent(event)


def test() -> None:
    """Run GLWidget test"""
    app = BaseApplication(sys.argv)
    widget = GLTessellationWidget()
    widget.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    test()
