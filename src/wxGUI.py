#!/usr/bin/env python2

import wx, os, random



def answerList():
	return ["Moo", "Quack"]
	
def truth():
	return "Moo"

wordPairs = {0 : ["moo", "quack"], 1 : ["woof", "miao"]}
numSounds = {"moo" : 3, "quack" : 2, "woof" : 2, "miao" : 2}

def playSound(pair):
	soundName = wordPairs[pair][random.randint(0,1)]
	filename =  soundName + str(random.randint(1,numSounds[soundName]))
	wx.Sound(os.path.expanduser("~/Desktop/software/sounds/" + filename + ".wav")).Play()



class MainWindow(wx.Frame):
	def __init__(self, parent, title):
		wx.Frame.__init__(self, parent, title=title, style=(wx.DEFAULT_FRAME_STYLE | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX | wx.WS_EX_CONTEXTHELP), size=(650,600))
		self.CreateStatusBar()
		
		filemenu = wx.Menu()
		helpmenu = wx.Menu()
		
		menuHelp = helpmenu.Append(wx.ID_ANY, "&Help topics", " lalalala")
		menuAbout = helpmenu.Append(wx.ID_ABOUT, "&About", " Information about this program")
		# helpmenu.AppendSeparator() 
		menuExit = filemenu.Append(wx.ID_EXIT, "E&xit", " Terminate the program")
		
		# lots of menu & help menu code can be added here
		
		menuBar = wx.MenuBar()
		menuBar.Append(filemenu, "&File")
		menuBar.Append(helpmenu, "&Help")
		self.SetMenuBar(menuBar)
		
		self.Bind(wx.EVT_MENU, self.OnHelp, menuHelp)
		self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
		self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
		
		# PANEL CODE (sometimes done as separate object, here one object together with frame)
		
		self.panel = wx.Panel(self)
		self.panel.SetBackgroundColour('#ededed')

		self.mainSizer = wx.BoxSizer(wx.VERTICAL)
		self.grid = wx.GridBagSizer(hgap=5, vgap=5)
		
		font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
		font.SetPointSize(20)
				
		self.wordBox = wx.StaticText(self.panel, label="a cool title")
		self.wordBox.SetFont(font)
		self.feedback = wx.StaticText(self.panel, label="***")

		self.moo = wx.Button(self, label="Moo")
		self.quack = wx.Button(self, label="Quack")
		self.next = wx.Button(self, label="Next")
		self.start = wx.Button(self, label="Start")
		self.Bind(wx.EVT_BUTTON, self.OnMoo, self.moo)
		self.Bind(wx.EVT_BUTTON, self.OnQuack, self.quack)
		self.Bind(wx.EVT_BUTTON, self.OnNext, self.next)
		self.Bind(wx.EVT_BUTTON, self.OnStart, self.start)
		#self.moo.Hide(), self.quack.Hide(), self.next.Hide()

		self.grid.Add(self.wordBox, pos=(1,0), span=(1,2))
		self.grid.Add(self.moo, pos=(2,0), span=(1,2))
		self.grid.Add(self.quack, pos=(2,2), span=(1,2))
		self.grid.Add(self.feedback, pos=(4,3), span=(1,1))
		self.grid.Add(self.next, pos=(5,3), span=(1,1))
		self.grid.Add(self.start, pos=(6,3))

		self.mainSizer.Add(self.grid, 0, wx.ALL, 5)
		self.panel.SetSizerAndFit(self.mainSizer)
		
		
	def OnHelp(self, event):
		dlg = wx.MessageDialog(self, "Here is a message.\nEnjoy!", "Help for this program", wx.OK | wx.ICON_INFORMATION)
		dlg.ShowModal()
		dlg.Destroy()
	def OnAbout(self, event):
		dlg = wx.MessageDialog(self, "What's this? Another message?\nWow Stas, you are so full of surprises!", "More fun messages", wx.OK | wx.ICON_INFORMATION)
		dlg.ShowModal()
		dlg.Destroy()
	def OnExit(self, event):
		self.Close(True)
		
	def OnMoo(self, event):
		userAnswer = answerList()[0]
		if userAnswer == truth():
			self.feedback.SetForegroundColour((0,255,0))
		else:
			self.feedback.SetForegroundColour((255,0,0))
		self.feedback.Label = truth()
		self.moo.Hide(), self.quack.Hide(), self.next.Show()
		
	def OnQuack(self, event): # pretty much a repeat of OnMoo
		userAnswer = answerList()[1]
		if userAnswer == truth():
			self.feedback.SetForegroundColour((0,255,0))
		else:
			self.feedback.SetForegroundColour((255,0,0))
		self.feedback.Label = truth()
		self.moo.Hide(), self.quack.Hide(), self.next.Show()
		
	def OnNext(self, event):
		self.moo.Show(), self.quack.Show()
		self.feedback.Label = ""
		playSound(0)
		
	def OnStart(self, event):
		if self.start.Label == "Start":
			self.start.Label = "Stop"
			self.moo.Show(), self.quack.Show()
			playSound(0)
		elif self.start.Label == "Stop":
			self.start.Label == "Start"
			self.moo.Hide(), self.quack.Hide(), self.next.Hide()

# provider = wx.SimpleHelpProvider()
# wx.HelpProvider_Set(provider)

app = wx.App(False)
frame = MainWindow(None, title="High Variability Phonetic Training software")

# nb = wx.Notebook(frame)
# nb.AddPage(whatever_panel_you_made(nb), "whatever panel name")

frame.Show()
app.MainLoop()