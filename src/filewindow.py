import wx, os, sqlite3
import wx.lib.mixins.listctrl as listmix
wx.USE_UNICODE = 1

import pyphon, metadatapanel

PANEL_SIZE = (600,620)

class EditableListCtrl(wx.ListCtrl, listmix.TextEditMixin):
	''' 
	TextEditMixin allows any column to be edited.
	'''
	def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0):
		'''Constructor'''
		wx.ListCtrl.__init__(self, parent, id, pos, size, style)
		listmix.TextEditMixin.__init__(self)


class AddPairsDialog(wx.Dialog):
	"""
	Add a minimal pair
	"""
	def __init__(self, parent, title, size):
		wx.Dialog.__init__(self, parent=parent, title=title, size=size)
		
		self.size = size
		self.parent = parent
		self.allContrasts = {lang:cList for lang, cList in parent.allContrasts.items() if cList}
		self.cursor = parent.cursor
		self.language = None
		self.contrast = None
		
		self.panel = wx.Panel(self, size=self.size)
		self.panel.SetBackgroundColour('#ededed')
		self.mainSizer = wx.BoxSizer(wx.VERTICAL)
		self.grid = wx.GridBagSizer(hgap=20, vgap=10)
		
		self.defaultLangText = "<choose language>"
		self.chooseLangChoices = [self.defaultLangText] + self.allContrasts.keys()
		self.chooseLanguage = wx.ComboBox(self.panel, size=(160,-1), choices=self.chooseLangChoices, style=wx.CB_READONLY)
		self.chooseContrast = wx.ComboBox(self.panel, size=(160,-1), choices=[], style=wx.CB_READONLY)
		self.chooseLanguage.SetStringSelection(self.defaultLangText)
		self.chooseContrast.Disable()
		
		self.first = wx.TextCtrl(self.panel, value=u"", size=(60,-1))
		self.second = wx.TextCtrl(self.panel, value=u"", size=(60,-1), style=wx.TE_PROCESS_ENTER)
		self.addPair = wx.Button(self.panel, label=u"Add pair")
		
		self.Bind(wx.EVT_BUTTON, self.OnAddPair, self.addPair)
		self.Bind(wx.EVT_TEXT_ENTER, self.OnAddPair, self.second)
		self.panel.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
		self.Bind(wx.EVT_COMBOBOX, self.OnLanguage, self.chooseLanguage)
		self.Bind(wx.EVT_COMBOBOX, self.OnContrast, self.chooseContrast)
		
		self.grid.Add(self.chooseLanguage, pos=(1,1))
		self.grid.Add(self.chooseContrast, pos=(2,1))
		self.grid.Add(self.first, pos=(3,1))
		self.grid.Add(self.second, pos=(3,2))
		self.grid.Add(self.addPair, pos=(4,1))
		
		self.mainSizer.Add(self.grid, 0, wx.ALL, 0)
		self.panel.SetSizerAndFit(self.mainSizer)
		
		self.chooseLanguage.SetFocus()


	def OnLanguage(self, event):
		if self.language != event.GetString():
			if self.defaultLangText in self.chooseLanguage.GetItems():
				self.chooseLanguage.SetItems(self.allContrasts.keys())
	
		self.language = unicode(event.GetString())
		print(u"you chose {}".format(self.language))

		self.defaultContrastText = "<contrast>"
		self.chooseContrastChoices = [self.defaultContrastText] + self.allContrasts[self.language]
		self.chooseContrast.SetItems(self.chooseContrastChoices)
		self.chooseContrast.SetStringSelection(self.defaultContrastText)
		self.chooseContrast.Enable()
		
	
	def OnContrast(self, event):
		if event.GetString() != self.defaultContrastText and self.defaultContrastText in self.chooseContrast.GetItems():
			self.chooseContrast.SetItems(self.allContrasts[self.language])
		self.contrast = unicode(event.GetString())
		print(u"you chose {}".format(self.contrast))
		
	
	def OnAddPair(self, event):
		item1, item2 = unicode(self.first.Value).strip(), unicode(self.second.Value).strip()
		entry = (self.language, self.contrast, item1, item2)
		
		if not (self.language and self.contrast):
			dlg = wx.MessageDialog(self.panel, u"Please specify the language and contrast.", u"Error", wx.OK | wx.ICON_ERROR)
			dlg.ShowModal()
			dlg.Destroy()
		
		elif not (item1 and item2):
			dlg = wx.MessageDialog(self.panel, u"Please specify both items.", u"Error", wx.OK | wx.ICON_ERROR)
			dlg.ShowModal()
			dlg.Destroy()
		
		else:
			self.cursor.execute(u"INSERT INTO minimal_pairs VALUES (?, ?, ?, ?)", entry)
			self.parent.AddToList(self.parent.GetCount(), entry)
			self.parent.original.append(entry)
			self.parent.everything.append(entry)
			self.first.SetFocus()
			self.first.SelectAll()
	
	def OnKeyDown(self, event): 
	# at the moment this only works when the panel is the object that is focussed (i.e. just clicked on/currently "active")
		'''Save the current changes when you press the 'enter' key.'''
		print ("you pressed a key")
		key = event.GetKeyCode()
		if key == wx.WXK_RETURN:
			self.OnAddPair(event)
	

