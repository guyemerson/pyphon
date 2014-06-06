import wx, os
import wx.lib.mixins.listctrl as listmix

import pyphon

PANEL_SIZE = (800,600)

class EditableListCtrl(wx.ListCtrl, listmix.TextEditMixin):
	''' 
	TextEditMixin allows any column to be edited.
	'''
	def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0):
		'''Constructor'''
		wx.ListCtrl.__init__(self, parent, id, pos, size, style)
		listmix.TextEditMixin.__init__(self)


class DatabasePanel(wx.Panel):
	'''
	Base panel for adding/editing files and minimal pairs
	'''
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, size=PANEL_SIZE)
		
		self.SetBackgroundColour('#ededed')
		self.mainSizer = wx.BoxSizer(wx.VERTICAL)
		self.grid = wx.GridBagSizer(hgap=5, vgap=5)

		self.selectAll = wx.Button(self, label="Select all")
		self.delete = wx.Button(self, label="Delete selected")
		self.save = wx.Button(self, label="Save changes")
		self.add = wx.Button(self, label="Add...")  # Generic label to be changed by child classes
		self.search = wx.TextCtrl(self, value="<search>", size=(250, -1), style=wx.TE_PROCESS_ENTER)
		
		self.Bind(wx.EVT_BUTTON, self.OnSelectAll, self.selectAll)
		self.Bind(wx.EVT_BUTTON, self.OnDelete, self.delete)
		self.Bind(wx.EVT_BUTTON, self.OnSave, self.save)
		self.Bind(wx.EVT_BUTTON, self.OnAdd, self.add)
		self.Bind(wx.EVT_TEXT_ENTER, self.OnSearch, self.search)
		#self.Bind(wx.EVT_TEXT, ..., self.search)  # We could build in auto-complete...
		
		self.itemList = EditableListCtrl(self, id=wx.ID_ANY, pos=(300,60), size=(500,400), style=wx.LC_REPORT|wx.SUNKEN_BORDER)
		
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
		self.metaData = parent.metaData
	
	def addToList(self, index, items):
		self.itemList.InsertStringItem(index, items[0])
		self.itemList.SetStringItem(index, 1, items[1])
		self.itemList.SetStringItem(index, 2, items[2])
		self.itemList.SetStringItem(index, 3, items[3])
	
	def OnSelectAll(self, event):
		print("You have pressed the 'Select All' button")
	
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
		DatabasePanel.__init__(self, parent=parent)
		
		self.itemList.InsertColumn(col=0, heading="Filename", width=180)
		self.itemList.InsertColumn(col=1, heading="Answer")  #, format=wx.LIST_FORMAT_LEFT, width=-1)
		self.itemList.InsertColumn(col=2, heading="Language")
		self.itemList.InsertColumn(col=3, heading="Speaker")
		
		self.add.Label = "Add files..."
		
		### Currently we load everything - later we need to do this based on search...
		self.cursor.execute("SELECT file, answer, language, speaker FROM recordings")
		for i, recording in enumerate(self.cursor):
			self.addToList(i, recording)
		
		# play file on pressing enter when row highlighted
		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnPlay, self.itemList)
		
	
	
	def OnPlay(self, event):
		'''Plays the sound file from the selected row.'''
		x = self.itemList.GetFocusedItem()
		print(x)
		filename = self.itemList.GetItemText(item=x, col=0)
		wx.Sound(filename).Play()

	def OnAdd(self, event):
		""" Browse for files """
		print("Let's do some browsin'")
		dlg = wx.FileDialog(self, "Choose file(s)", defaultDir=pyphon.DATA_DIR, defaultFile="", wildcard="*.wav", style=wx.FD_MULTIPLE)
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
					filename = direc + filename
				# Add files to the end of the table
				self.itemList.InsertStringItem(i, filename)
				i += 1
	
	def OnSave(self, event):
		newStuff = []
		dlg = wx.MessageDialog(self, "You intend to add these things to the database: \n{}\nDo you wish to continue?".format(newStuff), "Confirmation", wx.OK | wx.CANCEL)
		if dlg.ShowModal() == wx.ID_OK:
			print ("You want to put some stuff in the database. We've taken note and will have customer services call you.")
		dlg.Destroy()


