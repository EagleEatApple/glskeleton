#version 460 core
const vec4 vertices[4] = {
    { -1, -1, 0, 1 },
    {  1, -1, 0, 1 },
    {  1,  1, 0, 1 },
    { -1,  1, 0, 1 }
};
const vec2 texCoords[4] = {
    { 0, 0 }, { 1, 0 }, { 1, 1 }, { 0, 1 }
};
out vec2 texPos;
void main()
{
    gl_Position = vertices[gl_VertexID];
    texPos = texCoords[gl_VertexID];
}
