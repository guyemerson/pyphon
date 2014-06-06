import wx, os

import wx.lib.mixins.listctrl  as  listmix

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
	def __init__(self, parentPanel, title, size):
		wx.Dialog.__init__(self, parent=parentPanel, title=title, size=size)
		
		self.size = size
		self.parent = parentPanel
		
		self.panel = wx.Panel(self, size=self.size)
		self.panel.SetBackgroundColour('#ededed')
		self.mainSizer = wx.BoxSizer(wx.VERTICAL)
		self.grid = wx.GridBagSizer(hgap=20, vgap=10)
		
		self.chooseLanguage = wx.ComboBox(self.panel, size=(140,-1), choices=["-", "Catalan", "Burmese", "Svan"], style=wx.CB_READONLY)
		self.chooseContrast = wx.ComboBox(self, size=(95,-1), choices=["-", "bla-bli", "wo-we"], style=wx.CB_READONLY)
		self.firstWord = wx.TextCtrl(self.panel, value="", size=(60,-1))
		self.firstWord.SetFocus()
		self.secondWord = wx.TextCtrl(self.panel, value="", size=(60,-1))
		self.addPairButton = wx.Button(self.panel, label="Add pair")
		
		self.Bind(wx.EVT_BUTTON, self.OnAddPair, self.addPairButton)
		self.panel.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
		self.Bind(wx.EVT_COMBOBOX, self.OnChooseLanguage, self.chooseLanguage)
		self.Bind(wx.EVT_COMBOBOX, self.OnChooseContrast, self.chooseContrast)
		
		self.grid.Add(self.chooseLanguage, pos=(1,1))
		self.grid.Add(self.chooseContrast, pos=(1,2))
		self.grid.Add(self.firstWord, pos=(2,1))
		self.grid.Add(self.secondWord, pos=(2,2))
		self.grid.Add(self.addPairButton, pos=(3,1))
		self.mainSizer.Add(self.grid, 0, wx.ALL, 0)
		self.panel.SetSizerAndFit(self.mainSizer)

	def OnChooseLanguage(self, event):
		print("you chose a language")
	def OnChooseContrast(self, event):
		print("you chose a contrast")
	def AddPair(self):
		language, contrast = self.chooseLanguage.Value, self.chooseContrast.Value
		word1, word2 = self.firstWord.Value, self.secondWord.Value
		if "-" in [language, contrast]:
			dlg = wx.MessageDialog(self.panel, "You have not specified langauge or contrast.\nPlease specify these and try again.", "Error", wx.OK | wx.ICON_ERROR)
			dlg.ShowModal()
			dlg.Destroy()
		elif "" in [word1, word2]:
			dlg = wx.MessageDialog(self.panel, "You have not specified both words in the pair.\nPlease specify these and try again.", "Error", wx.OK | wx.ICON_ERROR)
			dlg.ShowModal()
			dlg.Destroy()
		else:
			self.parent.fileList.InsertStringItem(0, self.chooseLanguage.Value)
			self.parent.fileList.SetStringItem(0, 1, self.chooseContrast.Value)
			self.parent.fileList.SetStringItem(0, 2, self.firstWord.Value)
			self.parent.fileList.SetStringItem(0, 3, self.secondWord.Value)
	def OnKeyDown(self, event): 
	# at the moment this only works when the panel is the object that is focussed (i.e. just clicked on/currently "active")
		'''Save the current changes when you press the 'enter' key.'''
		print ("you pressed a key")
		key = event.GetKeyCode()
		if key == wx.WXK_RETURN:
			self.AddPair()
	def OnAddPair(self, event):
		self.AddPair()
		
		

class DatabasePanel(wx.Panel):
	def __init__(self, parent, cursor, options):
		wx.Panel.__init__(self, parent, size=PANEL_SIZE)
		
		self.options = options
		
		self.SetBackgroundColour('#ededed')
		self.mainSizer = wx.BoxSizer(wx.VERTICAL)
		self.grid = wx.GridBagSizer(hgap=5, vgap=5)

		self.selectAll = wx.Button(self, label="Select all")
		self.deleteSelected = wx.Button(self, label="Delete selected")
		self.save = wx.Button(self, label="Save changes")
		self.Bind(wx.EVT_BUTTON, self.OnSelectAll, self.selectAll)
		
		self.search = wx.TextCtrl(self, value="<search>", size=(250, -1))
		
		# first time using this object, seeing how it goes, may use ListBox object instead
		self.fileList = EditableListCtrl(self, id=wx.ID_ANY, pos=(300,60), size=(500,400), style=wx.LC_REPORT|wx.SUNKEN_BORDER)
		
		for i in range(len(self.options)):
			self.fileList.InsertColumn(col=i, heading=self.options[i])
		# also, widen column 1!!
		
		#self.fileList.Append("hello")
		#self.fileList.EnableAlternateRowColours(enable=True)
		#self.fileList.EnableBellOnNoMatch(on=True)
		
		self.grid.Add(self.search, pos=(1,1), span=(1,3))
		self.grid.Add(self.fileList,  pos=(3,1), span=(3,3))
		self.grid.Add(self.selectAll, pos=(6,1))
		self.grid.Add(self.save, pos=(6,4))
		self.grid.Add(self.deleteSelected, pos=(7,1))
		self.mainSizer.Add(self.grid, 0, wx.ALL, 0)
		self.SetSizerAndFit(self.mainSizer)
		
		
		# POPUP MENUS
		self.menu = wx.Menu()
		self.fileList.Bind(wx.EVT_CONTEXT_MENU, self.OnShowPopup)

	# Show popup menu
	def OnShowPopup(self, event):
		x = self.menu.GetMenuItemCount()  # deletes menu items to stop them accumulating
		for i in range(x):
			self.menu.DestroyItem(i) # THIS FAILS currently due to "another argument needed", although the documentation seems to say only an int is needed
		pos = self.ScreenToClient(event.GetPosition())
		sel = self.fileList.GetFocusedItem()
		for i in range(len(self.options)):
			option = 'Generalise "{}" to all {} entries'.format(self.fileList.GetItemText(item=sel, col=i), self.options[i])
			item = self.menu.Append(-1, option)
			self.Bind(wx.EVT_MENU, self.OnPopupItemSelected, item)
		self.PopupMenu(self.menu, pos)
	
	# Show dialog box appropriate to listbox clicked
	def OnPopupItemSelected(self, event):	
		item = self.menu.FindItemById(event.GetId())
		action = item.GetText()
		self.PopupMenuDialog(action) # self.PopupMenuDialog is defined in each child class, no need to define it in the parent class
		
	def OnSelectAll(self, event):
		print("You have pressed the 'Select All' button")



