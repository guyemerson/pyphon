import wx, os
import wx.lib.mixins.listctrl as listmix
wx.USE_UNICODE = 1

import pyphon, metadatapanel

PANEL_SIZE = (800,600)

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
		
		self.chooseLanguage = wx.ComboBox(self.panel, size=(140,-1), choices=parent.allLanguages, style=wx.CB_READONLY)
		self.chooseContrast = wx.ComboBox(self.panel, size=(140,-1), choices=["-"], style=wx.CB_READONLY)
		self.first = wx.TextCtrl(self.panel, value=u"", size=(60,-1))
		self.first.SetFocus()
		self.second = wx.TextCtrl(self.panel, value=u"", size=(60,-1))
		self.addPair = wx.Button(self.panel, label=u"Add pair")
		
		self.Bind(wx.EVT_BUTTON, self.OnAddPair, self.addPair)
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

	def OnLanguage(self, event):
		self.language = unicode(event.GetString())
		self.chooseContrast.SetItems(self.allContrasts[self.language])
		self.contrast = None
		print(u"you chose {}".format(self.language))
	
	def OnContrast(self, event):
		self.contrast = unicode(event.GetString())
		print(u"you chose {}".format(self.contrast))
	
	def OnAddPair(self, event):
		item1, item2 = unicode(self.first.Value).strip(), unicode(self.second.Value).strip()
		
		if not (self.language and self.contrast):
			dlg = wx.MessageDialog(self.panel, u"Please specify the language and contrast.", u"Error", wx.OK | wx.ICON_ERROR)
			dlg.ShowModal()
			dlg.Destroy()
		
		elif not (item1 and item2):
			dlg = wx.MessageDialog(self.panel, u"Please specify both items.", u"Error", wx.OK | wx.ICON_ERROR)
			dlg.ShowModal()
			dlg.Destroy()
		
		else:
			self.cursor.execute(u"INSERT INTO minimal_pairs VALUES (?, ?, ?, ?)", (self.language, self.contrast, item1, item2))
			self.parent.addToList(self.parent.itemList.GetItemCount(), (self.language, self.contrast, item1, item2))
	
	def OnKeyDown(self, event): 
	# at the moment this only works when the panel is the object that is focussed (i.e. just clicked on/currently "active")
		'''Save the current changes when you press the 'enter' key.'''
		print ("you pressed a key")
		key = event.GetKeyCode()
		if key == wx.WXK_RETURN:
			self.AddPair()
	

class DatabasePanel(wx.Panel):
	'''
	Base panel for adding/editing files and minimal pairs
	'''
	def __init__(self, parent, options):
		wx.Panel.__init__(self, parent, size=PANEL_SIZE)
		
		self.options = options
		
		self.SetBackgroundColour('#ededed')
		self.mainSizer = wx.BoxSizer(wx.VERTICAL)
		self.grid = wx.GridBagSizer(hgap=5, vgap=5)

		self.selectAll = wx.Button(self, label=u"Select all")
		self.delete = wx.Button(self, label=u"Delete selected")
		self.save = wx.Button(self, label=u"Save changes")
		self.add = wx.Button(self, label=u"Add...")  # Generic label to be changed by child classes
		self.search = wx.TextCtrl(self, value=u"<search>", size=(250, -1), style=wx.TE_PROCESS_ENTER)
		
		self.Bind(wx.EVT_BUTTON, self.OnSelectAll, self.selectAll)
		self.Bind(wx.EVT_BUTTON, self.OnDelete, self.delete)
		self.Bind(wx.EVT_BUTTON, self.OnSave, self.save)
		self.Bind(wx.EVT_BUTTON, self.OnAdd, self.add)
		self.Bind(wx.EVT_TEXT_ENTER, self.OnSearch, self.search)
		#self.Bind(wx.EVT_TEXT, ..., self.search)  # We could build in auto-complete...
		
		self.itemList = EditableListCtrl(self, id=wx.ID_ANY, pos=(300,60), size=(500,400), style=wx.LC_REPORT|wx.SUNKEN_BORDER)
		for i, text in enumerate(self.options):
			self.itemList.InsertColumn(col=i, heading=text)
		self.itemList.SetColumnWidth(0, 100)
		
		#self.itemList.EnableAlternateRowColours(enable=True)
		#self.itemList.EnableBellOnNoMatch(on=True)
		
		self.grid.Add(self.search, pos=(1,1), span=(1,3))
		self.grid.Add(self.add, pos=(1,4))
		self.grid.Add(self.itemList,  pos=(3,1), span=(3,3))
		self.grid.Add(self.selectAll, pos=(6,1))
		self.grid.Add(self.delete, pos=(7,1))
		self.grid.Add(self.save, pos=(6,4))
		
		self.mainSizer.Add(self.grid, 0, wx.ALL, 0)
		self.SetSizerAndFit(self.mainSizer)
		
		self.cursor = parent.cursor
		
		# POPUP MENUS
		self.menu = wx.Menu()  # Labels will be dynamically changed as needed
		self.itemList.Bind(wx.EVT_CONTEXT_MENU, self.OnShowPopup)
		
		for i in range(len(self.options)):
			item = self.menu.Append(-1, u"<placeholder>")
			self.Bind(wx.EVT_MENU, self.OnPopupItemSelected, item)
		
	
	def addToList(self, index, items):
		""" Add an item to the table """
		self.itemList.InsertStringItem(index, items[0])
		for i in range(1, len(items)):
			self.itemList.SetStringItem(index, i, items[i])
	
	
	def OnShowPopup(self, event):
		""" Show popup menu """
		pos = self.ScreenToClient(event.GetPosition())
		sel = self.itemList.GetFocusedItem()
		for i, item in enumerate(self.menu.GetMenuItems()):
			option = u'Copy "{}" to all selected rows'.format(self.itemList.GetItemText(item=sel, col=i))
			item.SetText(option)
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
	
	def OnSelectAll(self, event):
		""" This is still a placeholder """
		print(u"You have pressed the 'Select All' button")
	
	# The following functions must be overwritten by subclasses
	def OnAdd(self, event):	raise NotImplementedError
	def OnSave(self, event): raise NotImplementedError
	def OnSearch(self, event): raise NotImplementedError
	def OnDelete(self, event): raise NotImplementedError