class DatabasePanel(wx.Panel):
	'''
	Base panel for adding/editing files and minimal pairs
	'''
	def __init__(self, parent, headings, query):
		wx.Panel.__init__(self, parent, size=PANEL_SIZE)
		
		self.headings = headings
		self.cursor = parent.cursor
		self.query = query
		
		# GUI code #
		self.SetBackgroundColour('#ededed')
		self.mainSizer = wx.BoxSizer(wx.VERTICAL)
		self.grid = wx.GridBagSizer(hgap=5, vgap=5)

		#self.selectAll = wx.Button(self, label=u"Select all")
		#self.delete = wx.Button(self, label=u"Delete selected")
		self.save = wx.Button(self, label=u"Save changes")
		self.add = wx.Button(self, label=u"Add...")  # Generic label to be changed by child classes
		self.search = wx.SearchCtrl(self, value=u"", size=(250, -1), style=wx.TE_PROCESS_ENTER)
		
		self.itemList = EditableListCtrl(self, id=wx.ID_ANY, pos=(300,60), size=(450,400), style=wx.LC_REPORT|wx.SUNKEN_BORDER)
		for i, text in enumerate(self.headings):
			self.itemList.InsertColumn(col=i, heading=text)
		self.itemList.SetColumnWidth(0, 150)
		self.itemList.SetColumnWidth(2, 100)
		
		#self.Bind(wx.EVT_BUTTON, self.OnSelectAll, self.selectAll)
		#self.Bind(wx.EVT_BUTTON, self.OnDelete, self.delete)
		self.Bind(wx.EVT_BUTTON, self.OnSave, self.save)
		self.Bind(wx.EVT_BUTTON, self.OnAdd, self.add)
		self.Bind(wx.EVT_TEXT_ENTER, self.OnSearch, self.search)
		self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.OnSearch, self.search)
		#self.Bind(wx.EVT_TEXT, ..., self.search)  # We could build in auto-complete...# play file on pressing enter when row highlighted
		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnPlay, self.itemList)
		
		self.grid.Add(self.search, pos=(1,1), span=(1,3))
		self.grid.Add(self.itemList,  pos=(3,1), span=(3,3))
		#self.grid.Add(self.selectAll, pos=(6,1))
		#self.grid.Add(self.delete, pos=(7,1))
		self.grid.Add(self.add, pos=(6,1))
		self.grid.Add(self.save, pos=(6,2))
		
		self.mainSizer.Add(self.grid, 0, wx.ALL, 0)
		self.SetSizerAndFit(self.mainSizer)
		
		# POPUP MENUS
		self.menu = wx.Menu()  # Labels will be dynamically changed as needed
		self.itemList.Bind(wx.EVT_CONTEXT_MENU, self.OnShowPopup)
		
		for i in range(len(self.headings)):
			item = self.menu.Append(-1, u"<placeholder>")
			self.Bind(wx.EVT_MENU, self.OnPopupItemSelected, item)
		#self.menu.AppendSeparator()
		#delete = self.menu.Append(-1, u"Delete selected")
		#self.Bind(wx.EVT_MENU, self.OnDelete, delete)
		
		# DATABASE
		# To store the original records before user editing
		self.original = []
		self.everything = []
		self.cursor.execute(query)
		for recording in self.cursor:
			self.AddToList(len(self.original), recording)
			self.original.append(recording)
			self.everything.append(recording)	
		
		
	# Wrappers for itemList access
	def AddToList(self, index, items):
		""" Add an item to the table """
		self.itemList.InsertStringItem(index, items[0])
		for i in range(1, len(items)):
			self.itemList.SetStringItem(index, i, items[i])
	
	def GetFocused(self):
		return self.itemList.GetFocusedItem()
	
	def GetText(self, row, column):
		return self.itemList.GetItemText(row, column)
	
	def GetRow(self, row):
		return tuple(self.GetText(row, i) for i in range(len(self.headings)))
	
	def GetFocusedText(self, column):
		focus = self.GetFocused()
		return self.GetText(focus, column)
	
	def GetFocusedRow(self):
		focus = self.GetFocused()
		return self.GetRow(focus)
	
	def GetCount(self):
		return self.itemList.GetItemCount()
	
	# Methods to be triggered by events
	def OnShowPopup(self, event):
		""" Show popup menu """
		pos = self.ScreenToClient(event.GetPosition())
		sel = self.itemList.GetFocusedItem()
		items = self.menu.GetMenuItems()
		for i in range(len(self.headings)):
			option = u'Copy "{}" to all selected rows'.format(self.itemList.GetItemText(item=sel, col=i))
			items[i].SetText(option)
		self.PopupMenu(self.menu, pos)
	
	def OnPopupItemSelected(self, event):
		""" Show dialog box appropriate to listbox clicked """
		item = self.menu.FindItemById(event.GetId())
		choice = self.menu.GetMenuItems().index(item)
		sel = self.itemList.GetFocusedItem()
		text = self.itemList.GetItemText(item=sel, col=choice)
		for row in range(self.itemList.GetItemCount()):
			if self.itemList.IsSelected(row):
				self.itemList.SetStringItem(row, choice, text)
	
	def OnSearch(self, event):
		searched = event.GetString()
		self.original = []
		self.itemList.DeleteAllItems()
		i = 0
		for item in self.everything:
			for cell in item:
				if searched in cell:
					self.original.append(item)
					self.AddToList(i, item)
					i += 1
					break
	
	# The following functions must be overwritten by subclasses
	def OnAdd(self, event):	raise NotImplementedError
	def OnSave(self, event): raise NotImplementedError
	def OnDelete(self, event): raise NotImplementedError
	def OnPlay(self, event): raise NotImplementedError


