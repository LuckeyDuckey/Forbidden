#version 330 core

uniform sampler2D BackgroundTexture;
uniform sampler2D MidgroundTexture;
uniform sampler2D ForegroundTexture;
uniform sampler2D MenusTexture;

uniform float Time;
uniform vec2 Offset;

in vec2 FragmentCoordinate;
out vec4 FragmentColor;

struct WaveSettings
{
    float FrequencyMultiplier;
    float AmplitudeMultiplier;
    float SpeedMultiplier;
    float NumberOfWaves;
    float BaseWaveAmplitude;
    float BaseWaveFrequency;
    float BaseWaveSpeed;
    float BaseWaterLevel;
    float MaxWaveHeight;
};

const WaveSettings ForegroundWaves = WaveSettings(
    2.5, 0.25, 1.1, 3.0, 1.0, 10.0, 0.25, 0.5, 0.035
);
const WaveSettings BackgroundWaves = WaveSettings(
    2.5, 0.25, 1.1, 3.0, 1.0, 8.0, 0.25, 0.55, 0.035
);

const vec4 WaterColor = vec4(0.175, 0.25, 0.25, 1.0);
const vec4 FogColor = vec4(0.5, 0.5, 0.5, 1.0);

vec2 PositionOffsetRefraction(vec2 ScreenSpacePosition, vec2 WorldSpacePosition)
{
    ScreenSpacePosition.y += (cos((WorldSpacePosition.y + (Time * 0.04)) * 45.0) * 0.0019) + (cos((WorldSpacePosition.y + (Time * 0.1)) * 10.0) * 0.002) * 1.0;
	ScreenSpacePosition.x += (sin((WorldSpacePosition.y + (Time * 0.07)) * 15.0) * 0.0029) + (sin((WorldSpacePosition.y + (Time * 0.1)) * 15.0) * 0.002) * 1.0;
    return ScreenSpacePosition;
}

float GetWaveHeight(float PositionX, WaveSettings Waves)
{   
    // Initial values
    float WaveHeightTotal = 0.0;
    float WaveAmplitudeTotal = 0.0;
    
    float WaveAmplitude = Waves.BaseWaveAmplitude;
    float WaveFrequency = Waves.BaseWaveFrequency;
    float WaveSpeed = Waves.BaseWaveSpeed;
    
    // FBM loop
    for (float WaveNumber = 0.0; WaveNumber < Waves.NumberOfWaves; WaveNumber++) {
        float WaveDirection = mod(WaveNumber, 2.0) * 2.0 - 1.0;
        float WavePosition = PositionX * WaveDirection * WaveFrequency;
        float WaveTime = Time * WaveSpeed * WaveFrequency;
        
        WaveHeightTotal += WaveAmplitude * exp(sin(WavePosition + WaveTime) - 1.0);
        WaveAmplitudeTotal += WaveAmplitude;
        
        WaveFrequency *= Waves.FrequencyMultiplier;
        WaveAmplitude *= Waves.AmplitudeMultiplier;
        WaveSpeed *= Waves.SpeedMultiplier;
    
    }
    
    return Waves.BaseWaterLevel + (WaveHeightTotal / WaveAmplitudeTotal) * Waves.MaxWaveHeight;
}

vec2 PositionOffsetCaustics(vec2 Position)
{
    Position.y += (cos((Position.y + (Time * 0.7)) * 9.0) * 0.06) + (cos((Position.y + (Time * 0.5)) * 8.0) * 0.1) * 2.0;
    Position.x += (sin((Position.y + (Time * 0.8)) * 6.0) * 0.1) + (sin((Position.y + (Time * 0.5)) * 11.0) * 0.06) * 2.0;
    return Position;
}

vec2 WhiteNoise2D(vec2 Position) {
    return fract(sin(vec2(dot(Position, vec2(127.1, 311.7)), dot(Position, vec2(269.5, 183.3)))) * 43758.5453);
}

