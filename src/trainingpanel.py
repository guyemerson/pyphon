import wx, random
import os, os.path  # needed for picture of chicken
import pyphon
wx.USE_UNICODE = 1

class TrainingPanel(wx.Panel):
	'''
	This is the panel where training happens.
	This is the second panel for the MainWindow. The first panel, MainWindowPanel, is coded in the wxGUI module.
	The user sees four buttons - one for each word, and a "play again"/"next" button in the middle; and a "stop" button in the right bottom corner.
	Pressing "stop" returns to the main panel; the other buttons are used for the training itself.
	There is also now a picture in this panel.
	'''
	def __init__(self, parent, size):
		wx.Panel.__init__(self, parent=parent, size=size)
		"""
		cursor - SQLite3 database cursor object
		language - chosen language for training session
		contrast - chosen contrast for training session
		"""
		self.parent = parent
		self.size = size
		
		# We store all information about test samples in the list self.items
		self.items = []
		
		# Information about the current sample
		self.file = None
		self.answer = None
		self.options = [None, None]
		
		self.SetBackgroundColour('#ededed')
		
		# Sizers (for placing stuff in the panel)
		# The subSizer and the grid fit in the mainSizer, which is the panel's overall sizer
		self.mainSizer = wx.BoxSizer(wx.VERTICAL)
		self.subSizer  = wx.BoxSizer(wx.HORIZONTAL)
		self.grid = wx.GridBagSizer(hgap=20, vgap=5)
		
		# moo is the left button, quack is the right button
		self.moo = wx.Button(self, label="...")
		self.quack = wx.Button(self, label="...")
		self.next = wx.Button(self, label="Play")
		self.stop = wx.Button(self, label="Stop", style=wx.BU_EXACTFIT)
		self.Bind(wx.EVT_BUTTON, self.OnMoo, self.moo)
		self.Bind(wx.EVT_BUTTON, self.OnQuack, self.quack)
		self.Bind(wx.EVT_BUTTON, self.OnNext, self.next)
		self.Bind(wx.EVT_BUTTON, self.OnStop, self.stop)

		self.grid.Add(self.moo, pos=(0,0), span=(1,2))
		self.grid.Add(self.quack, pos=(0,2), span=(1,2))
		self.grid.Add(self.next, pos=(2,1), span=(1,2)) 

		# Picture of chicken
		src_dir = os.getcwd()
		chickenDir = os.path.join(os.path.split(src_dir)[0], 'images/kura.png')
		img = wx.Image(chickenDir, wx.BITMAP_TYPE_PNG)
		
		# make empty image
		self.maxImageSize = 80
		self.image = wx.StaticBitmap(self, bitmap=wx.EmptyBitmap(self.maxImageSize, self.maxImageSize))
		
		# re-size the image (should work for any image, not just this one)
		w = img.GetWidth()
		h = img.GetHeight()
		if w > h:
			newW = self.maxImageSize
			newH = int(self.maxImageSize * float(h)/w)
		else:
			newH = self.maxImageSize
			newW = int(self.maxImageSize * float(w)/h)
		img = img.Scale(newW, newH)

		# put the 'img' picture in the empty 'image' object - this will show the 'img' picture
		self.image.SetBitmap(wx.BitmapFromImage(img))
		# add the image to the grid
		self.grid.Add(self.image, pos=(3,0), span=(2,2))
		
		# subSizer contains stop button, with a 10 pixel border to the bottom and to the right.
		self.subSizer.Add(self.stop, 1, wx.RIGHT | wx.BOTTOM | wx.ALIGN_BOTTOM, 10)
		# mainSizer contains the grid and the subSizer underneath it. The grid has a 50 pixel border from the top.
		self.mainSizer.Add(self.grid, 1, wx.TOP | wx.ALIGN_CENTRE, 50)
		self.mainSizer.Add(self.subSizer, 1, wx.ALIGN_RIGHT, 0)
		self.SetSizerAndFit(self.mainSizer)
		
		self.CentreOnParent()
		
		# Both buttons are disabled at the start. They will be enabled when the user starts the training by pressing the "Next" button, initially labelled "Start".
		self.moo.Disable()
		self.quack.Disable()
		
		# Keyboard shortcuts
		self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
		self.pendingAnswer = False 
		# This variable is needed to stop the user from keeping on getting "correct answers" by pressing the same button many times.
		
			
	# Below - BUTTONS!
	# This is where the action happens
	
	def OnKeyDown(self, event):
		'''
		This is for keyboard shortcuts.
		1 - moo (left button) 
		2 - quack (right button)
		'''
		print ("you pressed a key and the TRAINING PANEL saw it")
		key = event.GetKeyCode() # a code referring to the key you pressed
		keyCharacter = chr(key)  # a string of the key you pressed
		if keyCharacter == "1":
			self.OnChoice(0)    # "moo" (left word)
		elif keyCharacter == "2":
			self.OnChoice(1)    # "quack" (right word)
		elif key == wx.WXK_SPACE:
			self.OnNext()       # "Next"

	
	def OnChoice(self, choice):
		"""
		Button press (left or right word) depending on choice (index in self.options).
		OnMoo and OnQuack methods redirect here.
		"""
		if self.pendingAnswer == False: 
			return # stops people from being able to answer the same question multiple times with button presses
		self.pendingAnswer = False
		print(self.options[choice])
		# Compare user's choice with the correct answer, change stats accordingly
		if self.options[choice] == self.answer:
			self.parent.sessionStats[True] += 1
		else:
			self.parent.sessionStats[False] += 1
		# Colour buttons backgrounds for feedback
		for button in [self.moo, self.quack]:
			if button.Label == self.answer:
				button.SetBackgroundColour((0,255,0)) # green
			else:
				button.SetBackgroundColour((255,0,0)) # red
		print(self.options[choice] == self.answer)
		print(self.parent.sessionStats)
		# Change the buttons
		self.moo.Disable()
		self.quack.Disable()
		self.next.Label = "Play next"
		self.next.SetFocus()
	
	def OnMoo(self, event):
		self.OnChoice(0)
	
	def OnQuack(self, event):
		self.OnChoice(1)
		
		
	def OnNext(self, event):
		'''
		When you press the "Next" button:
		- a new minimal pair is chosen randomly
		- the buttons are relabelled with the new words
		- the buttons' background colour is reset to neutral (grey)
		- the sound is played
		'''
		# allow the user to answer
		if self.pendingAnswer == False:
			self.pendingAnswer = True # this variable stops people from being able to answer the same question many times (by pressing a key)
			
			# reset the background colour of the buttons
			self.moo.SetBackgroundColour(wx.NullColour)
			self.quack.SetBackgroundColour(wx.NullColour)
			
			# Take a random sample, and store it
			filename, item_1, item_2, answer = random.choice(self.items)
			self.file = pyphon.filepath(filename)
			self.options = [item_1, item_2]
			self.answer = answer
			print(self.file)
			print(self.options)
			print(self.answer)
			assert len(self.options) == 2
			
			# Relabel the buttons
			self.moo.Label = self.options[0]
			self.quack.Label = self.options[1]
			self.moo.Enable()
			self.quack.Enable()
			self.next.Label = "Play again"
		
		# Play the file
		wx.Sound(self.file).Play()
	
		
	def OnStop(self, event):
		'''When the "Stop" button is pressed:
		- Reset the trainingpanel to have the same settings as at the beginning (ready for next session)
		- Switch back to MainWindowPanel
		'''
		# Resetting the look
		self.moo.Disable()
		self.quack.Disable()
		self.moo.Label = "..."
		self.quack.Label = "..."
		self.next.Label = "Play"
		self.moo.SetBackgroundColour(wx.NullColour)
		self.quack.SetBackgroundColour(wx.NullColour)
		
		# Resetting the data
		self.file = None
		self.answer = None
		self.options = None
		self.pendingAnswer = False
		
		# Switch to MainWindowPanel
		self.parent.switchMain()
		
	
	def prepareSession(self):
		print(self.parent.language)
		print(self.parent.contrast)
		self.parent.cursor.execute('''SELECT file, item_1, item_2, answer FROM
			((SELECT item_1, item_2 FROM minimal_pairs
				WHERE language = ? AND contrast = ?)
			JOIN (SELECT file, answer FROM recordings
				WHERE language = ?)
			ON item_1 = answer OR item_2 = answer)
			''', (self.parent.language, self.parent.contrast, self.parent.language))
		self.items = list(self.parent.cursor)
		print(self.items)
