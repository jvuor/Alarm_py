import wx

DEFAULT_TIMER = 15  # Length of the timer in minutes


class AlarmFrame(wx.Frame):
    """
    The window for the alarm clock
    """

    def __init__(self, *args, **kw):
        super(AlarmFrame, self).__init__(*args, **kw)

        self.Bind(wx.EVT_MOTION, self.OnMouse)

        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)

        self.start_time = wx.TimeSpan()         # Misusing(?) the TimeSpan class for the timer
        self.start_time = self.start_time.Minutes(DEFAULT_TIMER)

        self.timer = wx.Timer(self)             # Setup the timer event
        self.Bind(wx.EVT_TIMER, self.OnTimer)
        self.timer.Start(1000)                  # Execute every 1000 ms = every second

        self.blinkPhase = 0
        self.timerNotZero = True

        sizer = wx.BoxSizer(wx.VERTICAL)            # making a sizer for the window layout

        sizer.Add(wx.StaticText(self, label=self.start_time.Format("%M:%S")),  0, wx.LEFT|wx.RIGHT|wx.TOP, border=10)

        self.timertext = sizer.Children[0].GetWindow()      # a direct reference to the text element

        font = self.timertext.GetFont()
        font.PointSize += 30
        font = font.Bold()
        self.timertext.SetFont(font)
        self.timertext.SetBackgroundColour('white')

        buttonsizer = wx.BoxSizer(wx.HORIZONTAL)

        # Buttons, 1 - reset 2 - pause 3 - shutdown
        buttonsizer.Add(wx.Button(self, size=(30, 30), name="Button1"))
        buttonsizer.AddSpacer(15)
        self.button1 = buttonsizer.Children[0].GetWindow()
        buttonsizer.Add(wx.Button(self, size=(30, 30), name="Button2"))
        buttonsizer.AddSpacer(15)
        self.button2 = buttonsizer.Children[2].GetWindow()
        self.button1.SetBitmap(LoadIcon("reset"))
        self.button2play = LoadIcon("play")                  # Saving the icons for quickswapping
        self.button2pause = LoadIcon("pause")
        self.button2.SetBitmap(self.button2pause)
        buttonsizer.Add(wx.Button(self, size=(30, 30), name="Button3"))
        buttonsizer.Children[4].GetWindow().SetBitmap(LoadIcon("close"))

        self.button1.SetBackgroundColour('white')
        self.button2.SetBackgroundColour('white')
        buttonsizer.Children[4].GetWindow().SetBackgroundColour('white')

        self.Bind(wx.EVT_BUTTON, self.OnButton)     # Button event

        sizer.Add(buttonsizer, 0, wx.ALIGN_CENTER)
        sizer.AddSpacer(5)

        self.Bind(wx.EVT_MOTION, self.OnMouse)
        self.timertext.Bind(wx.EVT_MOTION, self.OnMouse)

        sizer.SetSizeHints(self)

        self.SetSizer(sizer)
        self.SetRoundShape()
        self.Layout()

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
                self.timertext.SetForegroundColour('red')
                self.timertext.SetLabel("00:00")
                self.blinkPhase = 1
            elif self.blinkPhase == 1:
                self.timertext.SetForegroundColour('black')
                self.timertext.SetLabel("00:00")
                self.blinkPhase = 0

    def OnButton(self, event):
        """Handler for button event, redirects to button handlers"""
        button = event.GetEventObject().GetName()
        if button == "Button1":
            self.OnButton1()
        elif button == "Button2":
            self.OnButton2()
        elif button == "Button3":
            self.OnExit(event)

    def OnButton1(self):
        """Handler for reset button"""
        self.start_time = self.start_time.Minutes(DEFAULT_TIMER)
        self.timertext.SetLabel(self.start_time.Format("%M:%S"))
        self.timerNotZero = True
        self.blinkPhase = 0
        self.timertext.SetForegroundColour('black')
        self.button1.SetBackgroundColour('white')

    def OnButton2(self):
        """Handler for pause button"""
        if self.timer.IsRunning() & self.timerNotZero:
            self.timer.Stop()
            self.button2.SetBitmap(self.button2play)
        elif self.timerNotZero:
            self.timer.Start()
            self.button2.SetBitmap(self.button2pause)

    def OnMouse(self, event):
        if not event.Dragging():
            self._dragPos = None
            if self.HasCapture():
                self.ReleaseMouse()
                return
        else:
            if not self.HasCapture():
                self.CaptureMouse()  # only capture it once

            if not self._dragPos:
                self._dragPos = event.GetPosition()
            else:
                pos = event.GetPosition()
                displacement = self._dragPos - pos
                self.SetPosition(self.GetPosition() - displacement)

    def OnEraseBackground(self, event):
        """
        Add a picture to the background
        """

        dc = wx.ClientDC(self)

        if not dc:
            dc = wx.ClientDC(self)
            rect = self.GetUpdateRegion().GetBox()
            dc.SetClippingRect(rect)

        bmp = wx.Bitmap("bg.png", wx.BITMAP_TYPE_PNG)

        dc.DrawBitmap(bmp, 0, 0, 0)

    def SetRoundShape(self, event=None):
        w, h = self.GetSize()
        self.SetShape(GetRoundShape(w, h, 10))

    def OnExit(self, event):
        """Window closing button pressed, shutting down"""
        self.Close(True)


def LoadIcon(filename):
    """Loads icon files by name, returns wx.BitMaps"""
    # wx.Image.AddHandler(wx.PNGHandler)             # This should work but it doesn't so...
    wx.InitAllImageHandlers()                        # ...falling back to this instead

    filename = "icons/" + filename + ".png"
    image = wx.Image()

    with open(filename, mode='rb') as file:
        image.LoadFile(file, type=wx.BITMAP_TYPE_PNG)

    return image.ConvertToBitmap()


def GetRoundBitmap( w, h, r ):
    """
    Stolen from https://hasenj.wordpress.com/2009/04/14/making-a-fancy-window-in-wxpython/
    """
    maskColor = wx.Colour(0,0,0)
    shownColor = wx.Colour(5,5,5)
    b = wx.Bitmap(w,h)
    dc = wx.MemoryDC(b)
    dc.SetBrush(wx.Brush(maskColor))
    dc.DrawRectangle(0,0,w,h)
    dc.SetBrush(wx.Brush(shownColor))
    dc.SetPen(wx.Pen(shownColor))
    dc.DrawRoundedRectangle(0,0,w,h,r)
    dc.SelectObject(wx.NullBitmap)
    b.SetMaskColour(maskColor)
    return b


def GetRoundShape( w, h, r ):
    return wx.Region( GetRoundBitmap(w,h,r) )


if __name__ == '__main__':
    # Setup the window and show it
    app = wx.App()

    display = wx.DisplaySize()      # Let's put the app in the bottom right corner by default
    place = display[0] - 300, display[1] - 200

    frame = AlarmFrame(None, title="Alarmpy", size=(230, 125), pos=place, style=wx.BORDER_NONE | wx.STAY_ON_TOP | wx.FRAME_SHAPED)

    frame.Show()
    app.MainLoop()