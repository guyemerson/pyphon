#!/usr/bin/env python2

from __future__ import division
import wx, datetime
from copy import copy

import trainingdialog, filewindow, statsdialog, optionsdialog, metadatapanel, databasegridpanel

GOLDEN = 0.61803398875

class MainWindowPanel(wx.Panel):
	'''
	This is the panel (i.e. container/organiser for widgets) which is used by the frame MainWindow. ("Frame" is the wx word for what we would call "window").
	
	The panel contains:
	- widgets (buttons and ComboBoxes) and their methods
	- database interaction (to fetch language and contrast options)
	- a GridBagSizer for organising the widgets in the panel
	- a BoxSizer as a "main sizer", in which the GridBagSizer fits
	'''
	def __init__(self, parent):
		"""
		cursor - SQLite3 cursor object
		"""
		wx.Panel.__init__(self, parent, size=(400,int(400*GOLDEN)))
		
		self.SetBackgroundColour("#ededed")
		self.mainSizer = wx.BoxSizer(wx.VERTICAL)

		# DATABASE CODE
		
		self.cursor = parent.cursor
		self.cursor.execute("SELECT DISTINCT language FROM contrast_set")
		self.trainLanguages = sorted(x[0] for x in self.cursor)  # cursor returns a list of tuples
		print (self.trainLanguages)
		
		self.allContrasts = parent.allContrasts
		
		# The following will be updated as options are chosen
		self.trainContrasts = []
		self.language = None
		self.contrast = None
		
		self.sessionStats = {True: 0, False: 0}
		
		# WIDGET CODE
		
		self.chooseLanguage = wx.ComboBox(self, size=(140,-1), choices=self.trainLanguages, style=wx.CB_READONLY)
		self.chooseContrast = wx.ComboBox(self, size=(95,-1), choices=["-"], style=wx.CB_READONLY)
		
		self.train = wx.Button(self, label="Train!")
		self.Bind(wx.EVT_BUTTON, self.OnTrain, self.train)
		self.Bind(wx.EVT_COMBOBOX, self.OnLanguage, self.chooseLanguage)
		self.Bind(wx.EVT_COMBOBOX, self.OnContrast, self.chooseContrast)
		
		self.sessionFeedback = wx.StaticText(self, label="You have not trained so far today.")
		
		# GRID CODE
		
		self.grid = wx.GridBagSizer(hgap=10, vgap=10)
		self.grid.Add(self.sessionFeedback, pos=(1,0), span=(1,3))
		self.grid.Add(self.chooseLanguage, pos=(3,0))
		self.grid.Add(self.chooseContrast, pos=(3,1))
		self.grid.Add(self.train, pos=(3,2))
		
		self.mainSizer.Add(self.grid, 20, wx.ALL, 20)
		self.SetSizerAndFit(self.mainSizer)
		
	
	def OnTrain(self, event):
		# Check that the current settings are valid
		assert self.language in self.trainLanguages
		assert self.contrast in self.trainContrasts
		# Open a new window
		initStats = copy(self.sessionStats)
		trainingTitle = self.language + " | " + self.contrast
		dlg = trainingdialog.TrainingDialog(self, trainingTitle, (270,int(GOLDEN*300)), self.cursor, self.language, self.contrast)
		dlg.ShowModal()
		dlg.Destroy()
		# Training feedback message
		try:
			trainedTrue = self.sessionStats[True]  - initStats[True]
			trainedTotal = trainedTrue + self.sessionStats[False] - initStats[False]
			proportion = trainedTrue / trainedTotal
			self.sessionFeedback.SetLabel("In your last session you trained a total of {} reps \nand got {:.0%} correct.".format(trainedTotal, proportion))
		except ZeroDivisionError:
			print ("zero reps - no feedback")
			
	def OnLanguage(self, event):
		# Save the chosen language
		print (event.GetString())
		self.language = event.GetString()
		# Find all contrasts for the language
		self.trainContrasts = self.allContrasts[self.language]
		print (self.trainContrasts)
		# Update the contrast dropdown menu
		self.chooseContrast.SetItems(self.trainContrasts)

	def OnContrast(self, event):
		# Save the chosen contrast
		print (event.GetString())
		self.contrast = event.GetString()
		


