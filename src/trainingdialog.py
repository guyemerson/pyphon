# This module contains the TrainingDialog wx GUI object and supporting functions only.

import wx, random, os

srcDir = os.path.expanduser(os.getcwd())
dataDir = os.path.join(os.path.split(srcDir)[0], 'data')
	
def filepath(text):
	"""	If text contains no slashes, add the default data directory	"""
	directory, filename = os.path.split(text)
	if directory == "":
		return os.path.join(dataDir, filename)
	else:
		return text


class TrainingDialog(wx.Dialog):
	'''
	This is the dialogue box where training happens.
	
	The box contains:
	- a panel object (internally coded, below) for organising and positioning widgets (buttons, text etc.)
	
	The panel contains:
	- The buttons and their methods
	'''
	def __init__(self, frame, title, size, cursor, language, contrast):
		wx.Dialog.__init__(self, parent=frame, title=title, size=size)
		
		"""
		cursor - SQLite3 database cursor object
		language - chosen language for training session
		contrast - chosen contrast for training session
		"""
		self.parent = frame
		print(language)
		print(contrast)
		# We store all information about test samples in the list self.items
		cursor.execute('''SELECT file, option_1, option_2, answer FROM
			((SELECT option_1, option_2 FROM minimal_pairs
				WHERE language = ? AND contrast = ?)
			JOIN (SELECT file, answer FROM samples
				WHERE language = ?)
			ON option_1 = answer OR option_2 = answer)
			''', (language, contrast, language))
		
		self.items = list(cursor)
		print(self.items)
		
		# Information about the current sample
		self.file = None
		self.options = [None, None]
		self.answer = None
		
		# Stats for the user's performance
		#self.sessionStats = {True: 0, False: 0} # need to develop this	
		
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
		
		# Keyboard shortcuts
		self.panel.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
				
		# Need to have a way to handle what happens when TrainingWindow closes, i.e.:
		# statistics are stored
		
		
	# Below - BUTTONS!
	# This is where the action happens
	
	def OnKeyUp(self, event):
		print ("you pressed a key")
		key = event.GetKeyCode()
		keyCharacter = chr(key)
		if keyCharacter == "1":
			self.OnMoo(event)
		elif keyCharacter == "2":
			self.OnQuack(event)
	# A space event for Next would also be nice
	# These still need to be (a) idiot-proofed (so they only work at the right time), and (b) the "error bell" needs to be removed
	def OnChoice(self, choice):
		"""
		Button press depending on choice (index in self.options)
		"""
		print(self.options[choice])
		# Compare user's choice with the correct answer
		if self.options[choice] == self.answer:
			self.feedback.SetForegroundColour((0,255,0))
			self.parent.sessionStats[True] += 1
		else:
			self.feedback.SetForegroundColour((255,0,0))
			self.parent.sessionStats[False] += 1
		print(self.options[choice] == self.answer)
		print(self.parent.sessionStats)
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
		filename, option_1, option_2, answer = random.choice(self.items)
		self.file = filepath(filename)
		self.options = [option_1, option_2]
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
		wx.Sound(self.file).Play()
	
		
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
