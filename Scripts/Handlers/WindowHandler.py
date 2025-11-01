import pygame, win32gui, win32con, win32api, ctypes

class WindowHandler:
    # Keep MinWindowSize above 150 to avoid aspect ratio issues
    def __init__(self, AspectRatio = None, MinWindowSize = 150):
        self.WindowHandle = pygame.display.get_wm_info()["window"]
        self.AspectRatio = AspectRatio
        self.WindowBorder = self.GetWindowBorderSize()
        self.MinWindowSize = self.GetMinWindowSize(MinWindowSize)

        self.MovingWindow = False
        self.MovingWindowOffset = None

        self.ResizingWindow = False
        self.ResizingWindowEdge = None
        self.ResizingWindowOrigin = None
        self.ResizingWindowRect = None

        # Disable maximize button
        WindowStyles = win32gui.GetWindowLong(self.WindowHandle, win32con.GWL_STYLE)
        WindowStyles &= ~win32con.WS_MAXIMIZEBOX
        win32gui.SetWindowLong(self.WindowHandle, win32con.GWL_STYLE, WindowStyles)

        self.OriginalWindowProcess = win32gui.SetWindowLong(
            self.WindowHandle,
            win32con.GWL_WNDPROC,
            lambda WindowHandle, MessageId, ParametersW, ParametersL: self.WindowProcess(WindowHandle, MessageId, ParametersW, ParametersL)
        )

    def GetWindowBorderSize(self):
        WindowLeft, WindowTop, WindowRight, WindowBottom = win32gui.GetWindowRect(self.WindowHandle)
        ClientLeft, ClientTop, ClientRight, ClientBottom = win32gui.GetClientRect(self.WindowHandle)

        return [
            (WindowRight - WindowLeft) - ClientRight,
            (WindowBottom - WindowTop) - ClientBottom,
        ]

    def GetMinWindowSize(self, MinWindowSize):
        MinClientWidth = MinWindowSize
        MinClientHeight = MinWindowSize
        
        if self.AspectRatio is not None:
            if MinClientWidth / MinClientHeight < self.AspectRatio:
                MinClientWidth = MinClientHeight * self.AspectRatio
            else:
                MinClientHeight = MinClientWidth / self.AspectRatio
        
        return [
            int(MinClientWidth + self.WindowBorder[0]),
            int(MinClientHeight + self.WindowBorder[1]),
        ]

    def ApplyMinWindowSize(self, WindowLeft, WindowTop, WindowWidth, WindowHeight):
        WidthDifference = max(self.MinWindowSize[0] - WindowWidth, 0)
        HeightDifference = max(self.MinWindowSize[1] - WindowHeight, 0)

        WindowWidth += WidthDifference
        WindowHeight += HeightDifference
        
        if self.ResizingWindowEdge in (win32con.HTTOPLEFT, win32con.HTTOPRIGHT, win32con.HTTOP):
            WindowTop -= HeightDifference
        if self.ResizingWindowEdge in (win32con.HTTOPLEFT, win32con.HTBOTTOMLEFT, win32con.HTLEFT):
            WindowLeft -= WidthDifference

        return WindowLeft, WindowTop, WindowWidth, WindowHeight

    def ApplyAspectRatio(self, WindowLeft, WindowTop, WindowWidth, WindowHeight):
        ClientWidth = WindowWidth - self.WindowBorder[0]
        ClientHeight = WindowHeight - self.WindowBorder[1]

        ScaledWindowWidth = int(ClientHeight * self.AspectRatio) + self.WindowBorder[0]
        ScaledWindowHeight = int(ClientWidth / self.AspectRatio) + self.WindowBorder[1]

        if self.ResizingWindowEdge in (win32con.HTTOP, win32con.HTBOTTOM):
            WindowWidth = ScaledWindowWidth

        elif self.ResizingWindowEdge in (win32con.HTLEFT, win32con.HTRIGHT):
            WindowHeight = ScaledWindowHeight

        else:
            if ClientWidth / ClientHeight > self.AspectRatio:
                WindowHeight = ScaledWindowHeight
            else:
                WindowWidth = ScaledWindowWidth

            # Preserve anchored corner
            if self.ResizingWindowEdge in (win32con.HTTOPLEFT, win32con.HTTOPRIGHT):
                WindowTop += (ClientHeight + self.WindowBorder[1]) - WindowHeight
            if self.ResizingWindowEdge in (win32con.HTTOPLEFT, win32con.HTBOTTOMLEFT):
                WindowLeft += (ClientWidth + self.WindowBorder[0]) - WindowWidth

        return WindowLeft, WindowTop, WindowWidth, WindowHeight

    def WindowProcess(self, WindowHandle, MessageId, ParametersW, ParametersL):
        if MessageId == win32con.WM_NCLBUTTONDOWN:
            WindowLeft, WindowTop, WindowRight, WindowBottom = win32gui.GetWindowRect(self.WindowHandle)
            MousePosition = [
                ctypes.c_short(ParametersL & 0xFFFF).value,
                ctypes.c_short((ParametersL >> 16) & 0xFFFF).value,
            ]

            if ParametersW == win32con.HTCAPTION:
                self.MovingWindow = True
                self.MovingWindowOffset = [
                    MousePosition[0] - WindowLeft,
                    MousePosition[1] - WindowTop,
                ]

            elif ParametersW in (
                win32con.HTLEFT, win32con.HTRIGHT,
                win32con.HTTOP, win32con.HTBOTTOM,
                win32con.HTTOPLEFT, win32con.HTTOPRIGHT,
                win32con.HTBOTTOMLEFT, win32con.HTBOTTOMRIGHT
            ):
                self.ResizingWindow = True
                self.ResizingWindowEdge = ParametersW
                self.ResizingWindowOrigin = MousePosition
                self.ResizingWindowRect = [WindowLeft, WindowTop, WindowRight, WindowBottom]

            else:
                return win32gui.CallWindowProc(self.OriginalWindowProcess, WindowHandle, MessageId, ParametersW, ParametersL)

            win32gui.SetCapture(self.WindowHandle)
            return 0

        elif MessageId == win32con.WM_MOUSEMOVE and (self.MovingWindow or self.ResizingWindow):
            MousePosition = win32api.GetCursorPos()

            if self.MovingWindow:
                WindowLeft = MousePosition[0] - self.MovingWindowOffset[0]
                WindowTop = MousePosition[1] - self.MovingWindowOffset[1]

                win32gui.SetWindowPos(self.WindowHandle, None, WindowLeft, WindowTop, 0, 0, win32con.SWP_NOSIZE | win32con.SWP_NOZORDER)

            elif self.ResizingWindow:
                WindowLeft, WindowTop, WindowRight, WindowBottom = self.ResizingWindowRect

                PositionDifference = [
                    MousePosition[0] - self.ResizingWindowOrigin[0],
                    MousePosition[1] - self.ResizingWindowOrigin[1],
                ]

                if self.ResizingWindowEdge in (win32con.HTLEFT, win32con.HTTOPLEFT, win32con.HTBOTTOMLEFT):
                    WindowLeft += PositionDifference[0]
                if self.ResizingWindowEdge in (win32con.HTRIGHT, win32con.HTTOPRIGHT, win32con.HTBOTTOMRIGHT):
                    WindowRight += PositionDifference[0]
                if self.ResizingWindowEdge in (win32con.HTTOP, win32con.HTTOPLEFT, win32con.HTTOPRIGHT):
                    WindowTop += PositionDifference[1]
                if self.ResizingWindowEdge in (win32con.HTBOTTOM, win32con.HTBOTTOMLEFT, win32con.HTBOTTOMRIGHT):
                    WindowBottom += PositionDifference[1]

                WindowWidth = WindowRight - WindowLeft
                WindowHeight = WindowBottom - WindowTop

                WindowLeft, WindowTop, WindowWidth, WindowHeight = self.ApplyMinWindowSize(WindowLeft, WindowTop, WindowWidth, WindowHeight)

                if self.AspectRatio is not None:
                    WindowLeft, WindowTop, WindowWidth, WindowHeight = self.ApplyAspectRatio(WindowLeft, WindowTop, WindowWidth, WindowHeight)

                win32gui.SetWindowPos(self.WindowHandle, None, WindowLeft, WindowTop, WindowWidth, WindowHeight, win32con.SWP_NOZORDER)

            return 0

        elif MessageId == win32con.WM_LBUTTONUP and (self.MovingWindow or self.ResizingWindow):
            if self.MovingWindow:
                self.MovingWindow = False
                self.MovingWindowOffset = None

            elif self.ResizingWindow:
                self.ResizingWindow = False
                self.ResizingWindowEdge = None
                self.ResizingWindowOrigin = None
                self.ResizingWindowRect = None

            win32gui.ReleaseCapture()
            return 0

        return win32gui.CallWindowProc(self.OriginalWindowProcess, WindowHandle, MessageId, ParametersW, ParametersL)
