from ..GameObject import GameObject
from ..CppBuild.Simulations import Vec2
from ..CppBuild.Simulations import VerletChain

import pygame, random
from pygame.locals import *
import numpy as np

class KelpSimulationManager(GameObject):
    def __init__(self, NumberOfKelp):
        self.KelpVerletChains = [self.CreateKelpVerletChain() for Index in range(NumberOfKelp)]

    def CreateKelpVerletChain(self):
        NumberPoints = random.randint(3, 20)
        RandomPositionX = random.uniform(-0.5, 1.5)
        OceanFloorHeight = self.Game.OceanFloor.GetTerrainHeight((RandomPositionX + 0.5) * 0.5)
        return VerletChain(
            Position = self.Game.Settings.SceneResolution * Vec2([RandomPositionX, 2.0]) - Vec2([0, OceanFloorHeight]),
            NumberPoints = NumberPoints,
            DesiredDistancePoints = 25,
            NumberDisplayPointsPerSegment = 2,
        )

    def Render(self):
        for KelpVerletChain in self.KelpVerletChains:
            # Verlet chains are unstable with variable delta time values
            KelpVerletChain.Update(1 / self.Game.Settings.FpsCap, self.Game.Mouse.Clicking, self.Game.Mouse.WorldPosition, self.Game.Mouse.AnimatedRadius)
            DisplayPoints = KelpVerletChain.CalculateDisplayPoints()
            
            SegmentWidths = KelpVerletChain.SegmentWidths
            SegmentColorMultipliers = KelpVerletChain.SegmentColorMultipliers

            for Index in range(len(DisplayPoints) - 1):
                pygame.draw.line(
                    surface = self.Game.PygameScene.ForegroundSurface,
                    color = np.array([225, 255, 75]) * SegmentColorMultipliers[Index],
                    start_pos = DisplayPoints[Index] - self.Game.PygameScene.PixelOffset,
                    end_pos = DisplayPoints[Index + 1] - self.Game.PygameScene.PixelOffset,
                    width = SegmentWidths[Index],
                )
