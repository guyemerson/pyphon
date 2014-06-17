import wx
#import pylab

#def piechart():
#	# make a square figure and axes
#	pylab.figure(1, figsize=(6,6))
#	ax = pylab.axes([0.1, 0.1, 0.8, 0.8]) # do we need this?
#
#	# The slices will be ordered and plotted counter-clockwise.
#	labels = "Correct", "Incorrect"
#	fracs = [15, 30]
#	explode=(0, 0)
#
#	pylab.pie(fracs, explode=explode, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
#    # The default startangle is 0, which would start the Frogs slice on the x-axis.
#    # With startangle=90, everything is rotated counter-clockwise by 90 degrees, so the plotting starts on the positive y-axis.
#
#	pylab.title("Performance", bbox={'facecolor':'0.8', 'pad':5})
#
#	pylab.show()


class StatsDialog(wx.Dialog):
	'''
	A custom dialogue box which allows you to choose some settings.
	'''
	def __init__(self, frame, title, size):
		wx.Dialog.__init__(self, parent=frame, title=title, size=size)
		
		self.panel = wx.Panel(self, size=(200,200))
		self.panel.SetBackgroundColour('#ededed')
		self.mainSizer = wx.BoxSizer(wx.VERTICAL)
		self.grid = wx.GridBagSizer(hgap=5, vgap=5)
		
		self.ok = wx.Button(self.panel, label="OK")
		self.Bind(wx.EVT_BUTTON, self.OnOK, self.ok)
		
		self.todayTrue  = frame.sessionStats[True]
		self.todayFalse = frame.sessionStats[False]
		
		self.today          = wx.StaticText(self.panel, label="Today:")
		self.correct        = wx.StaticText(self.panel, label="Correct")
		self.incorrect      = wx.StaticText(self.panel, label="Incorrect")
		self.total          = wx.StaticText(self.panel, label="Total")
		self.todayCorrect   = wx.StaticText(self.panel, label=str(self.todayTrue))
		self.todayIncorrect = wx.StaticText(self.panel, label=str(self.todayFalse))
		self.todayTotal     = wx.StaticText(self.panel, label=str(self.todayTrue + self.todayFalse))
		
		self.message = wx.StaticText(self.panel, label=
"""Coming soon:
- long-term statistics
- detailed performance breakdown
- graphs and visualisations""")
		
		self.grid.Add(self.today,     pos=(2,0))
		self.grid.Add(self.correct,   pos=(1,1))
		self.grid.Add(self.incorrect, pos=(1,2))
		self.grid.Add(self.total,     pos=(1,3))
		self.grid.Add(self.todayCorrect,   pos=(2,1))
		self.grid.Add(self.todayIncorrect, pos=(2,2))
		self.grid.Add(self.todayTotal,     pos =(2,3))
		self.grid.Add(self.message, pos=(4,1), span=(1,3))
		
		self.grid.Add(self.ok, pos=(6,2))
		
		self.mainSizer.Add(self.grid, 0, wx.ALL, 0)
		self.panel.SetSizerAndFit(self.mainSizer)
		
	def OnOK(self, event):
		self.Close()