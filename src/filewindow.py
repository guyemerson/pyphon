import wx, os

import wx.lib.mixins.listctrl  as  listmix


class EditableListCtrl(wx.ListCtrl, listmix.TextEditMixin):
	''' 
	TextEditMixin allows any column to be edited.
	'''
	def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0):
		'''Constructor'''
		wx.ListCtrl.__init__(self, parent, id, pos, size, style)
		listmix.TextEditMixin.__init__(self)


class FileWindow(wx.Frame):
	'''
	This is the frame where files are to be viewed and potentially inputted to the program.
	At the moment it is blank.
	
	It needs to be:
	- super idiot-proof -- we don't want anyone having any "accidents" with the data!!
	- encouraging (or at least not discouraging) as regards getting stuck in and contributing, especially through ease of use and lack of intimidation
	
	MULTIPLE FILES should be addable at once. This will make things easier and save people time.
	DRAG AND DROP could be pretty in this window. I will investigate this.
	'''
	def __init__(self, parent, title):
		wx.Frame.__init__(self, parent, title=title, style=(wx.DEFAULT_FRAME_STYLE | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX | wx.WS_EX_CONTEXTHELP), size=(500,500))
		
		# PANEL CODE (sometimes done as separate object, here one object together with frame)		
		self.panel = wx.Panel(self, size=(500,300))
		self.panel.SetBackgroundColour('#ededed')
		self.mainSizer = wx.BoxSizer(wx.VERTICAL)
		self.grid = wx.GridBagSizer(hgap=5, vgap=5)
	
		self.browse = wx.Button(self.panel, label="Browse...")
		
		# first time using this object, seeing how it goes, may use ListBox object instead
		self.fileList = EditableListCtrl(self.panel, id=wx.ID_ANY, pos=(300,60), size=(300,200), style=wx.LC_REPORT|wx.SUNKEN_BORDER)
		self.fileList.InsertColumn(col=0, heading="Filename")  #, format=wx.LIST_FORMAT_LEFT, width=-1)
		self.fileList.InsertColumn(col=1, heading="Sound")
		self.fileList.InsertColumn(col=2, heading="Contrast")
		print (self.fileList.GetColumnCount())
		
		rows = [("guns", "dangerous"),
		("pyphon", "awesome"),
		("pasta", "tasty")]
		
		i = 0
		for row in rows:
			self.fileList.InsertStringItem(i, row[0])
			self.fileList.SetStringItem(i, 1, row[1])
			self.fileList.SetStringItem(i, 2, "-")
			i +=1
		
		
		#self.fileList.Append("hello")
		#self.fileList.EnableAlternateRowColours(enable=True)
		#self.fileList.EnableBellOnNoMatch(on=True)		
		
		
		self.Bind(wx.EVT_BUTTON, self.OnBrowse, self.browse)
		
		self.grid.Add(self.browse, pos=(1, 3))
		self.grid.Add(self.fileList, pos=(3,1))
		
		self.mainSizer.Add(self.grid, 0, wx.ALL, 0)
		self.panel.SetSizerAndFit(self.mainSizer)
		
	def OnBrowse(self, event):
		print("Let's do some browsin'")
		dlg = wx.FileDialog(self, "Choose a file", defaultDir=os.getcwd(), defaultFile="", wildcard="*.wav", style=wx.FD_MULTIPLE)
		if dlg.ShowModal() == wx.ID_OK:
			print (dlg.GetFilenames())
			i = 0
			for file in dlg.GetFilenames():
				self.fileList.InsertStringItem(i, file)
				self.fileList.SetStringItem(i, 1, "<insert sound>")
				self.fileList.SetStringItem(i, 2, "...")
				i +=1
		#	self.filepath.Value = dlg.GetDirectory() + '\\' + dlg.GetFilename()  -- need to retool for multiple files