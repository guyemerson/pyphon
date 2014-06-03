import wx

panelSize = (800,600)

class MetadataPanel(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, size=panelSize)
		
		self.SetBackgroundColour('#ededed')
		
		# lists and headings
		self.languagesHeading = wx.StaticText(self, label="Languages")
		self.contrastsHeading = wx.StaticText(self, label="Contrasts")
		self.speakersHeading = wx.StaticText(self, label="Speakers")
		self.languages = wx.ListBox(self, -1)
		self.contrasts = wx.ListBox(self, -1)
		self.speakers =  wx.ListBox(self, -1)
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
		
		# toy inputs - to be done in a clever database way
		self.allLanguages = {"Burmese" : [["q-x", "f-j"], ["Barack Obama"]], "Svan" : [["o-u", "gh-grh"], ["Guy Emerson", "Stanislaw Pstrokonski"]], "Catalan" : [["f-v"], ["James Bond", "Lord Martin Rees"]]}
		for i in self.allLanguages:
			self.languages.Append(i)
		
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
		# Terribly unwieldy code (should use e.g. iteration if poss) but it does the trick
		# Thee popup menus, one for each box
		self.languagePopupmenu = wx.Menu()
		self.contrastPopupmenu = wx.Menu()
		self.speakerPopupmenu = wx.Menu()
		for text in "rename delete".split(): # all three popup menus have the same options, 'delete' and 'rename'
			item1 = self.languagePopupmenu.Append(-1, text)
			item2 = self.contrastPopupmenu.Append(-1, text)
			item3 = self.speakerPopupmenu.Append(-1, text)
			self.Bind(wx.EVT_MENU, self.OnLanguagePopupItemSelected, item1)
			self.Bind(wx.EVT_MENU, self.OnContrastPopupItemSelected, item2)
			self.Bind(wx.EVT_MENU, self.OnSpeakerPopupItemSelected, item3)
		self.languages.Bind(wx.EVT_CONTEXT_MENU, self.OnShowLanguagePopup)
		self.contrasts.Bind(wx.EVT_CONTEXT_MENU, self.OnShowContrastPopup)
		self.speakers.Bind(wx.EVT_CONTEXT_MENU, self.OnShowSpeakerPopup)
        
        # Show popup menus
	def OnShowLanguagePopup(self, event): 
		pos = self.ScreenToClient(event.GetPosition())
		self.PopupMenu(self.languagePopupmenu, pos)
	def OnShowContrastPopup(self, event):
		pos = self.ScreenToClient(event.GetPosition())
		self.PopupMenu(self.contrastPopupmenu, pos)
	def OnShowSpeakerPopup(self, event):
		pos = self.ScreenToClient(event.GetPosition())
		self.PopupMenu(self.speakerPopupmenu, pos)

		# Show dialog box appropriate to listbox clicked
	def OnLanguagePopupItemSelected(self, event):
		self.OnPopupItemSelected(ref=0, item=self.languagePopupmenu.FindItemById(event.GetId()))
	def OnContrastPopupItemSelected(self, event):
		self.OnPopupItemSelected(ref=1, item=self.contrastPopupmenu.FindItemById(event.GetId()))
	def OnSpeakerPopupItemSelected(self, event):
		self.OnPopupItemSelected(ref=2, item=self.speakerPopupmenu.FindItemById(event.GetId()))
	def OnPopupItemSelected(self, ref, item):
		action = item.GetText()
		self.PopupMenuDialog(ref, action)
		
		# Dialog box from popup menu
	def PopupMenuDialog(self, ref, action):
		'''Brings up the dialog box appropriate to the selected option in the context menu.'''
		whichBox = {0 : self.languages, 1 : self.contrasts, 2 : self.speakers}
		theBox = whichBox[ref]
		index = theBox.GetSelections()
		sel = theBox.GetString(index[0])
		print index, sel
		if action == "delete":
			dlg = wx.MessageDialog(self, "Really delete item '%s'?" % sel, "Delete item")
			if dlg.ShowModal() == wx.ID_OK:
				theBox.Delete(index[0])
				del self.allLanguages[sel] # remove from dictionary used in OnSelectLanguage
				self.contrasts.Clear(), self.speakers.Clear() # make blank, since now the corresponding language has been deleted
			dlg.Destroy()
		elif action == "rename":
			dlg = wx.TextEntryDialog(self, "Enter the new name for item '%s' below." % sel, "Rename item")
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
	def OnAdd(self, ref): # Do we need to protect against people adding lots of "junk" languages which are empty forever?
		'''Adds a language or contrast or speaker to the list.'''
		whichBox = {0 : [self.languages, "language"], 1 : [self.contrasts, "contrast"], 2 : [self.speakers, "speaker"]}
		box = whichBox[ref][0]
		variable = whichBox[ref][1]
		text = wx.GetTextFromUser(message=("Enter a new %s" % variable), caption=("New %s" % variable), default_value="", parent=None)
		if text != "":
			box.Append(text)
	
	def OnSelectLanguage(self, event):
		'''Gets speakers and contrasts for that language.'''
		index = event.GetSelection()
		language = self.languages.GetString(index)
		print (language)
		self.contrasts.Clear()
		self.speakers.Clear()
		for i in self.allLanguages[language][0]: # I tried to do these two iterations in one but the dict started doing really weird things
			self.contrasts.Append(i)
		for i in self.allLanguages[language][1]:
			self.speakers.Append(i)
		#event.Skip()
	
	def OnLanguageExample(self, event): self.OnExample(0, event.GetSelection())
	def OnContrastExample(self, event): self.OnExample(1, event.GetSelection())
	def OnSpeakerExample(self, event):  self.OnExample(2, event.GetSelection())
	def OnExample(self, ref, index):
		'''Plays the sound of that speaker saying a word, or a word in that language, or a pair of contrasting words for that contrast.'''
		whichBox = {0 : self.languages, 1 : self.contrasts, 2 : self.speakers}
		theBox = whichBox[ref]
		play = theBox.GetString(index)
		print ("You just asked for an example of %s" % play)
		# Finish me, Guy! :)
