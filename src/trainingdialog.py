# This module contains the TrainingDialog wx GUI object and supporting functions only.

import wx, random
import pyphon
wx.USE_UNICODE = 1

class TrainingDialog(wx.Dialog):
	'''
	This is the dialogue box where training happens.
	'''
	def __init__(self, parentPanel, title, size, cursor, language, contrast):
		wx.Dialog.__init__(self, parent=parentPanel, title=title, size=size)
		
		"""
		cursor - SQLite3 database cursor object
		language - chosen language for training session
		contrast - chosen contrast for training session
		"""
		self.parent = parentPanel
		self.size = size
		print(language)
		print(contrast)
		# We store all information about test samples in the list self.items
		cursor.execute('''SELECT file, item_1, item_2, answer FROM
			((SELECT item_1, item_2 FROM minimal_pairs
				WHERE language = ? AND contrast = ?)
			JOIN (SELECT file, answer FROM recordings
				WHERE language = ?)
			ON item_1 = answer OR item_2 = answer)
			''', (language, contrast, language))
		self.items = list(cursor)
		print(self.items)
		
		# Information about the current sample
		self.file = None
		self.answer = None
		self.options = [None, None]
		
		# Stats for the user's performance
		#self.sessionStats = {True: 0, False: 0} # need to develop this	
		
		# PANEL CODE
		
		self.panel = wx.Panel(self, size=self.size)
		self.panel.SetBackgroundColour('#ededed')
		self.mainSizer = wx.BoxSizer(wx.VERTICAL)
		self.grid = wx.GridBagSizer(hgap=20, vgap=10)
		
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

		self.grid.Add(self.moo, pos=(1,1), span=(1,2))
		self.grid.Add(self.quack, pos=(1,3), span=(1,2))
		self.grid.Add(self.feedback, pos=(2,2), span=(1,2))
		self.grid.Add(self.next, pos=(3,2), span=(1,2)) 
		self.grid.Add(self.start, pos=(4,3))

		self.mainSizer.Add(self.grid, 0, wx.ALL, 0)
		self.panel.SetSizerAndFit(self.mainSizer)
		
		self.Show() # is this line necessary?
		self.moo.Hide()
		self.quack.Hide()
		self.next.Hide()
		
		# Keyboard shortcuts
		self.panel.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
		self.pendingAnswer = False 
		# This variable is needed to stop the user from keeping on getting "correct answers" by pressing the same button many times.
		
				
		# Need to have a way to handle what happens when TrainingWindow closes, i.e.:
		# 1. statistics are stored
		
		
	# Below - BUTTONS!
	# This is where the action happens
	
	def OnKeyDown(self, event):
		print ("you pressed a key")
		key = event.GetKeyCode()
		keyCharacter = chr(key)
		if keyCharacter == "1":
			self.OnChoice(0)
		elif keyCharacter == "2":
			self.OnChoice(1)
		self.pendingAnswer = False
	# A space event for Next would also be nice

	def OnChoice(self, choice):
		"""
		Button press depending on choice (index in self.options)
		"""
		if self.pendingAnswer == False: return # stops people from being able to answer the same question multiple times with button presses
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
		# allow the user to answer
		self.pendingAnswer = True
		# Take a random sample, and store it
		filename, item_1, item_2, answer = random.choice(self.items)
		#filename, options, answer = random.choice(self.items)
		self.file = pyphon.filepath(filename)
		#self.options = options.split('|', 1)
		self.options = [item_1, item_2]
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
