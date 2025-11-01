from .GameObject import GameObject
from .CppBuild.Simulations import Vec2

import pygame
import moderngl as mgl
from array import array
import numpy as np

class SceneModernGL(GameObject):
    def __init__(self):
        self.Context = mgl.create_context()
        self.QuadBuffer = self.Context.buffer(data=array("f", [
            -1.0, 1.0, 0.0, 1.0,
            1.0, 1.0, 1.0, 1.0,
            -1.0, -1.0, 0.0, 0.0,
            1.0, -1.0, 1.0, 0.0
        ]))

        with open(f"Shaders/Vertex.glsl") as file:
            VertexShader = file.read()
        with open(f"Shaders/SceneFragment.glsl") as file:
            SceneFragmentShader = file.read()
        with open(f"Shaders/ScreenFragment.glsl") as file:
            ScreenFragmentShader = file.read()

        self.SceneProgram = self.Context.program(vertex_shader=VertexShader, fragment_shader=SceneFragmentShader)
        self.SceneRenderObject = self.Context.vertex_array(self.SceneProgram, [(self.QuadBuffer, "2f 2f", "Vertex", "TextureCoordinate")])

        self.ScreenProgram = self.Context.program(vertex_shader=VertexShader, fragment_shader=ScreenFragmentShader)
        self.ScreenRenderObject = self.Context.vertex_array(self.ScreenProgram, [(self.QuadBuffer, "2f 2f", "Vertex", "TextureCoordinate")])

        SceneResolutionInt = [int(self.Game.Settings.SceneResolution.x), int(self.Game.Settings.SceneResolution.y)]

        # Low resolution framebuffer to allow for dynamic screen sizes
        self.SceneTexture = self.Context.texture(SceneResolutionInt, 4)
        self.SceneTexture.filter = (mgl.NEAREST, mgl.NEAREST)
        self.SceneFrameBuffer = self.Context.framebuffer(color_attachments=[self.SceneTexture])

        self.BackgroundTexture = self.CreateTexture(SceneResolutionInt)
        self.MidgroundTexture = self.CreateTexture(SceneResolutionInt)
        self.ForegroundTexture = self.CreateTexture(SceneResolutionInt)
        self.MenusTexture = self.CreateTexture(SceneResolutionInt)

        self.ProgramTime = 0

    def CreateTexture(self, Resolution):
        Texure = self.Context.texture(Resolution, 4)
        Texure.filter = (mgl.NEAREST, mgl.NEAREST)
        Texure.swizzle = "BGRA"
        return Texure

    def Render(self):
        BackgroundSurface, MidgroundSurface, ForegroundSurface, MenusSurface = self.Game.PygameScene.GetLayers()

        # Render to sccene frame buffer
        self.SceneFrameBuffer.use()
        self.Context.viewport = (0, 0, int(self.Game.Settings.SceneResolution[0]), int(self.Game.Settings.SceneResolution[1]))
    
        self.BackgroundTexture.write(pygame.transform.flip(BackgroundSurface, False, True).get_view("1"))
        self.BackgroundTexture.use(0)
        self.SceneProgram["BackgroundTexture"] = 0

        self.MidgroundTexture.write(pygame.transform.flip(MidgroundSurface, False, True).get_view("1"))
        self.MidgroundTexture.use(1)
        self.SceneProgram["MidgroundTexture"] = 1

        self.ForegroundTexture.write(pygame.transform.flip(ForegroundSurface, False, True).get_view("1"))
        self.ForegroundTexture.use(2)
        self.SceneProgram["ForegroundTexture"] = 2

        self.MenusTexture.write(pygame.transform.flip(MenusSurface, False, True).get_view("1"))
        self.MenusTexture.use(3)
        self.SceneProgram["MenusTexture"] = 3

        self.ProgramTime += self.Game.DeltaTime
        self.SceneProgram["Time"] = self.ProgramTime
        self.SceneProgram["Offset"] = self.Game.PygameScene.PixelOffset / self.Game.Settings.SceneResolution

        self.SceneRenderObject.render(mode=mgl.TRIANGLE_STRIP)

        # Upscale scene and render to screen
        self.Context.screen.use()
        self.Context.viewport = (0, 0, int(self.Game.Settings.ScreenResolution[0]), int(self.Game.Settings.ScreenResolution[1]))

        self.SceneTexture.use(0)
        self.ScreenProgram["SceneTexture"] = 0

        self.ScreenRenderObject.render(mode=mgl.TRIANGLE_STRIP)

    def Quit(self):
        self.BackgroundTexture.release()
        self.MidgroundTexture.release()
        self.ForegroundTexture.release()
        self.SceneTexture.release()
        self.SceneFrameBuffer.release()