float VoronoiNoise(vec2 Position) {
    vec2 CellCoordindte = floor(Position);
    vec2 LocalCoordinate = fract(Position);

    vec2 NearestGrid = vec2(0.0);
    vec2 NearestVector = vec2(0.0);
    float MinimumDistance = 8.0;

    // First pass: find the closest cell center
    for (int y = -1; y <= 1; y++) {
        for (int x = -1; x <= 1; x++) {
            vec2 GridOffset = vec2(float(x), float(y));
            vec2 RandomCenter = 0.5 + 0.5 * sin(Time + 6.2831 * WhiteNoise2D(CellCoordindte + GridOffset));
            vec2 OffsetVector = GridOffset + RandomCenter - LocalCoordinate;
            float Distance = dot(OffsetVector, OffsetVector);

            if (Distance < MinimumDistance) {
                MinimumDistance = Distance;
                NearestVector = OffsetVector;
                NearestGrid = GridOffset;
            }
        }
    }

    // Second pass: compute distance to nearest border
    MinimumDistance = 8.0;
    for (int y = -2; y <= 2; y++) {
        for (int x = -2; x <= 2; x++) {
            vec2 GridOffset = NearestGrid + vec2(float(x), float(y));
            vec2 RandomCenter = 0.5 + 0.5 * sin(Time + 6.2831 * WhiteNoise2D(CellCoordindte + GridOffset));
            vec2 OffsetVector = GridOffset + RandomCenter - LocalCoordinate;

            if (dot(NearestVector - OffsetVector, NearestVector - OffsetVector) > 0.00001) {
                float edgeDist = dot(0.5 * (NearestVector + OffsetVector), normalize(OffsetVector - NearestVector));
                MinimumDistance = min(MinimumDistance, edgeDist);
            }
        }
    }

    return MinimumDistance;
}

float GetCausticsPattern(vec2 Position)
{
    float EdgeDistance = VoronoiNoise(PositionOffsetCaustics(Position * 10.0));
    return 1.0 + step(EdgeDistance, 0.015) * 0.045;
}

vec4 SampleLayer(sampler2D Texture, vec2 Position, float DarknessFactor, float FogFactor, vec4 BaseColor) {
    vec4 TextureSample = texture(Texture, Position);
    TextureSample.rgb *= DarknessFactor;
    return vec4(mix(BaseColor.rgb, TextureSample.rgb, FogFactor), TextureSample.a);
}

vec4 BlendLayers(vec4 BaseColor, vec4 BackgroundColor, vec4 MidgroundColor, vec4 ForegroundColor) {
    BaseColor = mix(BaseColor, BackgroundColor, BackgroundColor.a);
    BaseColor = mix(BaseColor, MidgroundColor, MidgroundColor.a);
    BaseColor = mix(BaseColor, ForegroundColor, ForegroundColor.a);
    return BaseColor;
}

float WhiteNoise1D(vec2 Position) {
    return fract(sin(dot(Position, vec2(12.9898, 78.233))) * 43758.5453);
}

float SmoothValueNoise(vec2 Position) {
    vec2 CellIndex = floor(Position);

    float NoiseSouthWest = WhiteNoise1D(CellIndex + vec2(0.0, 0.0));
    float NoiseSouthEast = WhiteNoise1D(CellIndex + vec2(1.0, 0.0));
    float NoiseNorthWest = WhiteNoise1D(CellIndex + vec2(0.0, 1.0));
    float NoiseNorthEast = WhiteNoise1D(CellIndex + vec2(1.0, 1.0));

    vec2 InterpolationValues = smoothstep(0.0, 1.0, fract(Position));

    return mix(
        mix(NoiseSouthWest, NoiseSouthEast, InterpolationValues.x),
        mix(NoiseNorthWest, NoiseNorthEast, InterpolationValues.x), 
        InterpolationValues.y
    );
}

float FractalNoise(vec2 Position) {
    float Octaves = 5.0;
    float Lacunarity = 2.0;
    float Gain = 0.5;

    float TotalValue = 0.0;
    float MaxValue = 0.0;

    float Amplitude = 0.5;
    float Frequency = 1.0;
    
    for (float Octave = 0.0; Octave < Octaves; Octave++) {
        TotalValue += SmoothValueNoise(Position * Frequency) * Amplitude;
        MaxValue += Amplitude;

        Amplitude *= Gain;
        Frequency *= Lacunarity;
    }

    return TotalValue / MaxValue;
}

