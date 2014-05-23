#!/usr/bin/env python2

import wx, os, sys

srcDir = os.getcwd()
dataDir = os.path.join(os.path.split(srcDir)[0], 'data')

import trainingwindow  #, filewindow (to follow)


class MainWindow(wx.Frame):
	def __init__(self, parent, title):
		wx.Frame.__init__(self, parent, title=title, style=(wx.DEFAULT_FRAME_STYLE | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX | wx.WS_EX_CONTEXTHELP), size=(650,600))
		
		self.open = wx.Button(self, label="English")
		self.Bind(wx.EVT_BUTTON, self.OnOpen, self.open)
		
	def OnOpen(self, event):
		secondWindow = trainingwindow.TrainingWindow(None, "hello there")
		secondWindow.Show()


# provider = wx.SimpleHelpProvider()
# wx.HelpProvider_Set(provider)

app = wx.App(False)
frame = MainWindow(None, title="High Variability Phonetic Training software")

# nb = wx.Notebook(frame)
# nb.AddPage(whatever_panel_you_made(nb), "whatever panel name")

frame.Show()
app.MainLoop()