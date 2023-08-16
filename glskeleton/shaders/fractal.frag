#version 460 core
in vec2 texPos;
out vec4 fragColor;
uniform sampler2D u_Texture;
void main()
{
    fragColor = texture(u_Texture, texPos);
}
