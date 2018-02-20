import wx

DEFAULT_TIMER = 15 #Length of the timer in minutes

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
        self.st = wx.StaticText(panel, label=self.start_time.Format("%M:%S"), pos=(10, 0))
        font = self.st.GetFont()
        font.PointSize += 40
        font = font.Bold()
        self.st.SetFont(font)

        self.button1 = wx.Button(panel, pos = (180,10), size = (30,30), label="O", name="Button1")  #Buttons, 1 - reset 2 - pause
        self.button2 = wx.Button(panel, pos = (180,50), size = (30,30), label="II", name="Button2")

        self.Bind(wx.EVT_BUTTON, self.OnButton)     # Button event

    def OnTimer(self, event):
        """Handler for timer event"""
        if self.timerNotZero:           # When timer runs, subtract one second and update text
            self.start_time = self.start_time.Subtract(wx.TimeSpan(0, sec = 1))
            self.st.SetLabel(self.start_time.Format("%M:%S"))
            if self.start_time.GetMinutes() == 0 and self.start_time.GetSeconds() == 0:     # We've reached zero
                self.timerNotZero = False
        else:                               # Once timer stop, makes the text background blink red
            if self.blinkPhase == 0:
                self.st.SetBackgroundColour('red')
                self.st.SetLabel("--:--")
                self.blinkPhase = 1
            elif self.blinkPhase == 1:
                self.st.SetBackgroundColour(wx.NullColour)
                self.st.SetLabel("--:--")
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
        self.st.SetLabel(self.start_time.Format("%M:%S"))
        self.timerNotZero = True
        self.blinkPhase = 0
        self.st.SetBackgroundColour(wx.NullColour)

    def OnButton2(self):
        """Handler for pause button"""
        if self.timer.IsRunning() & self.timerNotZero:
            self.timer.Stop()
            self.button2.SetLabel(">")      # Check out the cool ascii art (TODO: use icons instead)
        elif self.timerNotZero:
            self.timer.Start()
            self.button2.SetLabel("II")

    def OnExit(self, event):
        """Window closing button pressed, shutting down"""
        self.Close(True)

if __name__ == '__main__':
    # Setup the window and show it
    app = wx.App()

    display = wx.DisplaySize()      # Let's put the app in the bottom right corner by default
    place = display[0] - 300, display[1] - 200

    frame = AlarmFrame(None, title="Alarmpy", size=wx.Size(230,130), pos = place, style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX) | wx.STAY_ON_TOP)
    # Window style : no resizing, always on top, no maximize/minimize buttons

    frame.Show()
    app.MainLoop()