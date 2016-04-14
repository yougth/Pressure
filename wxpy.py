# -*- coding: utf-8 -*-
import wx

class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, 'xingge', size = (300, 200))
        panel = wx.Panel(self)
        self.label =wx.StaticText(panel, -1, 'Text Show Only', (100, 10))
        self.label.Bind(wx.EVT_LEFT_DOWN, self.OnTextClick)
        
        text = wx.TextCtrl(panel, -1, 'Input your name:', (100, 50))
        text.SetInsertionPoint(0)
        
        self.button = wx.Button(panel, -1, 'Btn click', pos = (100, 100))
        self.Bind(wx.EVT_BUTTON, self.OnButtonClick, self.button)

        self.sbar = self.CreateStatusBar()
        self.sbar.SetStatusText('yougth test')

    def OnButtonClick(self, event):
        print 'the button is clicked'

    def OnTextClick(self,event):
        print '......statictext is clicked..'

app = wx.App()
frame = MyFrame()
frame.Show()
app.MainLoop()