class RecordingsPanel(DatabasePanel):
	"""
	View and edit metadata for recordings
	"""
	def __init__(self, parent):
		DatabasePanel.__init__(self, parent=parent, options=(u"Filename", u"Answer", u"Language", u"Speaker"))
		self.add.Label = u"Add files..."
		
		### Currently we load everything - later we need to do this based on search...
		self.cursor.execute(u"SELECT file, answer, language, speaker FROM recordings")
		self.numOld = 0
		for recording in self.cursor:
			self.addToList(self.numOld, recording)
			self.numOld += 1
		
		# play file on pressing enter when row highlighted
		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnPlay, self.itemList)
		
		self.allLanguages, _, self.allSpeakers = parent.metaData
	
	
	def OnPlay(self, event):
		'''Plays the sound file from the selected row.'''
		x = self.itemList.GetFocusedItem()
		print(x)
		filename = self.itemList.GetItemText(item=x, col=0)
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
			
			i = self.itemList.GetItemCount()
			for filename in dlg.GetFilenames():
				print(filename)
				# Only remember the directory if not the data directory
				if direc:
					filename = os.path.join(direc, filename)
				# Add files to the end of the table
				self.addToList(i, (filename,))
				i += 1
	
	def OnSave(self, event):
		""" Currently, we save new files only """
		for i in range(self.numOld):
			pass
		for i in range(self.numOld, self.itemList.GetItemCount()):
			filename, answer, language, speaker = (self.itemList.GetItemText(i, j) for j in range(4))
			self.cursor.execute(u"INSERT INTO recordings VALUES (?,?,?,?)", (filename, speaker, language, answer))
		"""
		dlg = wx.MessageDialog(self, u"Save changes?".format(newStuff), u"Confirmation", wx.OK | wx.CANCEL)
		if dlg.ShowModal() == wx.ID_OK:
			print (u"You want to put some stuff in the database. We've taken note and will have customer services call you.")
		dlg.Destroy()
		"""


class MinimalPairsPanel(DatabasePanel):
	"""
	View and edit minimal pairs
	"""
	def __init__(self, parent):
		DatabasePanel.__init__(self, parent=parent, options=(u"Language", u"Contrast", u"Item 1", u"Item 2"))
		
		self.add.Label = u"Add pairs..."

		### Currently we load everything - later we need to do this based on search...
		self.cursor.execute(u"SELECT language, contrast, item_1, item_2 FROM minimal_pairs")
		for i, pair in enumerate(self.cursor):
			self.addToList(i, pair)
		
		self.allLanguages, self.allContrasts, _ = parent.metaData
	
	
	def OnAdd(self, event):
		dlg = AddPairsDialog(self, u"Add Pairs", size=(300,200))
		dlg.ShowModal()
		dlg.Destroy()



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
