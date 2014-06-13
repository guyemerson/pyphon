import wx
wx.USE_UNICODE = 1

PANEL_SIZE = (800,600)

class MetadataPanel(wx.Panel):
	def __init__(self, parent):
		"""
		Panel to view and edit languages, contrasts, and speakers.
		'cursor' should be an SQLite3 database cursor.
		"""
		wx.Panel.__init__(self, parent, size=PANEL_SIZE)
		
		self.SetBackgroundColour('#ededed')
		
		# boxes and headings
		self.languagesHeading = wx.StaticText(self, label=u"Languages")
		self.contrastsHeading = wx.StaticText(self, label=u"Contrasts")
		self.speakersHeading = wx.StaticText(self, label=u"Speakers")
		self.names = [u"language", u"contrast", u"speaker"]
		
		self.languages = wx.ListBox(self, size=(150,200))
		self.contrasts = wx.ListBox(self, size=(150,200))
		self.speakers =  wx.ListBox(self, size=(150,200))
		self.boxes = [self.languages, self.contrasts, self.speakers]
		
		self.addLanguage = wx.Button(self, label=u"Add language")
		self.addContrast = wx.Button(self, label=u"Add contrast")
		self.addSpeaker  = wx.Button(self, label=u"Add speaker")

		self.Bind(wx.EVT_LISTBOX, self.OnSelectLanguage, self.languages)
		self.Bind(wx.EVT_LISTBOX_DCLICK, self.OnLanguageExample, self.languages)
		self.Bind(wx.EVT_LISTBOX_DCLICK, self.OnContrastExample, self.contrasts)
		self.Bind(wx.EVT_LISTBOX_DCLICK, self.OnSpeakerExample,  self.speakers)
		
		self.Bind(wx.EVT_BUTTON, self.OnAddLanguage, self.addLanguage)
		self.Bind(wx.EVT_BUTTON, self.OnAddContrast, self.addContrast)
		self.Bind(wx.EVT_BUTTON, self.OnAddSpeaker,  self.addSpeaker)
		
		# Fetch items from database
		self.cursor = parent.cursor
		self.metaData = parent.metaData
		self.tables = (u"language_set", u"contrast_set", u"speaker_set")
		self.allLanguages, self.allContrasts, self.allSpeakers = self.metaData
		
		self.languages.SetItems(self.allLanguages)
		
		
		# grid and mainSizer
		self.mainSizer = wx.BoxSizer(wx.VERTICAL)
		self.grid = wx.GridBagSizer(hgap=20, vgap=5)
		self.grid.Add(self.languagesHeading, pos=(1,0))
		self.grid.Add(self.contrastsHeading, pos=(1,1))
		self.grid.Add(self.speakersHeading,  pos=(1,2))
		self.grid.Add(self.addLanguage, pos=(3,0))
		self.grid.Add(self.addContrast, pos=(3,1))
		self.grid.Add(self.addSpeaker,  pos=(3,2))
		self.grid.Add(self.languages, pos=(2,0))
		self.grid.Add(self.contrasts, pos=(2,1))
		self.grid.Add(self.speakers,  pos=(2,2))
		self.mainSizer.Add(self.grid, 0, wx.ALL | wx.ALIGN_CENTRE, 0)
		self.SetSizerAndFit(self.mainSizer)
		
		# POPUP MENUS
		# Thee popup menus, one for each box
		self.menus = [wx.Menu() for _ in range(3)]
		self.showPopupList = [self.OnShowPopup(i) for i in range(3)]
		self.popupItemSelectedList = [self.OnPopupItemSelected(i) for i in range(3)]
		self.popupOptions = (u"rename", u"delete") # all three popup menus have the same options, 'delete' and 'rename'
		for i, menu in enumerate(self.menus):
			for text in self.popupOptions:
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
		index = theBox.GetSelections()[0]
		selection = theBox.GetString(index)
		print index, selection
		
		if action == u"delete":
			dlg = wx.MessageDialog(self, u"Really delete item '{}'?".format(selection), u"Delete item")
			if dlg.ShowModal() == wx.ID_OK:
				theBox.Delete(index)
				# Remove from python dictionary and from database:
				if i == 0:
					del self.allLanguages[index]
					del self.allContrasts[selection]
					del self.allSpeakers[selection]
					self.cursor.execute(u"DELETE FROM language_set WHERE language = ?", (selection,))
					self.contrasts.Clear()
					self.speakers.Clear()
				else:
					del self.metaData[i][self.chosenLanguage][index]
					self.cursor.execute(u"DELETE FROM {} WHERE language = ? AND {} = ?".format(self.tables[i], self.names[i]), (self.chosenLanguage, selection))
			dlg.Destroy()
		
		elif action == u"rename":
			dlg = wx.TextEntryDialog(self, u"Enter the new name for item '{}' below.".format(selection), u"Rename item")
			if dlg.ShowModal() == wx.ID_OK:
				entry = dlg.GetValue()
				newlist = theBox.GetStrings() # all the listbox's current strings
				# replace selected string with user-entered string
				newlist = [entry if x == selection else x for x in newlist]
				
				if i == 0:
					self.allLanguages[index] = entry
					self.allContrasts[entry] = self.allContrasts.pop(selection)
					self.allSpeakers[entry]  = self.allSpeakers.pop(selection)
					self.chosenLanguage = entry
					self.cursor.execute(u"UPDATE language_set SET language = ? WHERE language = ?", (entry, selection))
				else:
					self.metaData[i][self.chosenLanguage][index] = entry
					self.cursor.execute(u"UPDATE {0} SET {1} = ? WHERE language = ? AND {1} = ?".format(self.tables[i], self.names[i]), (entry, self.chosenLanguage, selection))
				
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
		text = wx.GetTextFromUser(message=(u"Enter a new {}".format(variable)), caption=(u"New {}".format(variable)), default_value="", parent=None)
		if text != u"":
			box.Append(text)
			if i == 0:
				self.allLanguages.append(text)
				self.allContrasts[text] = []
				self.allSpeakers[text] = []
				self.cursor.execute(u"INSERT INTO language_set VALUES (?)", (text,))
			else:
				self.metaData[i][self.chosenLanguage].append(text)
				self.cursor.execute(u"INSERT INTO {} VALUES (?, ?)".format(self.tables[i]), (self.chosenLanguage, text))
	
	def OnSelectLanguage(self, event):
		'''Gets speakers and contrasts for that language.'''
		index = event.GetSelection()
		self.chosenLanguage = self.languages.GetString(index)
		print (self.chosenLanguage)
		self.contrasts.Clear()
		self.speakers.Clear()
		self.contrasts.SetItems(self.allContrasts[self.chosenLanguage])
		self.speakers.SetItems(self.allSpeakers[self.chosenLanguage])
		#event.Skip()
	
	def OnLanguageExample(self, event): self.OnExample(0, event.GetSelection())
	def OnContrastExample(self, event): self.OnExample(1, event.GetSelection())
	def OnSpeakerExample(self, event):  self.OnExample(2, event.GetSelection())
	
	def OnExample(self, i, index):
		'''Plays the sound of that speaker saying a word, or a word in that language, or a pair of contrasting words for that contrast.'''
		theBox = self.boxes[i]
		play = theBox.GetString(index)
		print (u"You just asked for an example of {}".format(play))
		# Finish me, Guy! :)
