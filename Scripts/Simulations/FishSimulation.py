from ..GameObject import GameObject
from ..CppBuild.Simulations import Vec2
from ..CppBuild.Simulations import Boid

import pygame, math, time, random, os
from pygame.locals import *
import numpy as np

class FishSimulationManager(GameObject):
    def __init__(self, NumberOfFish, BoundsMin, BoundsMax, BoundsMargin):
        self.Boids = [Boid(
            BoundsMin = BoundsMin,
            BoundsMax = BoundsMax,
            BoundsMargin = BoundsMargin,
        ) for Index in range(NumberOfFish)]

        self.FishImageLeft = pygame.image.load(os.path.join(os.getcwd(), "Data/Images/Fish.png")).convert_alpha()
        self.FishImageRight = pygame.transform.flip(self.FishImageLeft.copy(), True, False)

        self.CachedRotationsFishImageLeft = {
            Angle : pygame.transform.rotate(
                surface = self.FishImageLeft,
                angle = Angle,
            ) for Angle in range(-90, 91)
        }
        self.CachedRotationsFishImageRight = {
            Angle : pygame.transform.rotate(
                surface = self.FishImageRight,
                angle = Angle,
            ) for Angle in range(-90, 91)
        }

    def Render(self):
        for Boid in self.Boids:
            # Boids are unstable with variable delta time values
            Boid.Update(self.Boids, self.Game.DeltaTime, self.Game.Mouse.Clicking, self.Game.Mouse.WorldPosition, self.Game.Mouse.AnimatedRadius)

            if Boid.Direction.x < 0:
                Angle = math.degrees(math.atan2(Boid.Direction.y, -Boid.Direction.x))
                RenderImage = self.CachedRotationsFishImageLeft[round(Angle)]
            else:
                Angle = math.degrees(math.atan2(-Boid.Direction.y, Boid.Direction.x))
                RenderImage = self.CachedRotationsFishImageRight[round(Angle)]

            RenderPosition = Boid.Position - Vec2(RenderImage.get_size()) * 0.5
            
            self.Game.PygameScene.ForegroundSurface.blit(
                source = RenderImage,
                dest = RenderPosition - self.Game.PygameScene.PixelOffset,
            )
