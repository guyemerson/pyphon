import wx

class OptionsDialog(wx.Dialog):
	'''
	A custom dialogue box which allows you to choose some settings.
	You have NO IDEA how hard this was to create!!
	'''
	def __init__(self, frame, title, size):
		wx.Dialog.__init__(self, parent=frame, title=title, size=size)
		
		self.parent = frame
		
		self.panel = wx.Panel(self, size=(200,200))
		self.panel.SetBackgroundColour('#ededed')
		self.mainSizer = wx.BoxSizer(wx.VERTICAL)
		self.grid = wx.GridBagSizer(hgap=5, vgap=5)
		
		self.profanity = wx.CheckBox(self, label="Allow swear words")
		self.ok = wx.Button(self.panel, label="OK")
		self.Bind(wx.EVT_BUTTON, self.OnOK, self.ok)
		
		self.grid.Add(self.profanity, pos=(1,0), span=(1,3))
		self.grid.Add(self.ok, pos=(3,1))
		
		self.mainSizer.Add(self.grid, 0, wx.ALL, 0)
		self.panel.SetSizerAndFit(self.mainSizer)
		
	def OnOK(self, event):
		self.parent.panel.allowProfanity = self.profanity.GetValue()
		print (self.parent.panel.allowProfanity)
		self.Close()