#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import division
import wx, datetime
from copy import copy

import filewindow, statsdialog, optionsdialog, metadatapanel, trainingpanel

wx.USE_UNICODE = 1
GOLDEN = 0.61803398875  # using the golden ratio to make windows in prettier proportions :)


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
		wx.Panel.__init__(self, parent, size=(420,int(420*GOLDEN)))
		
		self.parent = parent
		self.SetBackgroundColour("#ededed")
		self.mainSizer = wx.BoxSizer(wx.VERTICAL)
		
		# WIDGET CODE
		
		self.defaultLangText = "<choose language>"
		self.chooseLangChoices = [self.defaultLangText] + self.parent.trainLanguages  # the list of options of languages is the available languages plus '<choose language>'
		self.chooseLanguage = wx.ComboBox(self, size=(160,-1), choices=self.chooseLangChoices, style=wx.CB_READONLY)  # language drop-down menu
		self.chooseContrast = wx.ComboBox(self, size=(100,-1), choices=[], style=wx.CB_READONLY)  # contrast drop-down menu, initially with an empty list of options as language is yet to be selected
		self.chooseLanguage.SetStringSelection(self.defaultLangText)  # on start-up, '<choose language>' is automatically selected
		
		self.train = wx.Button(self, label="Train!")  # 'train' button
		self.Bind(wx.EVT_BUTTON, self.OnTrain, self.train)
		self.Bind(wx.EVT_COMBOBOX, self.OnLanguage, self.chooseLanguage)
		self.Bind(wx.EVT_COMBOBOX, self.OnContrast, self.chooseContrast)
		
		self.train.Disable()  # 'train' button is disabled until both language and contrast have been chosen
		self.chooseContrast.Disable()  # cannot choose contrast until language has been chosen
		
		self.sessionFeedback = wx.StaticText(self, label="You have not trained so far today.")  # text telling you about your training
		
		# GRID CODE
		# this is the way in which the widgets are laid out. pos=(y,x).
		
		self.grid = wx.GridBagSizer(hgap=10, vgap=10)
		self.grid.Add(self.sessionFeedback, pos=(1,0), span=(1,3))
		self.grid.Add(self.chooseLanguage, pos=(3,0))
		self.grid.Add(self.chooseContrast, pos=(3,1))
		self.grid.Add(self.train, pos=(3,2))
		
		# the grid goes in the mainSizer, and the mainSizer is the overall sizer for the panel.
		self.mainSizer.Add(self.grid, 20, wx.EXPAND | wx.ALL, 20)
		self.SetSizerAndFit(self.mainSizer)
		
	
	def OnTrain(self, event):
		'''Switches to the TrainingPanel, where the training happens.
		This method is used when you press the 'train' button.'''
		# Check that the current settings are valid
		assert self.parent.language in self.parent.trainLanguages
		assert self.parent.contrast in self.parent.trainContrasts
		
		# Switch panel
		self.parent.switchTraining()
		
		
	def feedback(self):
		'''Training feedback message.
		Shows up in the MainPanel after you have completed training and returned to the MainPanel from the TrainingPanel by pressing the Stop button.'''
		try:
			trainedTrue = self.parent.sessionStats[True]  - self.parent.initStats[True]
			trainedTotal = trainedTrue + self.parent.sessionStats[False] - self.parent.initStats[False]
			proportion = trainedTrue / trainedTotal
			self.sessionFeedback.SetLabel("In your last session you trained a total of {} reps \nand got {:.0%} correct.".format(trainedTotal, proportion))
		except ZeroDivisionError:
			print ("zero reps - no feedback")
		
			
	def OnLanguage(self, event):
		'''
		Save the chosen language. Reset the contrast. Remove '<choose language>' as an option, if it is there.
		Disable the 'train' button (if enabled), since both language and contrast need to be chosen to be able to proceed.
		This all happens when a language is chosen in the drop-down menu.
		'''
		print (event.GetString())
		if self.parent.language != event.GetString(): # you only need to do anything if you've actually changed the language
			if self.defaultLangText in self.chooseLanguage.GetItems():     # if '<choose language>' is still one of the options...
				self.chooseLanguage.SetItems(self.parent.trainLanguages)   # ...make the options only the available languages, i.e. not including '<choose language>'...
				self.chooseLanguage.SetStringSelection(event.GetString())  # ...and set the clicked option to be selected
			self.parent.language = event.GetString()
			self.train.Disable() # since you now need to choose a contrast, and you can't press 'train' until you've selected both language and contrast
			self.parent.trainContrasts = self.parent.allContrasts[self.parent.language]  # Find all contrasts for the language
			print (self.parent.trainContrasts)
			# Update the contrast dropdown menu
			self.defaultContrastText = "<contrast>"
			self.chooseContrastChoices = [self.defaultContrastText] + self.parent.trainContrasts
			self.chooseContrast.SetItems(self.chooseContrastChoices)
			self.chooseContrast.SetStringSelection(self.defaultContrastText)
		self.chooseContrast.Enable()  # now you can choose a contrast from this drop-down menu
		
		# NOTE: the SetStringSelection method is automatically implemented when a selection is made in the drop-down menu.
		# Therefore, it does not normally need to be used explicitly, and isn't in this method in the case where '<choose language>' is not in self.chooseLanguage.GetItems() (i.e. the drop-down menu options list).
		# The reason it needs to be used explicitly in the 'if' statement is that the entire contents of the drop-down box has been refreshed with SetItems, which means the program needs 'reminding' of what should be selected.


	def OnContrast(self, event):
		'''
		Save the chosen contrast. 
		
		This happens when a contrast is chosen in the drop-down menu.
		'''
		# Save the chosen contrast
		print (event.GetString())
		if event.GetString() != self.defaultContrastText and self.defaultContrastText in self.chooseContrast.GetItems():
		# if the chosen contrast isn't '<choose contrast>' and '<choose contrast>' is still an available option in the drop-down menu...
			self.chooseContrast.SetItems(self.parent.trainContrasts)   # ...make the options only the available contrasts, i.e. not including '<choose contrast>'...
			self.chooseContrast.SetStringSelection(event.GetString())  # ...and set the clicked option to be selected
			self.train.Enable()  # now you can press the 'train' button, as both language and contrast have been selected
		self.parent.contrast = event.GetString()
		# NOTE: see final note in OnLanguage method. The same applies to this method.
		