class AddPairsDialog(wx.Dialog):
	"""
	Add a minimal pair
	"""
	def __init__(self, parent, title, size):
		wx.Dialog.__init__(self, parent=parent, title=title, size=size)
		
		self.size = size
		self.parent = parent
		self.allContrasts = parent.metaData[1]
		self.language = None
		self.contrast = None
		
		self.panel = wx.Panel(self, size=self.size)
		self.panel.SetBackgroundColour('#ededed')
		self.mainSizer = wx.BoxSizer(wx.VERTICAL)
		self.grid = wx.GridBagSizer(hgap=20, vgap=10)
		
		self.chooseLanguage = wx.ComboBox(self.panel, size=(140,-1), choices=parent.metaData[0], style=wx.CB_READONLY)
		self.chooseContrast = wx.ComboBox(self.panel, size=(140,-1), choices=["-"], style=wx.CB_READONLY)
		self.first = wx.TextCtrl(self.panel, value="", size=(60,-1))
		self.first.SetFocus()
		self.second = wx.TextCtrl(self.panel, value="", size=(60,-1))
		self.addPair = wx.Button(self.panel, label="Add pair")
		
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
		self.language = event.GetString()
		self.chooseContrast.SetItems(self.allContrasts[self.language])
		print("you chose {}".format(self.language))
	
	def OnContrast(self, event):
		self.contrast = event.GetString()
		print("you chose {}".format(self.contrast))
	
	def OnAddPair(self, event):
		item1, item2 = self.first.Value, self.second.Value
		if "-" in [self.language, self.contrast]:
			dlg = wx.MessageDialog(self.panel, "You have not specified language or contrast.\nPlease specify these and try again.", "Error", wx.OK | wx.ICON_ERROR)
			dlg.ShowModal()
			dlg.Destroy()
		elif "" in [item1, item2]:
			dlg = wx.MessageDialog(self.panel, "You have not specified both words in the pair.\nPlease specify these and try again.", "Error", wx.OK | wx.ICON_ERROR)
			dlg.ShowModal()
			dlg.Destroy()
		else:
			self.parent.addToList(self.parent.itemList.GetItemCount(), (self.language, self.contrast, item1, item2))
	
	def OnKeyDown(self, event): 
	# at the moment this only works when the panel is the object that is focussed (i.e. just clicked on/currently "active")
		'''Save the current changes when you press the 'enter' key.'''
		print ("you pressed a key")
		key = event.GetKeyCode()
		if key == wx.WXK_RETURN:
			self.AddPair()


class MinimalPairsPanel(DatabasePanel):
	"""
	View and edit minimal pairs
	"""
	def __init__(self, parent):
		DatabasePanel.__init__(self, parent=parent)
		
		self.add.Label = "Add pair..."
		
		self.itemList.InsertColumn(col=0, heading="Language", width=100)
		self.itemList.InsertColumn(col=1, heading="Contrast") 
		self.itemList.InsertColumn(col=2, heading="Item 1")
		self.itemList.InsertColumn(col=3, heading="Item 2")

		### Currently we load everything - later we need to do this based on search...
		self.cursor.execute("SELECT language, contrast, item_1, item_2 FROM minimal_pairs")
		for i, pair in enumerate(self.cursor):
			self.addToList(i, pair)
		
		self.allLanguages, self.allContrasts, _ = parent.metaData
	
	
	def OnAdd(self, event):
		dlg = AddPairsDialog(self, "Add Pairs", size=(300,200))
		dlg.ShowModal()
		dlg.Destroy()


class FileWindow(wx.Frame):
	'''
	This is the frame where files are to be viewed and potentially inputted to the program.
	The MainWindow is this window's parent, so it should be possible to communicate in between these, to e.g. interdict multiple instances.
	'''
	def __init__(self, parent, title):
		wx.Frame.__init__(self, parent, title=title, style=(wx.DEFAULT_FRAME_STYLE | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX | wx.WS_EX_CONTEXTHELP), size=PANEL_SIZE)
		self.cursor = parent.cursor
		self.metaData = parent.metaData
	
class FileNotebook(wx.Notebook):
	def __init__(self, parent):
		wx.Notebook.__init__(self, parent)
		self.cursor = parent.cursor
		self.metaData = parent.metaData