float GetWindPattern(vec2 Position) {
    // Offest over time determines direction
    vec2 SlowLargeBreezeOffest = vec2(Time / 2.5, 0.0);
    vec2 FastSmallBreezeOffset = vec2(Time / 5.0, 0.0);

    // Layered noise where larger, slower waves (layer 4) influence smaller, faster ones (layer 1)
    float FirstLayerNoise = FractalNoise(Position - FastSmallBreezeOffset);
    float SecondLayerNoise = FractalNoise(Position + 2.0 * FirstLayerNoise);
    float ThirdLayerNoise = FractalNoise(Position + SecondLayerNoise);
    float FourthLayerNoise = FractalNoise(Position + SlowLargeBreezeOffest + ThirdLayerNoise);

    return FourthLayerNoise;
}

void main()
{
	vec2 OffestCoordinate = FragmentCoordinate + vec2(Offset.x, -Offset.y);
    
    float ForegroundHeight = GetWaveHeight(OffestCoordinate.x, ForegroundWaves);
    float BackgroundHeight = GetWaveHeight(OffestCoordinate.x, BackgroundWaves);
    
    if (ForegroundHeight > OffestCoordinate.y) {
        // Apply depth based darkening
        float WaterBrightness = smoothstep(ForegroundHeight - 1.5, ForegroundHeight, OffestCoordinate.y);
        FragmentColor = WaterColor * (WaterBrightness * 0.5 + 0.5);

        // Apply surface refraction + general refraction
        vec2 SamplePosition = FragmentCoordinate + vec2(smoothstep(ForegroundHeight - 0.025, ForegroundHeight, OffestCoordinate.y) * 0.015, 0.0);
        SamplePosition = PositionOffsetRefraction(SamplePosition, OffestCoordinate);

        vec4 BackgroundColor = SampleLayer(BackgroundTexture, SamplePosition, WaterBrightness * 0.25 + 0.25, 0.1, FragmentColor);
        vec4 MidgroundColor = SampleLayer(MidgroundTexture, SamplePosition, WaterBrightness * 0.25 + 0.25, 0.2, FragmentColor);
        vec4 ForegroundColor = SampleLayer(ForegroundTexture, SamplePosition, WaterBrightness * 0.075 + 0.05, 0.4, FragmentColor);

        // Combine layers + Add caustics to water
        FragmentColor = GetCausticsPattern(OffestCoordinate * 1.5) * BlendLayers(FragmentColor, BackgroundColor, MidgroundColor, ForegroundColor);
    }
    
    else {

        // Apply fog to water based on scene depth
        float SceneDepth = smoothstep(ForegroundHeight, BackgroundHeight, OffestCoordinate.y);
        vec4 FogColorAnimated = FogColor * (GetWindPattern(OffestCoordinate) * 0.75 + 0.5);
        FragmentColor = vec4(mix(WaterColor.rgb * 0.75, FogColorAnimated.rgb, SceneDepth * 0.5 + step(1.0, SceneDepth) * 0.5), 1.0);

        vec4 BackgroundColor = SampleLayer(BackgroundTexture, FragmentCoordinate, 0.5, 0.45, FogColorAnimated);
        vec4 MidgroundColor = SampleLayer(MidgroundTexture, FragmentCoordinate, 0.5, 0.65, FogColorAnimated);
        vec4 ForegroundColor = SampleLayer(ForegroundTexture, FragmentCoordinate, 0.5, 0.85, FogColorAnimated);

        // Layers hit water at different scene depth
        BackgroundColor.a *= 1.0 - step(SceneDepth, 0.85);
        MidgroundColor.a *= 1.0 - step(SceneDepth, 0.5);
        ForegroundColor.a *= 1.0 - step(SceneDepth, 0.15);

        // Combine layers
        FragmentColor = BlendLayers(FragmentColor, BackgroundColor, MidgroundColor, ForegroundColor);
    }

    vec4 MenusColor = texture(MenusTexture, FragmentCoordinate);
    FragmentColor = mix(FragmentColor, MenusColor, MenusColor.a);
}
