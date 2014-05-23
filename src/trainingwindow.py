# This module contains the TrainingWindow wx GUI object and supporting functions only.

import wx, random, os

# dataPath = "~/git/pyphon/data/"  # This one's for you - COMMENT MINE OUT and COMMENT THIS IN when you run the code
dataPath = "~/Desktop/software/pyphon/data/"
#dataPath = os.getcwd() + "/data/"
# The above is a bit of a hackish solution but I can't think of another way of doing this at the moment
# dataPath = "..\\data\\" # -- doesn't work

### All this stuff...
def answerList():
	return ["Mouse", "Mouth"]
	
wordPairs = {0 : ["mouth", "mouse"], 1 : ["sheep", "ship"]}
numSounds = {"mouth" : 1, "mouse" : 1, "sheep" : 1, "ship" : 1}

def playSound(pair):
	soundName = wordPairs[pair][random.randint(0,1)]
	filename =  soundName + str(random.randint(1,numSounds[soundName]))
	ultimate = dataPath + filename + ".wav"
	print ultimate
	wx.Sound(os.path.expanduser(ultimate)).Play()
	return soundName
	
### ... should be superseded by some cleverer database solution, along the lines of what train.py does.
	

class TrainingWindow(wx.Frame):
	def __init__(self, parent, title):
		self.truth = None
	
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
		
		self.panel = wx.Panel(self, size=(600,650))
		self.panel.SetBackgroundColour('#ededed')

		self.mainSizer = wx.BoxSizer(wx.VERTICAL)
		self.grid = wx.GridBagSizer(hgap=20, vgap=20)
		
		font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
		font.SetPointSize(20)
				
		self.wordBox = wx.StaticText(self.panel, label="a cool title")
		self.wordBox.SetFont(font)
		self.feedback = wx.StaticText(self.panel, label="***")

		self.moo = wx.Button(self.panel, label="Mouse")
		self.quack = wx.Button(self.panel, label="Mouth")
		self.next = wx.Button(self.panel, label="Next")
		self.start = wx.Button(self.panel, label="Start")
		self.Bind(wx.EVT_BUTTON, self.OnMoo, self.moo)
		self.Bind(wx.EVT_BUTTON, self.OnQuack, self.quack)
		self.Bind(wx.EVT_BUTTON, self.OnNext, self.next)
		self.Bind(wx.EVT_BUTTON, self.OnStart, self.start)
		#self.moo.Hide(), self.quack.Hide(), self.next.Hide()

		self.grid.Add(self.wordBox, pos=(1,0))
		self.grid.Add(self.moo, pos=(2,0))
		self.grid.Add(self.quack, pos=(2,2))
		self.grid.Add(self.feedback, pos=(4,3))
		self.grid.Add(self.next, pos=(5,3))
		self.grid.Add(self.start, pos=(6,3))

		self.mainSizer.Add(self.grid, 100, wx.ALL, 100)
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
		
		# Below - BUTTONS!
		# This is where the action happens
		
	def OnMoo(self, event):
		userAnswer = answerList()[0]  # a stand-in. This needs to actually reflect the user's answer
		print self.truth
		if userAnswer == self.truth:
			self.feedback.SetForegroundColour((0,255,0))    # i.e. green
		else:
			self.feedback.SetForegroundColour((255,0,0))    # i.e. red
		self.feedback.Label = self.truth
		self.moo.Hide(), self.quack.Hide(), self.next.Show()
		
	def OnQuack(self, event): # pretty much a repeat of OnMoo
		userAnswer = answerList()[1]
		print self.truth
		if userAnswer == self.truth:
			self.feedback.SetForegroundColour((0,255,0)) 
		else:
			self.feedback.SetForegroundColour((255,0,0))
		self.feedback.Label = self.truth
		self.moo.Hide(), self.quack.Hide(), self.next.Show()
		
	def OnNext(self, event):
		self.moo.Show(), self.quack.Show()
		self.feedback.Label = ""
		self.truth = playSound(0).title()
		
	def OnStart(self, event):
		if self.start.Label == "Start":
			self.start.Label = "Stop"
			self.moo.Show(), self.quack.Show()
			self.truth = playSound(0).title()
		elif self.start.Label == "Stop":
			self.start.Label == "Start"
			self.moo.Hide(), self.quack.Hide(), self.next.Hide()

		# END OF BUTTONS