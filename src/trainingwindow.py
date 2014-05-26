# This module contains the TrainingWindow wx GUI object and supporting functions only.

import wx, random, os, sqlite3

srcDir = os.getcwd()
dataDir = os.path.join(os.path.split(srcDir)[0], 'data')
datafile = os.path.join(dataDir, 'data.db')

### All this stuff...
def answerList():
	return ["Mouse", "Mouth"]
	
wordPairs = {0 : ["mouth", "mouse"], 1 : ["sheep", "ship"]}
numSounds = {"mouth" : 1, "mouse" : 1, "sheep" : 1, "ship" : 1}

def playSound(pair):
	soundName = wordPairs[pair][random.randint(0,1)]
	filename =  soundName + str(random.randint(1,numSounds[soundName])) + ".wav"
	ultimate = os.path.join(dataDir, filename)
	print ultimate
	wx.Sound(os.path.expanduser(ultimate)).Play()
	return soundName
	
### ... should be superseded by some cleverer database solution, along the lines of what train.py does.
	

class TrainingWindow(wx.Frame):
	'''
	This is the frame (i.e. window) where training happens. Probably the most important frame of all.
	
	The frame contains:
	- a panel object (internally coded, below) for organising and positioning widgets (buttons, text etc.)
	- a "status bar", which is not yet used to its full potential (because I haven't figured out how to give it commands yet)
	
	The panel contains:
	- The buttons and their methods
	
	Database hookup is yet to begin. This is a high priority for development.
	'''
	def __init__(self, parent, title, language, contrast):  # need to incorporate language and contrast
		self.sessionStats = {"attempts" : 0, "correct" : 0} # need to develop this
		self.truth = None
	
		wx.Frame.__init__(self, parent, title=title, style=(wx.DEFAULT_FRAME_STYLE | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX | wx.WS_EX_CONTEXTHELP), size=(300,200))
		# Would be easier if the Frame couldn't be closed using the icon in the corner. Could this be disabled?
		self.CreateStatusBar()   # would be nice to have the status bar show the current stats for the session (like in Anki)
		
		
		# PANEL CODE (sometimes done as separate object, here one object together with frame)
		
		self.panel = wx.Panel(self, size=(300,200))
		self.panel.SetBackgroundColour('#ededed')
		self.mainSizer = wx.BoxSizer(wx.VERTICAL)
		self.grid = wx.GridBagSizer(hgap=5, vgap=5)
		
		self.feedback = wx.StaticText(self.panel, label="")

		self.moo = wx.Button(self.panel, label="Mouse")
		self.quack = wx.Button(self.panel, label="Mouth")
		self.next = wx.Button(self.panel, label="Next")
		self.start = wx.Button(self.panel, label="Start")
		self.Bind(wx.EVT_BUTTON, self.OnMoo, self.moo)
		self.Bind(wx.EVT_BUTTON, self.OnQuack, self.quack)
		self.Bind(wx.EVT_BUTTON, self.OnNext, self.next)
		self.Bind(wx.EVT_BUTTON, self.OnStart, self.start)

		self.grid.Add(self.moo, pos=(1,0))
		self.grid.Add(self.quack, pos=(1,2))
		self.grid.Add(self.feedback, pos=(2,1))
		self.grid.Add(self.next, pos=(3,1))
		self.grid.Add(self.start, pos=(3,2))

		self.mainSizer.Add(self.grid, 0, wx.ALL, 0)
		self.panel.SetSizerAndFit(self.mainSizer)
		
				
		# Need to have a way to handle what happens when TrainingWindow closes, i.e.:
		# 1. statistics are stored
		# 2. MainWindow should return to normal, and you should be able to open a new TrainingWindow
		
		
		# Below - BUTTONS!
		# This is where the action happens
		
	def OnMoo(self, event):
		userAnswer = answerList()[0]  # a stand-in. This needs to actually reflect the user's answer
		# can event.GetString() be used here? (apparently not)
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
		self.next.Hide()
		
	def OnStart(self, event):
		if self.start.Label == "Start":
			self.start.Label = "Stop"
			self.moo.Show(), self.quack.Show()
			self.truth = playSound(0).title()
		elif self.start.Label == "Stop":
			self.start.Label = "Start"
			self.moo.Hide(), self.quack.Hide(), self.next.Hide()
			self.feedback.Label = ""
#			self.feedback.SetForegroundColour((0,0,0))

		# END OF BUTTONS