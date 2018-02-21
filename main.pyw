import wx

DEFAULT_TIMER = 20 #Length of the timer in minutes

class AlarmFrame(wx.Frame):
    """
    The window for the alarm clock
    """

    def __init__(self, *args, **kw):
        super(AlarmFrame, self).__init__(*args, **kw)

        self.start_time = wx.TimeSpan()         # Misusing(?) the TimeSpan class for the timer
        self.start_time = self.start_time.Minutes(DEFAULT_TIMER)

        self.timer = wx.Timer(self)             # Setup the timer event
        self.Bind(wx.EVT_TIMER, self.OnTimer)
        self.timer.Start(1000)                  # Execute every 1000 ms = every second

        self.blinkPhase = 0
        self.timerNotZero = True

        panel = wx.Panel(self)                  # Setup the window layout
        self.timertext = wx.StaticText(panel, label=self.start_time.Format("%M:%S"), pos=(10, -5))
        font = self.timertext.GetFont()
        font.PointSize += 40
        font = font.Bold()
        self.timertext.SetFont(font)

        self.button1 = wx.Button(panel, pos = (180, 5), size = (30,30), name="Button1")  # Buttons, 1 - reset 2 - pause
        self.button1.SetBitmap(LoadIcon("reset"))
        self.button2 = wx.Button(panel, pos = (180, 45), size = (30,30), name="Button2")
        self.button2play = LoadIcon("play")                  # Saving the icons for quickswapping
        self.button2pause = LoadIcon("pause")
        self.button2.SetBitmap(self.button2pause)

        self.Bind(wx.EVT_BUTTON, self.OnButton)     # Button event

    def OnTimer(self, event):
        """Handler for timer event"""
        if self.timerNotZero:           # When timer runs, subtract one second and update text
            self.start_time = self.start_time.Subtract(wx.TimeSpan(0, sec = 1))
            self.timertext.SetLabel(self.start_time.Format("%M:%S"))
            if self.start_time.GetMinutes() == 0 and self.start_time.GetSeconds() == 0:     # Timer reached zero
                self.timerNotZero = False
                self.button1.SetBackgroundColour('red')
        else:                               # Once timer stop, makes the text background blink red
            if self.blinkPhase == 0:
                self.timertext.SetBackgroundColour('red')
                self.timertext.SetLabel("--:--")
                self.blinkPhase = 1
            elif self.blinkPhase == 1:
                self.timertext.SetBackgroundColour(wx.NullColour)
                self.timertext.SetLabel("--:--")
                self.blinkPhase = 0

    def OnButton(self, event):
        """Handler for button event, redirects to button handlers"""
        button = event.GetEventObject().GetName()
        if button == "Button1":
            self.OnButton1()
        elif button == "Button2":
            self.OnButton2()

    def OnButton1(self):
        """Handler for reset button"""
        self.start_time = self.start_time.Minutes(DEFAULT_TIMER)
        self.timertext.SetLabel(self.start_time.Format("%M:%S"))
        self.timerNotZero = True
        self.blinkPhase = 0
        self.timertext.SetBackgroundColour(wx.NullColour)
        self.button1.SetBackgroundColour(wx.NullColour)

    def OnButton2(self):
        """Handler for pause button"""
        if self.timer.IsRunning() & self.timerNotZero:
            self.timer.Stop()
            self.button2.SetBitmap(self.button2play)
        elif self.timerNotZero:
            self.timer.Start()
            self.button2.SetBitmap(self.button2pause)

    def OnExit(self, event):
        """Window closing button pressed, shutting down"""
        self.Close(True)


def LoadIcon(filename):
    """Loads icon files by name"""
    #wx.Image.AddHandler(wx.PNGHandler)             # This should work but it doesn't so...
    wx.InitAllImageHandlers()                       # ...falling back to this instead

    filename = "icons/" + filename + ".png"
    image = wx.Image()

    with open(filename, mode='rb') as file:
        image.LoadFile(file, type=wx.BITMAP_TYPE_PNG)

    return image.ConvertToBitmap()

if __name__ == '__main__':
    # Setup the window and show it
    app = wx.App()

    display = wx.DisplaySize()      # Let's put the app in the bottom right corner by default
    place = display[0] - 300, display[1] - 200

    frame = AlarmFrame(None, title="Alarmpy", size=wx.Size(230,120), pos = place,
                       style = wx.DEFAULT_FRAME_STYLE & \
                               ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX) | wx.STAY_ON_TOP)
    # Window style : no resizing, always on top, no maximize/minimize buttons

    frame.Show()
    app.MainLoop()