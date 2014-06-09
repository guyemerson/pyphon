import wx, os
import wx.grid


class SimpleGrid(wx.grid.Grid):
	def __init__(self, parent):
		wx.grid.Grid.__init__(self, parent, -1)
		
		self.CreateGrid(10,4)
		#self.SetColLabelValue(0, "Language")
		#self.SetRowLabelValue(0, "First")
		#self.SetCellValue(0,0,"hello")
		#self.SetCellValue(0,1,"stuff")
		#self.SetCellValue(1,1,"more stuff")



class DatabaseGridPanel(wx.Panel):
	def __init__(self, parent, headings):
		wx.Panel.__init__(self, parent, size=(400,400))
		
		self.headings = headings
		
		self.panel = wx.Panel(self, size=(300,300))
		self.panel.SetBackgroundColour('#ededed')
		self.mainSizer = wx.BoxSizer(wx.VERTICAL)
		self.grid = wx.GridBagSizer(hgap=5, vgap=5)
		
		self.sheet = SimpleGrid(self)
		self.browse = wx.Button(self, label="Browse...")
		
		self.grid.Add(self.sheet, pos=(0,0),span=(10,5))
		self.grid.Add(self.browse, pos=(2,6))
		self.mainSizer.Add(self.grid, 0, wx.ALL, 0)
		self.panel.SetSizerAndFit(self.mainSizer)
		
		self.Bind(wx.EVT_BUTTON, self.OnBrowse, self.browse)
		
	def OnBrowse(self, event):
		print("Let's do some browsin'")
		dlg = wx.FileDialog(self, "Choose a file", defaultDir=os.getcwd(), defaultFile="", wildcard="*.wav", style=wx.FD_MULTIPLE)
		if dlg.ShowModal() == wx.ID_OK:
			print (dlg.GetFilenames())
			i = 0
			for filename in dlg.GetFilenames():
				self.sheet.SetCellValue(row=i,col=0, s=filename)
				self.sheet.SetCellValue(row=i, col=1, s="<insert sound>")
				self.sheet.SetCellValue(row=i, col=2, s="...")
				i +=1



class AddDataGridPanel(DatabaseGridPanel):
	def __init__(self, parent):
		DatabaseGridPanel.__init__(self, parent=parent, headings=["Filename", "Answer", "Language", "Speaker"])
		
		for i, heading in enumerate(self.headings):
			self.sheet.SetColLabelValue(i, heading)
		self.sheet.SetRowLabelValue(0, "First")

		self.sheet.SetCellValue(0,0,"hello")
		self.sheet.SetCellValue(0,1,"stuff")
		self.sheet.SetCellValue(1,1,"more stuff")


class MinimalPairsGridPanel(DatabaseGridPanel):
	def __init__(self, parent):
		DatabaseGridPanel.__init__(self, parent=parent, headings=["Language", "Contrast", "Option 1", "Option 2"])


class TestFrame(wx.Frame):
	def __init__(self, parent):
		wx.Frame.__init__(self, parent, -1, "A Grid", size=(200,200))
		
		#grid = SimpleGrid(self)
		
		self.panel = AddDataGridPanel(self)
		
		
#app = wx.App(False)
#frame = TestFrame(None)
#frame.Show(True)
#app.MainLoop()