import wx

class OptionsDialog(wx.Dialog):
	'''
	A custom dialogue box which allows you to choose some settings.
	You have NO IDEA how hard this was to create!!
	'''
	def __init__(self, frame, title, size):
		wx.Dialog.__init__(self, parent=frame, title=title, size=size)
		
		self.panel = wx.Panel(self, size=(200,200))
		self.panel.SetBackgroundColour('#ededed')
		self.mainSizer = wx.BoxSizer(wx.VERTICAL)
		self.grid = wx.GridBagSizer(hgap=5, vgap=5)
		
		self.profanity = wx.CheckBox(self, label="Allow swear words")
		
		self.grid.Add(self.profanity, pos=(1,0))
		
		self.mainSizer.Add(self.grid, 0, wx.ALL, 0)
		self.panel.SetSizerAndFit(self.mainSizer)