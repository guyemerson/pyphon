#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import division
import wx, datetime
from copy import copy

import filewindow, statsdialog, optionsdialog, metadatapanel, trainingpanel

wx.USE_UNICODE = 1
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
		wx.Panel.__init__(self, parent, size=(400,int(400*GOLDEN)))
		
		self.parent = parent
		self.SetBackgroundColour("#ededed")
		self.mainSizer = wx.BoxSizer(wx.VERTICAL)
		
		# WIDGET CODE
		
		self.defaultLangText = "<choose language>"
		self.chooseLangChoices = [self.defaultLangText] + self.parent.trainLanguages
		self.chooseLanguage = wx.ComboBox(self, size=(160,-1), choices=self.chooseLangChoices, style=wx.CB_READONLY)
		self.chooseContrast = wx.ComboBox(self, size=(100,-1), choices=[], style=wx.CB_READONLY)
		self.chooseLanguage.SetStringSelection(self.defaultLangText)
		
		self.train = wx.Button(self, label="Train!")
		self.Bind(wx.EVT_BUTTON, self.OnTrain, self.train)
		self.Bind(wx.EVT_COMBOBOX, self.OnLanguage, self.chooseLanguage)
		self.Bind(wx.EVT_COMBOBOX, self.OnContrast, self.chooseContrast)
		
		self.train.Disable()
		self.chooseContrast.Disable()
		
		self.sessionFeedback = wx.StaticText(self, label="You have not trained so far today.")
		
		# GRID CODE
		
		self.grid = wx.GridBagSizer(hgap=10, vgap=10)
		self.grid.Add(self.sessionFeedback, pos=(1,0), span=(1,3))
		self.grid.Add(self.chooseLanguage, pos=(3,0))
		self.grid.Add(self.chooseContrast, pos=(3,1))
		self.grid.Add(self.train, pos=(3,2))
		
		self.mainSizer.Add(self.grid, 20, wx.EXPAND | wx.ALL, 20)
		self.SetSizerAndFit(self.mainSizer)
		
	
	def OnTrain(self, event):
		# Check that the current settings are valid
		assert self.parent.language in self.parent.trainLanguages
		assert self.parent.contrast in self.parent.trainContrasts
		
		# Switch panel
		self.parent.switchTraining()
		
		
	def feedback(self):
		# Training feedback message
		try:
			trainedTrue = self.parent.sessionStats[True]  - self.parent.initStats[True]
			trainedTotal = trainedTrue + self.parent.sessionStats[False] - self.parent.initStats[False]
			proportion = trainedTrue / trainedTotal
			self.sessionFeedback.SetLabel("In your last session you trained a total of {} reps \nand got {:.0%} correct.".format(trainedTotal, proportion))
		except ZeroDivisionError:
			print ("zero reps - no feedback")
			
	def OnLanguage(self, event):
		# Save the chosen language
		print (event.GetString())
		if self.parent.language != event.GetString():
			if self.defaultLangText in self.chooseLanguage.GetItems():
				self.chooseLanguage.SetItems(self.parent.trainLanguages)
			self.parent.language = event.GetString()
			self.train.Disable()
			# Find all contrasts for the language
			self.parent.trainContrasts = self.parent.allContrasts[self.parent.language]
			print (self.parent.trainContrasts)
			# Update the contrast dropdown menu
			self.defaultContrastText = "<contrast>"
			self.chooseContrastChoices = [self.defaultContrastText] + self.parent.trainContrasts
			self.chooseContrast.SetItems(self.chooseContrastChoices)
			self.chooseContrast.SetStringSelection(self.defaultContrastText)
		self.chooseContrast.Enable()

	def OnContrast(self, event):
		# Save the chosen contrast
		print (event.GetString())
		if event.GetString() != self.defaultContrastText and self.defaultContrastText in self.chooseContrast.GetItems():
			self.chooseContrast.SetItems(self.parent.trainContrasts)
		self.parent.contrast = event.GetString()
		self.train.Enable()
		


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
		
		self.sessionStats = {True: 0, False: 0}
		
		
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
		
		
		# DATABASE CODE (formerly in MainWindowPanel)
		
		self.cursor.execute("SELECT DISTINCT language FROM contrast_set")
		self.trainLanguages = sorted(x[0] for x in self.cursor)  # cursor returns a list of tuples
		print (self.trainLanguages)
		
		# The following will be updated as options are chosen
		self.trainContrasts = []
		self.language = None
		self.contrast = None


		# PANEL AND MENUS
		
		self.mainPanel = MainWindowPanel(self)
		self.trainingPanel = trainingpanel.TrainingPanel(self, size=(400,int(400*GOLDEN)))
		#self.trainingPanel.Hide()
		self.SetBackgroundColour("#ededed") # to cover up the fact that the panel seems not to be filling the frame...
		
		self.sizer = wx.BoxSizer(wx.HORIZONTAL)
		self.sizer.Add(self.mainPanel, 1, wx.EXPAND)
		self.sizer.Add(self.trainingPanel, 1, wx.EXPAND)
		self.SetSizer(self.sizer)
		self.sizer.Hide(self.trainingPanel)
		self.sizer.Layout()
		self.sizer.Show(self.mainPanel)
		self.sizer.Layout()
		
		self.CreateStatusBar()
		
		filemenu = wx.Menu()
		helpmenu = wx.Menu()
		
		menuDB = filemenu.Append(wx.ID_ANY, "Edit &Database", "View and edit the database")
		filemenu.AppendSeparator()
		#menuOptions = filemenu.Append(wx.ID_ANY, "&Settings", "Change settings")
		menuStats = filemenu.Append(wx.ID_ANY, "View my &stats", "Statistics of past performance")
		#menuHelp = helpmenu.Append(wx.ID_ANY, "&Help topics", "Help for this program")
		menuAbout = helpmenu.Append(wx.ID_ABOUT, "&About", " Information about this program") 
		menuExit = filemenu.Append(wx.ID_EXIT, "E&xit", " Terminate the program")
		# The StausBar messages seem to be persistent. How to get rid of them after rollover?
		# How to send commands to the StatusBar more directly? e.g. for showing today's stats, like in Anki
		
		# lots of menu & help menu code can be added here
		
		menuBar = wx.MenuBar()
		menuBar.Append(filemenu, "&File")
		menuBar.Append(helpmenu, "&Help")
		self.SetMenuBar(menuBar)
		
		#self.Bind(wx.EVT_MENU, self.OnOptions, menuOptions)
		self.Bind(wx.EVT_MENU, self.OnFile, menuDB)
		self.Bind(wx.EVT_MENU, self.OnStats, menuStats)
		#self.Bind(wx.EVT_MENU, self.OnHelp, menuHelp)
		self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
		self.Bind(wx.EVT_MENU, self.OnClose, menuExit)
		self.Bind(wx.EVT_CLOSE, self.OnClose)
	
		self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
	
		# WITH SPECIAL THANKS TO NATHAN OSMAN. WE LOVE YOU
	def switchTraining(self):
		self.sizer.Hide(self.mainPanel)
		self.sizer.Layout()
		self.sizer.Show(self.trainingPanel)
		self.sizer.Layout()
		self.initStats = copy(self.sessionStats)
		self.trainingPanel.prepareSession()
		
	def switchMain(self):
		self.sizer.Hide(self.trainingPanel)
		self.sizer.Layout()
		self.sizer.Show(self.mainPanel)
		self.sizer.Layout()
		self.mainPanel.feedback()


	def OnKeyDown(self, event):
		print "You pressed a key and the FRAME saw it"

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
		dlg = wx.MessageDialog(self,
u"""PyPhon is an open-source application for learning new sound contrasts in a foreign language.

For a simple introduction to the method used (High Variability Phonetic Training), see:
http://languagelog.ldc.upenn.edu/nll/?p=328 

This program is published under the GNU General Public License.

The authors are:
Guy Emerson (getemerson+pyphon@gmail.com)
Stanisław Pstrokoński (bigstas_lives@hotmail.com)""",  "About PyPhon 0.0", wx.OK | wx.ICON_INFORMATION)
		dlg.ShowModal()
		dlg.Destroy()
	
	def OnClose(self, event):
		# Here do all the things you want to do when closing, like saving data, and asking the user questions using dialog boxes
		self.Destroy()



#app = wx.App(False)
#frame = MainWindow(None, title="High Variability Phonetic Training software", cursor=cursor)
# provider = wx.SimpleHelpProvider()
# wx.HelpProvider_Set(provider)
#frame.Show()
#app.MainLoop()