class RecordingsPanel(DatabasePanel):
	"""
	View and edit metadata for recordings
	"""
	def __init__(self, parent):
		DatabasePanel.__init__(self, parent=parent, headings=(u"Filename", u"Answer", u"Language", u"Speaker"), query=u"SELECT file, answer, language, speaker FROM recordings")
		self.add.Label = u"Add files..."
		self.fields = ("file", "answer", "language", "speaker")
		
		self.allLanguages, _, self.allSpeakers = parent.metaData
	
	
	def OnPlay(self, event):
		'''Plays the sound file from the selected row.'''
		filename = self.GetFocusedText(0)
		filename = pyphon.filepath(filename)
		wx.Sound(filename).Play()

	def OnAdd(self, event):
		""" Browse for files """
		print("Let's do some browsin'")
		dlg = wx.FileDialog(self, u"Choose file(s)", defaultDir=pyphon.DATA_DIR, defaultFile=u"", wildcard=u"*.wav", style=wx.FD_MULTIPLE)
		if dlg.ShowModal() == wx.ID_OK:
			# Check if files are already in the data directory
			direc = dlg.GetDirectory()
			if direc == pyphon.DATA_DIR:
				direc = None
			
			i = self.GetCount()
			for filename in dlg.GetFilenames():
				print(filename)
				# Only remember the directory if not the data directory
				if direc:
					filename = os.path.join(direc, filename)
				# Add files to the end of the table
				self.AddToList(i, (filename,))
				i += 1
	
	def OnSave(self, event):
		""" Update existing files, and add new files """
		# Update existing files
		for i in range(len(self.original)):
			old = self.original[i]
			new = self.GetRow(i)
			if new != old:
				self.cursor.execute(u"UPDATE recordings SET {} = ?, {} = ?, {} = ?, {} = ? WHERE file = ?".format(*self.fields), new + old[0:1])
				self.original[i] = new
		# Add new files
		for i in range(len(self.original), self.GetCount()):
			recording = self.GetRow(i)
			filename, answer, language, speaker = recording
			self.cursor.execute(u"INSERT INTO recordings VALUES (?,?,?,?)", (filename, speaker, language, answer))
			self.original.append(recording)
		# 'hack'
		self.everything = []
		self.cursor.execute(self.query)
		for recording in self.cursor:
			self.everything.append(recording)	
		# We could catch sqlite3.IntegrityError to inform the user when something goes wrong
		dlg = wx.MessageDialog(self, u"Changes successfully saved", u"Confirmation", wx.OK)
		dlg.ShowModal()
		dlg.Destroy()
		
		

