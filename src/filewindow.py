import wx, os


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
		wx.Frame.__init__(self, parent, title=title, style=(wx.DEFAULT_FRAME_STYLE | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX | wx.WS_EX_CONTEXTHELP), size=(500,300))
		
		# PANEL CODE (sometimes done as separate object, here one object together with frame)		
		self.panel = wx.Panel(self, size=(500,300))
		self.panel.SetBackgroundColour('#ededed')
		self.mainSizer = wx.BoxSizer(wx.VERTICAL)
		self.grid = wx.GridBagSizer(hgap=5, vgap=5)
	
		self.filepath = wx.TextCtrl(self, value="<your file path here>", pos=(150,60), size=(300,-1))
		self.browse = wx.Button(self.panel, label="Browse...")
		
		self.Bind(wx.EVT_BUTTON, self.OnBrowse, self.browse)
		
		self.grid.Add(self.filepath, pos=(1,1))
		self.grid.Add(self.browse, pos=(1, 3))
		
		self.mainSizer.Add(self.grid, 0, wx.ALL, 0)
		self.panel.SetSizerAndFit(self.mainSizer)
		
	def OnBrowse(self, event):
		print("Let's do some browsin'")
		# I don't know what some of the string arguments below are doing! I took this from the old phonetic simulation GUI 
		dlg = wx.FileDialog(self, "Choose a file", os.getcwd(), "", "*.wav", wx.OPEN)
		if dlg.ShowModal() == wx.ID_OK:
			self.filepath.Value = dlg.GetDirectory() + '\\' + dlg.GetFilename()