class MainWindow(wx.Frame):
	'''
	This is the main frame (wx word for what we would call a "window") for the whole program.
	The purpose of this frame is to link to training and file input.
	In this frame, when you choose to train by pressing the 'train' button, you switch from the MainWindowPanel to the TrainingPanel.
	You can access file input and other features via the menu bar (toolbar) of this frame.
	
	The frame contains:
	- a panel (coded above)
	- a menu bar/toolbar
	- menu options and their methods
	- a "status bar" (the little info strip at the bottom)
	'''
	def __init__(self, parent, title, cursor):
		"""
		cursor - SQLite3 cursor object
		"""
		wx.Frame.__init__(self, parent, title=title, style=(wx.DEFAULT_FRAME_STYLE | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX | wx.WS_EX_CONTEXTHELP), size=(420,int(420*GOLDEN)))
		
		# at the beginning, you have answered no questions correctly and no questions incorrectly
		self.sessionStats = {True: 0, False: 0}
		
		
		# DATABASE ACCESS
		
		self.cursor = cursor
		
		self.cursor.execute("SELECT * FROM language_set")
		self.allLanguages = [x[0] for x in self.cursor]  # the first column of the table
		self.allContrasts = {x:[] for x in self.allLanguages} # Initialise with empty lists
		self.allSpeakers  = {x:[] for x in self.allLanguages}
		
		self.metaData = (self.allLanguages, self.allContrasts, self.allSpeakers)
		
		for i, table in ((1, "contrast_set"), (2, "speaker_set")):
			self.cursor.execute("SELECT * FROM {}".format(table))  # select all elements from "contrast_set" (and later "speaker_set")
			for language, entry in self.cursor:  # I'm not so sure what's going on here, could you document this Guy? -- Staś
				self.metaData[i][language].append(entry)
			for language in self.allLanguages:
				self.metaData[i][language].sort()
		
		
		# DATABASE CODE (formerly in MainWindowPanel)
		
		self.cursor.execute("SELECT DISTINCT language FROM contrast_set")  # Guy?
		self.trainLanguages = sorted(x[0] for x in self.cursor)  # cursor returns a list of tuples
		print (self.trainLanguages)
		
		# The following will be updated as options are chosen
		self.trainContrasts = []
		self.language = None
		self.contrast = None


		# PANEL AND MENUS
		
		# attach the panels to the frame
		self.mainPanel = MainWindowPanel(self)
		self.trainingPanel = trainingpanel.TrainingPanel(self, size=(420,int(420*GOLDEN)))
		self.SetBackgroundColour("#ededed")
		
		self.sizer = wx.BoxSizer(wx.HORIZONTAL)
		self.sizer.Add(self.mainPanel, 1, wx.EXPAND)
		self.sizer.Add(self.trainingPanel, 1, wx.EXPAND)
		self.SetSizer(self.sizer)
		self.sizer.Hide(self.trainingPanel) # we want to hide the TrainingPanel at the start
		self.sizer.Layout()
		self.sizer.Show(self.mainPanel) # we want to see the MainWindowPanel at the start
		self.sizer.Layout()
		
		self.CreateStatusBar() # this is that little ribbon at the bottom which gives you messages when you highlight certain things
		
		# toolbar menus
		filemenu = wx.Menu()
		helpmenu = wx.Menu()
		
		# adding options to each menu
		menuDB = filemenu.Append(wx.ID_ANY, "Edit &Database", "View and edit the database")
		filemenu.AppendSeparator()  # this is that horizontal line between options in the filemenu
		#menuOptions = filemenu.Append(wx.ID_ANY, "&Settings", "Change settings")
		menuStats = filemenu.Append(wx.ID_ANY, "View my &stats", "Statistics of past performance")
		#menuHelp = helpmenu.Append(wx.ID_ANY, "&Help topics", "Help for this program")
		menuAbout = helpmenu.Append(wx.ID_ABOUT, "&About", " Information about this program") 
		menuExit = filemenu.Append(wx.ID_EXIT, "E&xit", " Terminate the program")
		# The StausBar messages seem to be persistent. How to get rid of them after rollover?
		# How to send commands to the StatusBar more directly? e.g. for showing today's stats, like in Anki
		
		# lots of menu & help menu code can be added here
		
		# Now to add the toolbar menus to an actual toolbar, and attach this toolbar to the frame
		menuBar = wx.MenuBar()
		menuBar.Append(filemenu, "&File")
		menuBar.Append(helpmenu, "&Help")
		self.SetMenuBar(menuBar)
		
		# EVENT BINDING - attaching methods to events. Here mostly clicking on menus. Also closing the program.
		#self.Bind(wx.EVT_MENU, self.OnOptions, menuOptions)
		self.Bind(wx.EVT_MENU, self.OnFile, menuDB)
		self.Bind(wx.EVT_MENU, self.OnStats, menuStats)
		#self.Bind(wx.EVT_MENU, self.OnHelp, menuHelp)
		self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
		self.Bind(wx.EVT_MENU, self.OnClose, menuExit)
		self.Bind(wx.EVT_CLOSE, self.OnClose)
	
		# WITH SPECIAL THANKS TO NATHAN OSMAN. WE LOVE YOU
	def switchTraining(self):
		'''Switch from MainWindowPanel to TrainingPanel.
		Happens when the 'train' button is pressed.'''
		self.sizer.Hide(self.mainPanel)
		self.sizer.Layout()
		self.sizer.Show(self.trainingPanel)
		self.sizer.Layout()
		self.initStats = copy(self.sessionStats)
		self.trainingPanel.prepareSession()
		
	def switchMain(self):
		'''Switch from TrainingPanel to MainWindowPanel.
		Happens when the 'stop' button is pressed.'''
		self.sizer.Hide(self.trainingPanel)
		self.sizer.Layout()
		self.sizer.Show(self.mainPanel)
		self.sizer.Layout()
		self.mainPanel.feedback() # changes the feedback text to let you know how well you did in the previous session

	def OnFile(self, event):
		'''Opens FileWindow.
		FileWindow is the place where you can edit the database.'''
		secondWindow = filewindow.FileWindow(self, "File Submission")
		secondWindow.Show()
	
	def OnStats(self, event):
		'''Brings up stats. Used to be a pie chart using pylab, now a dialogue box.'''
		#dlg = wx.MessageDialog(self, "Your stats are great!\nStas and Guy will have a display ready for you in no time.", "User Statistics", wx.OK) 
		dlg = statsdialog.StatsDialog(self, title="Statistics Summary", size=(300,300))
		dlg.ShowModal()
		dlg.Destroy()
	
	def OnOptions(self, event):
		'''Brings up the Options dialogue box.'''
		dlg = optionsdialog.OptionsDialog(self, "Settings", (200,200))
		dlg.ShowModal()
		dlg.Destroy()
	
	def OnHelp(self, event):
		'''Brings up the Help dialogue box.'''
		dlg = wx.MessageDialog(self, "Here is a message.\nEnjoy!", "Help for this program", wx.OK | wx.ICON_INFORMATION)
		dlg.ShowModal()
		dlg.Destroy()
	
	def OnAbout(self, event):
		'''Brings up the About dialogue box.'''
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
		'''Here do all the things you want to do when closing, like saving data, and asking the user questions using dialog boxes.
		At the moment, nothing particularly exciting happens, it just closes the program.'''
		self.Destroy()
