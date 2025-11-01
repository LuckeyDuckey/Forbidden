from ..GameObject import GameObject
from ..CppBuild.Simulations import Vec2

import pygame, sys, math, os, time, random
from pygame.locals import *
import numpy as np

class BoatSimulation(GameObject):
    def __init__(self, Position, NumberSamplePoints):
        self.Position = Position
        
        self.BoatImage = pygame.image.load(os.path.join(os.getcwd(), "Data/Images/Boat.png")).convert_alpha()
        self.BoatPixelOffset = Vec2(self.BoatImage.get_size()) * Vec2([0, 0.475])

        self.LanternImage = pygame.image.load(os.path.join(os.getcwd(), "Data/Images/Lantern.png")).convert_alpha()
        self.LanternPixelOffset = Vec2(self.LanternImage.get_size()) * Vec2([0.5, 0])

        self.LanternGlowImage = self.GenerateLanternGlow([250, 250], [255, 200, 100], 0.75)
        self.LanternGlowPixelOffset = Vec2(self.LanternGlowImage.get_size()) * Vec2([0.5, 0.5]) - Vec2(self.LanternImage.get_size()) * Vec2([0, 0.5])

        self.VectorToLantern = Vec2(self.BoatImage.get_size()) * Vec2([0.5, 0.35])

        self.NumberSamplePoints = NumberSamplePoints
        self.ProgramTime = 0
        self.WaveSettings = {
            "FrequencyMultiplier": 2.5,
            "AmplitudeMultiplier": 0.25,
            "SpeedMultiplier": 1.1,
            "NumberOfWaves": 3,
            "BaseWaveAmplitude": 1.0,
            "BaseWaveFrequency": 10.0,
            "BaseWaveSpeed": 0.25,
            "BaseWaterLevel": 0.5,
            "MaxWaveHeight": 0.035,
        }

    def GenerateLanternGlow(self, Size, Color, Intensity):
        # Generate normalized coordinate grids (0 to 1 range)
        PositionX, PositionY = np.meshgrid(
            np.linspace(0, 1, Size[0], dtype=np.float64),
            np.linspace(0, 1, Size[1], dtype=np.float64),
            indexing='ij'  # Ensures correct shape [x, y]
        )

        # Calculate radial distance and glow falloff
        DistanceFromCenter = np.clip(np.sqrt((PositionX - 0.5) ** 2 + (PositionY - 0.5) ** 2), 0.0, 0.5)
        GlowIntensity = np.clip(pow((0.5 - DistanceFromCenter) * 2, 2) * Intensity, 0.0, 1.0)

        # Apply color
        SurfaceArray = np.zeros((Size[0], Size[1], 4), dtype=np.float64)
        SurfaceArray[:, :, :3] = Color
        SurfaceArray[:, :, 3] = GlowIntensity * 255.0

        # Apply dithering to remove banding
        DitherNoise = np.random.uniform(-1.0, 1.0, GlowIntensity.shape)
        SurfaceArray[:, :, 3] = np.clip(SurfaceArray[:, :, 3] + DitherNoise, 0, 255)

        # Convert to uint8 and make an alpha surface
        Surface = pygame.surfarray.make_surface(SurfaceArray[:, :, :3].astype(np.uint8)).convert_alpha()

        # Apply alpha channel separately (since make_surface doesn’t take alpha array directly)
        alpha_surface = pygame.surfarray.pixels_alpha(Surface)
        alpha_surface[:] = SurfaceArray[:, :, 3].astype(np.uint8)
        del alpha_surface  # Unlock the surface

        return Surface

    def GetWaveHeight(self, PositionX): 
        # Initial values
        WaveHeightTotal = 0
        WaveAmplitudeTotal = 0
        
        WaveAmplitude = self.WaveSettings["BaseWaveAmplitude"]
        WaveFrequency = self.WaveSettings["BaseWaveFrequency"]
        WaveSpeed = self.WaveSettings["BaseWaveSpeed"]
        
        # FBM loop
        for WaveNumber in range(self.WaveSettings["NumberOfWaves"]):
            WaveDirection = (WaveNumber % 2) * 2 - 1
            WavePosition = PositionX * WaveDirection * WaveFrequency
            WaveTime = self.ProgramTime * WaveSpeed * WaveFrequency
            
            WaveHeightTotal += WaveAmplitude * np.exp(np.sin(WavePosition + WaveTime) - 1)
            WaveAmplitudeTotal += WaveAmplitude
            
            WaveFrequency *= self.WaveSettings["FrequencyMultiplier"]
            WaveAmplitude *= self.WaveSettings["AmplitudeMultiplier"]
            WaveSpeed *= self.WaveSettings["SpeedMultiplier"]
        
        return self.WaveSettings["BaseWaterLevel"] + (WaveHeightTotal / WaveAmplitudeTotal) * self.WaveSettings["MaxWaveHeight"]

    def Render(self):
        self.ProgramTime += self.Game.DeltaTime

        WavePointsX = np.array([
            self.Position.x + self.BoatImage.get_width() * (Index / self.NumberSamplePoints - 0.5)
            for Index in range(self.NumberSamplePoints)
        ])
        WavePointsY = np.array([
            self.Game.Settings.SceneResolution.y * (1 - self.GetWaveHeight(Point / self.Game.Settings.SceneResolution.x))
            for Point in WavePointsX
        ])

        AverageWaveGradient, _ = np.polyfit(WavePointsX, WavePointsY, 1)
        AverageWaveHeight = np.mean(WavePointsY)

        BoatAngle = math.atan(AverageWaveGradient)
        RenderImage = pygame.transform.rotate( 
            surface = self.BoatImage,
            angle = math.degrees(-BoatAngle),
        )
        RenderPosition = Vec2([self.Position.x, AverageWaveHeight]) - self.BoatPixelOffset - Vec2(RenderImage.get_size()) * 0.5
        
        self.Game.PygameScene.ForegroundSurface.blit(
            source = RenderImage,
            dest = RenderPosition - self.Game.PygameScene.PixelOffset,
        )

        RotatedVectorToLantern = Vec2([
            self.VectorToLantern.x * math.cos(BoatAngle) - self.VectorToLantern.y * math.sin(BoatAngle),
            self.VectorToLantern.x * math.sin(BoatAngle) + self.VectorToLantern.y * math.cos(BoatAngle),
        ])
        LanternPosition = RotatedVectorToLantern + RenderPosition + Vec2(RenderImage.get_size()) * 0.5

        self.Game.PygameScene.ForegroundSurface.blit(
            source = self.LanternImage,
            dest = LanternPosition - self.LanternPixelOffset - self.Game.PygameScene.PixelOffset,
        )

        self.Game.PygameScene.ForegroundSurface.blit(
            source = self.LanternGlowImage,
            dest = LanternPosition - self.LanternGlowPixelOffset - self.Game.PygameScene.PixelOffset,
        )
