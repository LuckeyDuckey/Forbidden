from ..CppBuild.Simulations import Vec2

import json, os

class SettingsHandler:
    def __init__(self):
        with open(os.path.join(os.getcwd(), "Data/Settings.json"), "r") as File:
            SettingsData = json.load(File)

        # 360p scales cleanly to common resolutions
        self.SceneResolution = Vec2(SettingsData["SceneResolution"])
        self.ScreenResolution = Vec2(SettingsData["ScreenResolution"])

        self.FullScreen = SettingsData["FullScreen"]
        self.AspectRatio = self.SceneResolution.x / self.SceneResolution.y

        self.SoundsVolume = SettingsData["SoundsVolume"]
        self.MusicVolume = SettingsData["MusicVolume"]

        self.ShowDebug = SettingsData["ShowDebug"]
        self.FpsCap = SettingsData["FpsCap"]
