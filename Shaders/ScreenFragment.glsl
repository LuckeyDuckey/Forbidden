#version 330

uniform sampler2D SceneTexture;

in vec2 FragmentCoordinate;
out vec4 FragmentColor;

void main() {
    FragmentColor = texture(SceneTexture, FragmentCoordinate);
}
