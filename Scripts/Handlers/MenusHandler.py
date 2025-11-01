from ..GameObject import GameObject
from ..CppBuild.Simulations import Vec2

import pygame, os
from pygame.locals import *

# Title.ttf # 16 + 16n # 16, 32, 48, 64
# Body.ttf # 13 + 13n # 13, 26, 39, 52

class TitleMenu(GameObject):
    def __init__(self, Active):
        self.TitleFont = pygame.font.Font(os.path.join(os.getcwd(), "Data/Fonts/Title.ttf"), 64)
        self.BodyFont = pygame.font.Font(os.path.join(os.getcwd(), "Data/Fonts/Body.ttf"), 13)

        self.TitleImage = self.TitleFont.render("forbidden", False, [255, 255, 255])
        self.TextImage = self.BodyFont.render("press any key to continue", False, [255, 255, 255])

        self.Active = Active

    def Update(self, Events):
        for Event in Events:
            if Event.type == KEYDOWN and self.Active:
                self.Active = False
                self.Game.Audio.MenuSound.play()

    def Render(self):
        self.Game.PygameScene.MenusSurface.blit(
            source = self.TitleImage,
            dest = self.Game.Settings.SceneResolution * Vec2([0.5, 0.45]) - Vec2(self.TitleImage.get_size()) * 0.5,
        )

        self.Game.PygameScene.MenusSurface.blit(
            source = self.TextImage,
            dest = self.Game.Settings.SceneResolution * Vec2([0.5, 0.55]) - Vec2(self.TextImage.get_size()) * 0.5,
        )

class DebugMenu(GameObject):
    def __init__(self, Active):
        self.BodyFont = pygame.font.Font(os.path.join(os.getcwd(), "Data/Fonts/Body.ttf"), 13)
        self.CurrentFrameFps = None

        self.Active = Active

    def Update(self, Events):
        self.CurrentFrameFps = round(self.Game.Clock.get_fps())

    def Render(self):
        FpsTextImage = self.BodyFont.render(f"FPS {str(self.CurrentFrameFps)}", False, [255, 255, 255])
        self.Game.PygameScene.MenusSurface.blit(
            source = FpsTextImage,
            dest = self.Game.Settings.SceneResolution * Vec2([0.025, 0.025]),
        )

class MenusHandler(GameObject):
    def __init__(self):
        self.Menus = {
            "TitleMenu": TitleMenu(True),
            "DebugMenu": DebugMenu(self.Game.Settings.ShowDebug),
        }

    @property
    def State(self):
        return self.Menus["TitleMenu"].Active

    def Update(self, Events):
        for Menu in self.Menus.values():
            Menu.Update(Events)

    def Render(self):
        for Menu in self.Menus.values():
            if not Menu.Active:
                continue
            Menu.Render()