class MinimalPairsPanel(DatabasePanel):
	"""
	View and edit minimal pairs
	"""
	def __init__(self, parent):
		DatabasePanel.__init__(self, parent=parent, headings=(u"Language", u"Contrast", u"Item 1", u"Item 2"), query=u"SELECT language, contrast, item_1, item_2 FROM minimal_pairs")
		self.fields = ("language", "contrast", "item_1", "item_2")
		
		self.add.Label = u"Add pairs..."
		
		self.allLanguages, self.allContrasts, _ = parent.metaData
		
	def OnAdd(self, event):
		dlg = AddPairsDialog(self, u"Add Pairs", size=(300,200))
		dlg.ShowModal()
		dlg.Destroy()
	
	def OnSave(self, event):
		""" Update existing pairs """
		for i in range(len(self.original)):
			old = self.original[i]
			new = self.GetRow(i)
			if new != old:
				self.cursor.execute(u"UPDATE minimal_pairs SET {0} = ?, {1} = ?, {2} = ?, {3} = ? WHERE {0} = ? AND {1} = ? AND {2} = ? AND {3} = ?".format(*self.fields), new + old)
				self.original[i] = new
		# 'hack'
		self.everything = []
		self.cursor.execute(self.query)
		for recording in self.cursor:
			self.everything.append(recording)
		# dialogue box
		dlg = wx.MessageDialog(self, u"Changes successfully saved", u"Confirmation", wx.OK)
		dlg.ShowModal()
		dlg.Destroy()
	
	"""
	To reduce code redundancy, we could use something like this...
	def SaveQuery(self, old, new):
		pass
	... which would be called by a method in DatabasePanel
	"""


class FileWindow(wx.Frame):
	'''
	This is the frame where files are to be viewed and potentially inputted to the program.
	The MainWindow is this window's parent, so they can communicate.
	'''
	def __init__(self, parent, title):
		wx.Frame.__init__(self, parent, title=title, style=(wx.DEFAULT_FRAME_STYLE | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX | wx.WS_EX_CONTEXTHELP), size=PANEL_SIZE)
		self.cursor = parent.cursor
		self.metaData = parent.metaData
		notebook = FileNotebook(self)
		notebook.AddPage(metadatapanel.MetadataPanel(notebook), u"Language info")
		notebook.AddPage(RecordingsPanel(notebook), u"Recordings")
		notebook.AddPage(MinimalPairsPanel(notebook), u"Minimal pairs")
		#notebook.AddPage(databasegridpanel.AddDataGridPanel(notebook), "Recordings")
		#notebook.AddPage(databasegridpanel.MinimalPairsGridPanel(notebook), "Minimal pairs")
	
class FileNotebook(wx.Notebook):
	def __init__(self, parent):
		wx.Notebook.__init__(self, parent)
		self.cursor = parent.cursor
		self.metaData = parent.metaData
