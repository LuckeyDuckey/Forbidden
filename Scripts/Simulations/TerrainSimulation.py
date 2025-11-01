from ..GameObject import GameObject
from ..CppBuild.Simulations import Vec2

import pygame, math, time, sys, random
from pygame.locals import *
import numpy as np

class GrassSimulation(GameObject):
    def __init__(self, TerrainSurface, DisplayPointsOffset):
        self.TerrainSurface = TerrainSurface
        self.DisplayPointsOffset = DisplayPointsOffset

    def RenderBlade(self, Position, NumberDisplayPoints):
        DisplayPoints = [
            Position + Vec2([
                random.randint(-self.DisplayPointsOffset.x, self.DisplayPointsOffset.x),
                -Index * self.DisplayPointsOffset.y,
            ])
            for Index in range(NumberDisplayPoints)
        ]
        
        for Index in range(NumberDisplayPoints - 1):
            pygame.draw.line(
                surface = self.TerrainSurface,
                color = [225, 255, 75],
                start_pos = DisplayPoints[Index],
                end_pos = DisplayPoints[Index + 1],
                width = random.randint(1, 3),
            )

class TerrainSimulation(GameObject):
    def __init__(self, Position, Resolution, StepSize, NumberOfGrassBlades):
        self.Position = Position - Vec2([0, Resolution.y])
        self.Resolution = Resolution
        
        self.StepSize = StepSize
        self.TerrainSeed = random.random()
        self.TerrainSurface = pygame.Surface(Resolution).convert_alpha()

        self.TerrarinGrass = GrassSimulation(
            TerrainSurface = self.TerrainSurface,
            DisplayPointsOffset = Vec2([3, 4]),
        )
        self.NumberOfGrassBlades = NumberOfGrassBlades
        
        self.RenderTerrain()

    def EaseInOutSine(self, Value):
        return -(math.cos(math.pi * Value) - 1) * 0.5;

    def SampleValueNoise(self, PositionX):
        Fractional = lambda Value: Value - math.floor(Value)
        return Fractional(math.sin(PositionX + self.TerrainSeed) * 43758.5453123)

    def GetTerrainHeight(self, ScaledPositionX, Octaves=4, Lacunarity=3.0, Gain=0.5):
        TotalValue = 0.0
        MaxValue = 0.0

        Amplitude = 1.0
        Frequency = 1.0

        for Octave in range(Octaves):
            SamplePositionX = ScaledPositionX * Frequency
            
            ValueNoiseLeft = self.SampleValueNoise(SamplePositionX // self.StepSize)
            ValueNoiseRight = self.SampleValueNoise(SamplePositionX // self.StepSize + 1.0)

            BlendFactor = self.EaseInOutSine((SamplePositionX % self.StepSize) / self.StepSize)
            BlendedValueNoise = ValueNoiseLeft * (1 - BlendFactor) + ValueNoiseRight * BlendFactor

            TotalValue += BlendedValueNoise * Amplitude
            MaxValue += Amplitude

            Amplitude *= Gain
            Frequency *= Lacunarity

        # Normalize and scale
        return (TotalValue / MaxValue) * self.Resolution.y

    def RenderTerrain(self):
        TerrainPoints = [self.Resolution, Vec2([0, self.Resolution.y])]
        for PositionX in range(int(self.Resolution.x)):
            TerrainPoints.append(Vec2([PositionX, self.Resolution.y - self.GetTerrainHeight(PositionX / self.Resolution.x)]))

        self.TerrainSurface.fill([0, 0, 0, 0])
        pygame.draw.polygon(
            surface = self.TerrainSurface,
            color = [225, 190, 145],
            points = TerrainPoints,
        )

        for Index in range(self.NumberOfGrassBlades):
            self.TerrarinGrass.RenderBlade(
                Position = Vec2([
                    Index * (self.Resolution.x / self.NumberOfGrassBlades),
                    self.Resolution.y - self.GetTerrainHeight(Index / self.NumberOfGrassBlades),
                ]),
                NumberDisplayPoints = random.randint(2, 4),
            )

    def Render(self):
        self.Game.PygameScene.ForegroundSurface.blit(
            source = self.TerrainSurface,
            dest = self.Position - self.Game.PygameScene.PixelOffset,
        )