class AddDataPanel(DatabasePanel):
	def __init__(self, parent, cursor):
		DatabasePanel.__init__(self, parent=parent, cursor=cursor, options=["Filename", "Answer", "Language", "Speaker"])
		
		self.browse = wx.Button(self, label="Browse...")
		self.save.Label= "Add to database"
		self.deleteSelected.Label = "Remove selected"

		rows = [("guns", "dangerous"),
		("pyphon", "awesome"),
		("pasta", "tasty")]
		
		i = 0
		for row in rows:
			self.fileList.InsertStringItem(i, row[0])
			self.fileList.SetStringItem(i, 1, row[1])
			self.fileList.SetStringItem(i, 2, "-")
			i +=1
		
		self.Bind(wx.EVT_BUTTON, self.OnBrowse, self.browse)
		self.Bind(wx.EVT_BUTTON, self.OnAdd, self.save)
		# play file on pressing enter when row highlighted
		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnFileExample, self.fileList)
		
		self.grid.Add(self.browse, pos=(1,4))


	def PopupMenuDialog(self, action):
		x = self.fileList.GetFocusedItem()
		print x
		thingy = self.fileList.GetItemText(item=x, col=0)
		dlg = wx.MessageDialog(self, "You are interested in {}".format(thingy), "Message for you")
		dlg.ShowModal()
		dlg.Destroy()
	
	def OnFileExample(self, event):
		'''Plays the sound file from the selected row.'''
		x = self.fileList.GetFocusedItem()
		print x
		playDir  = self.fileList.GetItemText(item=x, col=0)
		print ("You just asked for an example of {}".format(playDir))
		# Finish me, Guy! :)

	def OnBrowse(self, event):
		print("Let's do some browsin'")
		dlg = wx.FileDialog(self, "Choose a file", defaultDir=os.getcwd(), defaultFile="", wildcard="*.wav", style=wx.FD_MULTIPLE)
		if dlg.ShowModal() == wx.ID_OK:
			print (dlg.GetFilenames())
			i = 0
			for filename in dlg.GetFilenames():
				self.fileList.InsertStringItem(i, filename)
				self.fileList.SetStringItem(i, 1, "<insert sound>")
				self.fileList.SetStringItem(i, 2, "...")
				i +=1
	
	def OnAdd(self, event):
		newStuff = []
		dlg = wx.MessageDialog(self, "You intend to add these things to the database: \n{}\nDo you wish to continue?".format(newStuff), "Confirmation", wx.OK | wx.CANCEL)
		if dlg.ShowModal() == wx.ID_OK:
			print ("You want to put some stuff in the database. We've taken note and will have customer services call you.")
		dlg.Destroy()



class MinimalPairsPanel(DatabasePanel):
	def __init__(self, parent, cursor):
		DatabasePanel.__init__(self, parent=parent, cursor=cursor, options=["Language", "Contrast", "Option 1", "Option 2"])
		
		self.addPairs = wx.Button(self, label="Add pairs...")
		self.Bind(wx.EVT_BUTTON, self.OnAddPairs, self.addPairs)
		
		self.SetBackgroundColour('#ededed')
		self.mainSizer = wx.BoxSizer(wx.VERTICAL)

		rows = [("guns", "dangerous"),
		("pyphon", "awesome"),
		("pasta", "tasty")]
		
		for i, row in enumerate(rows):
			self.fileList.InsertStringItem(i, row[0])
			self.fileList.SetStringItem(i, 1, row[1])
			self.fileList.SetStringItem(i, 2, "-")
		
		self.grid.Add(self.addPairs, pos=(1,4))

	def OnAddPairs(self, event):
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
		
