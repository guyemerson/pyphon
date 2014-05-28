# This module contains the TrainingWindow wx GUI object and supporting functions only.

import wx, random, os, sqlite3

srcDir = os.path.expanduser(os.getcwd())
dataDir = os.path.join(os.path.split(srcDir)[0], 'data')
datafile = os.path.join(dataDir, 'data.db')
	

class TrainingWindow(wx.Frame):
	'''
	This is the frame (i.e. window) where training happens. Probably the most important frame of all.
	
	The frame contains:
	- a panel object (internally coded, below) for organising and positioning widgets (buttons, text etc.)
	- a "status bar", which is not yet used to its full potential (because I haven't figured out how to give it commands yet)
	
	The panel contains:
	- The buttons and their methods
	'''
	def __init__(self, parent, title, cursor, language, contrast):  # need to incorporate language and contrast
		"""
		cursor - SQL database cursor object
		language - chosen language for training session
		contrast - chosen contrast for training session
		"""
		print(language)
		print(contrast)
		# We store all information about test samples in the list self.items
		cursor.execute("SELECT file, options, answer FROM samples WHERE language = ? AND contrast = ?", (language, contrast))
		self.items = list(cursor)
		print(self.items)
		
		# Information about the current sample
		self.file = None
		self.answer = None
		self.options = []
		
		# Stats for the user's performance
		self.sessionStats = {True: 0, False: 0} # need to develop this
	
		wx.Frame.__init__(self, parent, title=title, style=(wx.DEFAULT_FRAME_STYLE | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX | wx.WS_EX_CONTEXTHELP), size=(300,200))
		# Would be easier if the Frame couldn't be closed using the icon in the corner. Could this be disabled?
		self.CreateStatusBar()   # would be nice to have the status bar show the current stats for the session (like in Anki)
		
		
		# PANEL CODE (sometimes done as separate object, here one object together with frame)
		
		self.panel = wx.Panel(self, size=(300,200))
		self.panel.SetBackgroundColour('#ededed')
		self.mainSizer = wx.BoxSizer(wx.VERTICAL)
		self.grid = wx.GridBagSizer(hgap=5, vgap=5)
		
		self.feedback = wx.StaticText(self.panel, label="")
		
		# moo is the left button, quack is the right button
		self.moo = wx.Button(self.panel, label="")
		self.quack = wx.Button(self.panel, label="")
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
		
		self.Show() # is this line necessary?
		self.moo.Hide()
		self.quack.Hide()
		self.next.Hide()
		
				
		# Need to have a way to handle what happens when TrainingWindow closes, i.e.:
		# 1. statistics are stored
		# 2. MainWindow should return to normal, and you should be able to open a new TrainingWindow
		
		
	# Below - BUTTONS!
	# This is where the action happens
	
	def OnChoice(self, choice):
		"""
		Button press depending on choice (index in self.options)
		"""
		print(self.options[choice])
		# Compare user's choice with the correct answer
		if self.options[choice] == self.answer:
			self.feedback.SetForegroundColour((0,255,0))
			self.sessionStats[True] += 1
		else:
			self.feedback.SetForegroundColour((255,0,0))
			self.sessionStats[False] += 1
		print(self.options[choice] == self.answer)
		print(self.sessionStats)
		# Give feedback to user
		self.feedback.Label = self.answer.title()
		# Change the buttons
		self.moo.Hide()
		self.quack.Hide()
		self.next.Show()
	
	def OnMoo(self, event):
		self.OnChoice(0)
	
	def OnQuack(self, event):
		self.OnChoice(1)
		
		
	def OnNext(self, event):
		# Take a random sample, and store it
		filename, options, answer = random.choice(self.items)
		self.file = filename
		self.options = options.split('|', 1)
		self.answer = answer
		print(self.file)
		print(self.options)
		print(self.answer)
		assert len(self.options) == 2
		# Relabel the buttons
		self.moo.Label = self.options[0].title()
		self.quack.Label = self.options[1].title()
		self.moo.Show()
		self.quack.Show()
		self.feedback.Label = ""
		self.next.Hide()
		# Play the file
		wx.Sound(filename).Play()
	
		
	def OnStart(self, event):
		if self.start.Label == "Start":
			self.start.Label = "Stop"
			self.OnNext(event)
		elif self.start.Label == "Stop":
			self.start.Label = "Start"
			self.moo.Hide()
			self.quack.Hide()
			self.next.Hide()
			self.feedback.Label = ""
			#self.feedback.SetForegroundColour((0,0,0))
	
	# END OF BUTTONS