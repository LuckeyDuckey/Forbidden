#version 330 core

in vec2 Vertex;
in vec2 TextureCoordinate;

out vec2 FragmentCoordinate;

void main()
{
    FragmentCoordinate = TextureCoordinate;
    gl_Position = vec4(Vertex, 0.0, 1.0);
}