class MainWindow(wx.Frame):
	'''
	This is the main frame (wx word for what we would call a "window") for the whole program.
	The purpose of this frame is to link to training and file input, and (hopefully) to be pretty.
	
	The frame contains:
	- a panel (coded above)
	- a menu bar
	- menu options and their methods
	- a "status bar" (the little info strip at the bottom)
	'''
	def __init__(self, parent, title, cursor):
		"""
		cursor - SQLite3 cursor object
		"""
		wx.Frame.__init__(self, parent, title=title, style=(wx.DEFAULT_FRAME_STYLE | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX | wx.WS_EX_CONTEXTHELP), size=(400,int(400*GOLDEN)))
		
		# DATABASE ACCESS
		
		self.cursor = cursor
		
		self.cursor.execute("SELECT * FROM language_set")
		self.allLanguages = [x[0] for x in self.cursor]
		self.allContrasts = {x:[] for x in self.allLanguages} # Initialise with empty lists
		self.allSpeakers  = {x:[] for x in self.allLanguages}
		
		self.metaData = (self.allLanguages, self.allContrasts, self.allSpeakers)
		
		for i, table in ((1, "contrast_set"), (2, "speaker_set")):
			self.cursor.execute("SELECT * FROM {}".format(table))
			for language, entry in self.cursor:
				self.metaData[i][language].append(entry)
			for language in self.allLanguages:
				self.metaData[i][language].sort()
		
		# PANEL AND MENUS
		
		self.panel = MainWindowPanel(self)
		
		self.CreateStatusBar()   # would be nice to have Golden Ratio proportions
		
		filemenu = wx.Menu()
		helpmenu = wx.Menu()
		
		menuDB = filemenu.Append(wx.ID_ANY, "Edit &Database", "view and edit the database")
		filemenu.AppendSeparator()
		menuOptions = filemenu.Append(wx.ID_ANY, "&Settings", "change settings")
		menuStats = filemenu.Append(wx.ID_ANY, "View my &stats", "Statistics of past performance")
		menuHelp = helpmenu.Append(wx.ID_ANY, "&Help topics", "You could always call Stas for help")
		menuAbout = helpmenu.Append(wx.ID_ABOUT, "&About", " Information about this program") 
		menuExit = filemenu.Append(wx.ID_EXIT, "E&xit", " Terminate the program")
		# The StausBar messages seem to be persistent. How to get rid of them after rollover?
		# How to send commands to the StatusBar more directly? e.g. for showing today's stats, like in Anki
		
		# lots of menu & help menu code can be added here
		
		menuBar = wx.MenuBar()
		menuBar.Append(filemenu, "&File")
		menuBar.Append(helpmenu, "&Help")
		self.SetMenuBar(menuBar)
		
		self.Bind(wx.EVT_MENU, self.OnOptions, menuOptions)
		self.Bind(wx.EVT_MENU, self.OnFile, menuDB)
		self.Bind(wx.EVT_MENU, self.OnStats, menuStats)
		self.Bind(wx.EVT_MENU, self.OnHelp, menuHelp)
		self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
		self.Bind(wx.EVT_MENU, self.OnClose, menuExit)
		self.Bind(wx.EVT_CLOSE, self.OnClose)
	

	def OnFile(self, event):
		'''Opens FileWindow.'''
		secondWindow = filewindow.FileWindow(self, "File Submission")
		secondWindow.Show()
	
	def OnStats(self, event):
		'''Brings up stats. Used to be a pie chart using pylab, now a dialogue box.'''
		#dlg = wx.MessageDialog(self, "Your stats are great!\nStas and Guy will have a display ready for you in no time.", "User Statistics", wx.OK) 
		dlg = statsdialog.StatsDialog(self, title="Statistics Summary", size=(300,300))
		dlg.ShowModal()
		dlg.Destroy()
	
	def OnOptions(self, event):
		dlg = optionsdialog.OptionsDialog(self, "Settings", (200,200))
		dlg.ShowModal()
		dlg.Destroy()
	
	def OnHelp(self, event):
		dlg = wx.MessageDialog(self, "Here is a message.\nEnjoy!", "Help for this program", wx.OK | wx.ICON_INFORMATION)
		dlg.ShowModal()
		dlg.Destroy()
	
	def OnAbout(self, event):
		dlg = wx.MessageDialog(self, "What's this? Another message?\nWow Stas, you are so full of surprises!", "More fun messages", wx.OK | wx.ICON_INFORMATION)
		dlg.ShowModal()
		dlg.Destroy()
	
	def OnClose(self, event):
		# Here do all the things you want to do when closing, like saving data, and asking the user questions using dialog boxes
		"""
		with open(userdata, 'a') as f:
			print (str(self.panel.sessionStats))
			f.write(str(datetime.date.today()))
			f.write(str(self.panel.sessionStats))
			f.write("\n")
		"""
		dlg = wx.MessageDialog(self, "Jesus has changed your life.\nSave changes?", "Important", wx.YES | wx.NO | wx.ICON_QUESTION)
		dlg.ShowModal()
		self.Destroy()



#app = wx.App(False)
#frame = MainWindow(None, title="High Variability Phonetic Training software", cursor=cursor)
# provider = wx.SimpleHelpProvider()
# wx.HelpProvider_Set(provider)
#frame.Show()
#app.MainLoop()
