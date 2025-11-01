from ..GameObject import GameObject
from ..CppBuild.Simulations import Vec2

import pygame
from pygame.locals import *

class MouseHandler(GameObject):
    def __init__(self):
        self.ScenePosition = Vec2([0, 0])
        self.WorldPosition = Vec2([0, 0])
        self.Clicking = False
        self.BorderThickness = 1

        self.TargetRadius = 25
        self.AnimatedRadius = 25

        self.MinRadius = 25
        self.MaxRadius = 150
        self.MenusRadius = 4

    def Render(self):
        pygame.draw.circle(
            surface = self.Game.PygameScene.ForegroundSurface,
            color = [255, 255, 255],
            center = self.ScenePosition,
            radius = self.AnimatedRadius,
            width = self.BorderThickness,
        )

        if not self.Clicking:
            return

        pygame.draw.circle(
            surface = self.Game.PygameScene.ForegroundSurface,
            color = [255, 255, 255],
            center = self.ScenePosition,
            radius = self.AnimatedRadius - (self.BorderThickness * 2),
        )

    def Update(self, Events, MousePosition):
        ScaledMousePosition = MousePosition / self.Game.Settings.ScreenResolution * self.Game.Settings.SceneResolution

        self.ScenePosition = ScaledMousePosition
        self.WorldPosition = ScaledMousePosition + self.Game.PygameScene.PixelOffset

        self.AnimatedRadius += ((self.MenusRadius if self.Game.Menus.State else self.TargetRadius) - self.AnimatedRadius) * min(25.0 * self.Game.DeltaTime, 1.0)

        for Event in Events:
            if Event.type == MOUSEWHEEL:
                self.TargetRadius = min(max(self.TargetRadius + (Event.y * 5), self.MinRadius), self.MaxRadius)
            
            if Event.type == MOUSEBUTTONDOWN and Event.button == 1:
                self.Clicking = True

            if Event.type == MOUSEBUTTONUP and Event.button == 1:
                self.Clicking = False
