from ..GameObject import GameObject

import pygame, os, random
from pygame.locals import *

pygame.mixer.init()

class LoopingSound(GameObject):
    # Leave channel 0 open for non looping sounds
    def __init__(self, SoundPath, BaseVolume = 1.0, CrossfadeDuration = 2.0, ChannelOne = 0, ChannelTwo = 1):
        self.Sound = pygame.mixer.Sound(SoundPath)
        self.BaseVolume = BaseVolume
        
        self.CrossfadeDuration = CrossfadeDuration
        self.SoundLength = self.Sound.get_length()

        self.ActiveChannel = pygame.mixer.Channel(ChannelOne)
        self.PausedChannel = pygame.mixer.Channel(ChannelTwo)

        self.SoundTime = 0.0
        self.ActiveChannel.play(self.Sound)

    def Update(self, Volume):
        self.SoundTime += self.Game.DeltaTime

        self.ActiveChannel.set_volume(self.BaseVolume * self.Game.Settings.SoundsVolume * Volume)
        self.PausedChannel.set_volume(self.BaseVolume * self.Game.Settings.SoundsVolume * Volume)
        
        if self.SoundTime < self.SoundLength - self.CrossfadeDuration:
            return
        
        self.PausedChannel.play(self.Sound, fade_ms = int(self.CrossfadeDuration * 1000))
        self.ActiveChannel.fadeout(int(self.CrossfadeDuration * 1000))

        self.ActiveChannel, self.PausedChannel = self.PausedChannel, self.ActiveChannel
        self.SoundTime = 0.0

class MusicHandler(GameObject):
    def __init__(self, Tracks):
        self.Tracks = random.sample(Tracks, len(Tracks))
        self.CurrentTrackIndex = 0

        self.TrackEndEvent = pygame.USEREVENT + 1
        pygame.mixer.music.set_endevent(self.TrackEndEvent)

        self.PlayTrack()

    def PlayTrack(self):
        CurrentTrack = self.Tracks[self.CurrentTrackIndex]

        pygame.mixer.music.load(CurrentTrack["FilePath"])
        pygame.mixer.music.set_volume(CurrentTrack["BaseVolume"] * self.Game.Settings.MusicVolume)
        pygame.mixer.music.play(0)

    def Update(self, PygameEvents):
        for Event in PygameEvents:
            if Event.type == self.TrackEndEvent:
                self.CurrentTrackIndex = (self.CurrentTrackIndex + 1) % len(self.Tracks)
                self.PlayTrack()

class AudioHandler(GameObject):
    def __init__(self):
        self.SurfaceOceanSound = LoopingSound(
            SoundPath = os.path.join(os.getcwd(), "Data/Sounds/SurfaceOcean.ogg"),
            BaseVolume = 1.0,
            CrossfadeDuration = 2.0,
            ChannelOne = 1,
            ChannelTwo = 2,
        )
        self.UnderwaterOceanSound = LoopingSound(
            SoundPath = os.path.join(os.getcwd(), "Data/Sounds/UnderwaterOcean.ogg"),
            BaseVolume = 0.6,
            CrossfadeDuration = 2.0,
            ChannelOne = 3,
            ChannelTwo = 4,
        )
        self.WindSound = LoopingSound(
            SoundPath = os.path.join(os.getcwd(), "Data/Sounds/Wind.ogg"),
            BaseVolume = 0.25,
            CrossfadeDuration = 2.0,
            ChannelOne = 5,
            ChannelTwo = 6,
        )

        self.MenuSound = pygame.mixer.Sound(os.path.join(os.getcwd(), "Data/Sounds/Menu.ogg"))
        self.MenuSoundBaseVolume = 1.0

        self.Music = MusicHandler([
            {"FilePath": os.path.join(os.getcwd(), "Data/Music/DiesIrae.ogg"), "BaseVolume": 0.2},
            {"FilePath": os.path.join(os.getcwd(), "Data/Music/AntiphonaCrucemSanctamSubiit.ogg"), "BaseVolume": 0.2},
            {"FilePath": os.path.join(os.getcwd(), "Data/Music/AntiphonaSalveRegina.ogg"), "BaseVolume": 0.2},
        ])

    def Update(self, PygameEvents):
        self.Music.Update(PygameEvents)
        self.MenuSound.set_volume(self.MenuSoundBaseVolume * self.Game.Settings.SoundsVolume)

        OceanDepth = min(max(0.5 + self.Game.PygameScene.PixelOffset.y / self.Game.Settings.SceneResolution.y, 0), 1)

        self.SurfaceOceanSound.Update(1 - OceanDepth)
        self.UnderwaterOceanSound.Update(OceanDepth)
        self.WindSound.Update(1 - OceanDepth)
