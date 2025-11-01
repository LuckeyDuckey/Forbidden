import pygame, sys, math, os, time, random
from pygame.locals import *

from Scripts.GameObject import GameObject
from Scripts.CppBuild.Simulations import Vec2
from Scripts.Handlers.SettingsHandler import SettingsHandler
from Scripts.Handlers.WindowHandler import WindowHandler

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Forbidden")

        self.Settings = SettingsHandler()

        if self.Settings.FullScreen:
            self.Screen = pygame.display.set_mode(
                size = self.Settings.ScreenResolution,
                flags = pygame.OPENGL | pygame.DOUBLEBUF | pygame.SCALED | pygame.FULLSCREEN,
            )
            self.Settings.ScreenResolution = Vec2(pygame.display.get_window_size())
        else:
            self.Screen = pygame.display.set_mode(
                size = self.Settings.ScreenResolution,
                flags = pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE,
            )

        self.Window = WindowHandler(self.Settings.AspectRatio, self.Settings.SceneResolution.y)

        self.Clock = pygame.time.Clock()
        self.DeltaTime = 1 / self.Settings.FpsCap
        self.LastTime = time.time()
            
        GameObject.Game = self
        self.LoadGameObjects()

    def LoadGameObjects(self):
        from Scripts.ScenePygame import ScenePygame
        from Scripts.SceneModernGL import SceneModernGL
        from Scripts.Handlers.MouseHandler import MouseHandler
        from Scripts.Handlers.AudioHandler import AudioHandler
        from Scripts.Handlers.MenusHandler import MenusHandler

        self.PygameScene = ScenePygame()
        self.ModernGLScene = SceneModernGL()
        self.Mouse = MouseHandler()
        self.Audio = AudioHandler()
        self.Menus = MenusHandler()

        from Scripts.Simulations.BoatSimulation import BoatSimulation
        from Scripts.Simulations.TerrainSimulation import TerrainSimulation
        from Scripts.Simulations.KelpSimulation import KelpSimulationManager
        from Scripts.Simulations.FishSimulation import FishSimulationManager

        self.Boat = BoatSimulation(
            Position = self.Settings.SceneResolution * 0.5,
            NumberSamplePoints = 5,
        )

        self.OceanFloor = TerrainSimulation(
            Position = self.Settings.SceneResolution * Vec2([-0.5, 2.0]),
            Resolution = Vec2([self.Settings.SceneResolution.x * 2, 50]),
            StepSize = 0.1,
            NumberOfGrassBlades = 200,
        )

        self.KelpManager = KelpSimulationManager(
            NumberOfKelp = 25,
        )

        self.FishManager = FishSimulationManager(
            NumberOfFish = 25,
            BoundsMin = self.Settings.SceneResolution * Vec2([-0.5, 0.55]),
            BoundsMax = self.Settings.SceneResolution * Vec2([1.5, 1.875]),
            BoundsMargin = 25,
        )

    def Run(self):
        while True:
            self.Clock.tick(self.Settings.FpsCap)
            self.DeltaTime = time.time() - self.LastTime
            self.LastTime = time.time()

            PygameEvents = pygame.event.get()

            self.Menus.Update(PygameEvents)
            self.PygameScene.Update(PygameEvents)
            self.Mouse.Update(PygameEvents, Vec2(pygame.mouse.get_pos()))
            self.Audio.Update(PygameEvents)

            self.PygameScene.Render()
            self.Boat.Render()
            self.OceanFloor.Render()
            self.KelpManager.Render()
            self.FishManager.Render()
            self.Menus.Render()
            self.Mouse.Render()
            self.ModernGLScene.Render()

            pygame.display.flip()

            for Event in PygameEvents:
                if Event.type == QUIT:
                    self.ModernGLScene.Quit()
                    pygame.quit()
                    sys.exit()

                if Event.type == pygame.VIDEORESIZE:
                    self.Settings.ScreenResolution = Vec2([Event.w, Event.h])

if __name__ == "__main__":
    Game().Run()
