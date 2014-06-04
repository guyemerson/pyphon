import wx

PANEL_SIZE = (800,600)

class MetadataPanel(wx.Panel):
	def __init__(self, parent, cursor):
		"""
		Panel to view and edit languages, contrasts, and speakers.
		'cursor' should be an SQLite3 database cursor.
		"""
		wx.Panel.__init__(self, parent, size=PANEL_SIZE)
		
		self.SetBackgroundColour('#ededed')
		
		# boxes and headings
		self.languagesHeading = wx.StaticText(self, label="Languages")
		self.contrastsHeading = wx.StaticText(self, label="Contrasts")
		self.speakersHeading = wx.StaticText(self, label="Speakers")
		self.names = ["language", "contrast", "speaker"]
		
		self.languages = wx.ListBox(self, -1)
		self.contrasts = wx.ListBox(self, -1)
		self.speakers =  wx.ListBox(self, -1)
		self.boxes = [self.languages, self.contrasts, self.speakers]
		
		self.addLanguage = wx.Button(self, label="Add langauge")
		self.addContrast = wx.Button(self, label="Add contrast")
		self.addSpeaker  = wx.Button(self, label="Add speaker")

		self.Bind(wx.EVT_LISTBOX, self.OnSelectLanguage, self.languages)
		self.Bind(wx.EVT_LISTBOX_DCLICK, self.OnLanguageExample, self.languages)
		self.Bind(wx.EVT_LISTBOX_DCLICK, self.OnContrastExample, self.contrasts)
		self.Bind(wx.EVT_LISTBOX_DCLICK, self.OnSpeakerExample,  self.speakers)
		
		self.Bind(wx.EVT_BUTTON, self.OnAddLanguage, self.addLanguage)
		self.Bind(wx.EVT_BUTTON, self.OnAddContrast, self.addContrast)
		self.Bind(wx.EVT_BUTTON, self.OnAddSpeaker,  self.addSpeaker)
		
		# Fetch items from database
		cursor.execute("SELECT * FROM language_set")
		self.allLanguages = [x[0] for x in cursor]
		self.allLanguages.sort()
		self.languages.SetItems(self.allLanguages)
		
		self.allContrasts = {x:[] for x in self.allLanguages}
		cursor.execute("SELECT * FROM contrast_set")
		for language, contrast in cursor:
			self.allContrasts[language].append(contrast)
		for language in self.allLanguages:
			self.allContrasts[language].sort()
		
		self.allSpeakers  = {x:[] for x in self.allLanguages}
		cursor.execute("SELECT * FROM speaker_set")
		for language, speaker in cursor:
			self.allSpeakers[language].append(speaker)
		for language in self.allLanguages:
			self.allSpeakers[language].sort()
		
		self.cur = cursor  # We will need the cursor later, when saving changes
		
		
		# grid and mainSizer
		self.mainSizer = wx.BoxSizer(wx.VERTICAL)
		self.grid = wx.GridBagSizer(hgap=5, vgap=5)
		self.grid.Add(self.languagesHeading, pos=(1,1))
		self.grid.Add(self.contrastsHeading, pos=(1,2))
		self.grid.Add(self.speakersHeading,  pos=(1,3))
		self.grid.Add(self.addLanguage, pos=(2,1))
		self.grid.Add(self.addContrast, pos=(2,2))
		self.grid.Add(self.addSpeaker,  pos=(2,3))
		self.grid.Add(self.languages, pos=(3,1))
		self.grid.Add(self.contrasts, pos=(3,2))
		self.grid.Add(self.speakers,  pos=(3,3))
		self.mainSizer.Add(self.grid, 0, wx.ALL, 0)
		self.SetSizerAndFit(self.mainSizer)
		
		# POPUP MENUS
		# Thee popup menus, one for each box
		self.menus = [wx.Menu() for _ in range(3)]
		self.showPopupList = [self.OnShowPopup(i) for i in range(3)]
		self.popupItemSelectedList = [self.OnPopupItemSelected(i) for i in range(3)]
		for i, menu in enumerate(self.menus):
			for text in ["rename", "delete"]: # all three popup menus have the same options, 'delete' and 'rename'
				item = menu.Append(-1, text)
				self.Bind(wx.EVT_MENU, self.popupItemSelectedList[i], item)
			self.boxes[i].Bind(wx.EVT_CONTEXT_MENU, self.showPopupList[i])
	
	# Show popup menus
	def OnShowPopup(self, i):
		def func(event):
			pos = self.ScreenToClient(event.GetPosition())
			self.PopupMenu(self.menus[i], pos)
		return func
	
	# Show dialog box appropriate to listbox clicked
	def OnPopupItemSelected(self, i):
		def func(event):
			item = self.menus[i].FindItemById(event.GetId())
			action = item.GetText()
			self.PopupMenuDialog(i, action)
		return func
		
		# Dialog box from popup menu
	def PopupMenuDialog(self, i, action):
		'''Brings up the dialog box appropriate to the selected option in the context menu.'''
		theBox = self.boxes[i]
		index = theBox.GetSelections()
		sel = theBox.GetString(index[0])
		print index, sel
		if action == "delete":
			dlg = wx.MessageDialog(self, "Really delete item '{}'?".format(sel), "Delete item")
			if dlg.ShowModal() == wx.ID_OK:
				theBox.Delete(index[0])
				del self.allLanguages[sel] # remove from dictionary used in OnSelectLanguage
				self.contrasts.Clear(), self.speakers.Clear() # make blank, since now the corresponding language has been deleted
			dlg.Destroy()
		elif action == "rename":
			dlg = wx.TextEntryDialog(self, "Enter the new name for item '{}' below.".format(sel), "Rename item")
			if dlg.ShowModal() == wx.ID_OK:
				entry = dlg.GetValue()
				newlist = theBox.GetStrings() # all the listbox's current strings
				# replace selected string with user-entered string
				newlist = [entry if x==sel else x for x in newlist]
				if theBox == self.languages:
					# replace key in dict in OnSelectLanguage with user-entered string
					self.allLanguages[entry] = self.allLanguages.pop(sel)
				elif theBox == self.contrasts:
					pass # should change the contrast
				elif theBox == self.speakers:
					pass # should change the speaker
				# rewrite box contents
				theBox.Clear()
				theBox.InsertItems(newlist,0)
			dlg.Destroy()
	# END POPUP MENUS
		
		
	def OnAddLanguage(self, event): self.OnAdd(0)
	def OnAddContrast(self, event): self.OnAdd(1)
	def OnAddSpeaker(self, event):  self.OnAdd(2)
	
	def OnAdd(self, i): # Do we need to protect against people adding lots of "junk" languages which are empty forever?
		'''Adds a language or contrast or speaker to the list.'''
		box = self.boxes[i]
		variable = self.names[i]
		text = wx.GetTextFromUser(message=("Enter a new {}".format(variable)), caption=("New {}".format(variable)), default_value="", parent=None)
		if text != "":
			box.Append(text)
	
	def OnSelectLanguage(self, event):
		'''Gets speakers and contrasts for that language.'''
		index = event.GetSelection()
		language = self.languages.GetString(index)
		print (language)
		self.contrasts.Clear()
		self.speakers.Clear()
		self.contrasts.SetItems(self.allContrasts[language])
		self.speakers.SetItems(self.allSpeakers[language])
		#event.Skip()
	
	def OnLanguageExample(self, event): self.OnExample(0, event.GetSelection())
	def OnContrastExample(self, event): self.OnExample(1, event.GetSelection())
	def OnSpeakerExample(self, event):  self.OnExample(2, event.GetSelection())
	
	def OnExample(self, ref, index):
		'''Plays the sound of that speaker saying a word, or a word in that language, or a pair of contrasting words for that contrast.'''
		whichBox = {0 : self.languages, 1 : self.contrasts, 2 : self.speakers}
		theBox = whichBox[ref]
		play = theBox.GetString(index)
		print ("You just asked for an example of {}".format(play))
		# Finish me, Guy! :)
