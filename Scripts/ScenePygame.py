from .GameObject import GameObject
from .CppBuild.Simulations import Vec2

import pygame, os
from pygame.locals import *

class ScenePygame(GameObject):
    def __init__(self):
        self.BackgroundSurface = pygame.Surface(self.Game.Settings.SceneResolution).convert_alpha()
        self.MidgroundSurface = pygame.Surface(self.Game.Settings.SceneResolution).convert_alpha()
        self.ForegroundSurface = pygame.Surface(self.Game.Settings.SceneResolution).convert_alpha()
        self.MenusSurface = pygame.Surface(self.Game.Settings.SceneResolution).convert_alpha()

        self.TargetOffset = Vec2([0, 0])
        self.AnimatedOffset = Vec2([0, 0])
        self.KeysPressed = {"w": False, "s": False, "a": False, "d": False}

        self.MidgroundImage = pygame.image.load(os.path.join(os.getcwd(), "Data/Images/Midground.png")).convert_alpha()
        self.BackgroundImage = pygame.image.load(os.path.join(os.getcwd(), "Data/Images/Background.png")).convert_alpha()

    @property
    def PixelOffset(self):
        return self.AnimatedOffset

    def Update(self, Events):
        self.TargetOffset.Clamp(
            -self.Game.Settings.SceneResolution * Vec2([0.5, 1.0]),
            self.Game.Settings.SceneResolution * Vec2([0.5, 1.0]),
        )

        if self.Game.Menus.State:
            FinalTargetOffset = self.TargetOffset + (self.Game.Mouse.ScenePosition - self.Game.Settings.SceneResolution * 0.5) * 0.1
        else:
            FinalTargetOffset = self.TargetOffset

        self.AnimatedOffset += (FinalTargetOffset - self.AnimatedOffset) * min(5.0 * self.Game.DeltaTime, 1.0)

        for Event in Events:
            if Event.type == KEYDOWN:
                if Event.key == pygame.K_w: self.KeysPressed["w"] = True
                if Event.key == pygame.K_s: self.KeysPressed["s"] = True
                if Event.key == pygame.K_a: self.KeysPressed["a"] = True
                if Event.key == pygame.K_d: self.KeysPressed["d"] = True

            if Event.type == KEYUP:
                if Event.key == pygame.K_w: self.KeysPressed["w"] = False
                if Event.key == pygame.K_s: self.KeysPressed["s"] = False
                if Event.key == pygame.K_a: self.KeysPressed["a"] = False
                if Event.key == pygame.K_d: self.KeysPressed["d"] = False

        if self.Game.Menus.State:
            return

        CameraSpeed = 250 * self.Game.DeltaTime
        
        if self.KeysPressed["w"]: self.TargetOffset.y -= CameraSpeed
        if self.KeysPressed["s"]: self.TargetOffset.y += CameraSpeed
        if self.KeysPressed["a"]: self.TargetOffset.x -= CameraSpeed
        if self.KeysPressed["d"]: self.TargetOffset.x += CameraSpeed

    def Render(self):
        self.BackgroundSurface.fill([0, 0, 0, 0])
        self.MidgroundSurface.fill([0, 0, 0, 0])
        self.ForegroundSurface.fill([0, 0, 0, 0])
        self.MenusSurface.fill([0, 0, 0, 0])

        self.BackgroundSurface.blit(
            source = self.BackgroundImage,
            dest = self.Game.Settings.SceneResolution * Vec2([-0.5, -1.0]) - self.PixelOffset * Vec2([0.8, 1.0]),
        )

        self.MidgroundSurface.blit(
            source = self.MidgroundImage,
            dest = self.Game.Settings.SceneResolution * Vec2([-0.5, -1.0]) - self.PixelOffset * Vec2([0.9, 1.0]),
        )

    def GetLayers(self):
        return self.BackgroundSurface, self.MidgroundSurface, self.ForegroundSurface, self.MenusSurface
