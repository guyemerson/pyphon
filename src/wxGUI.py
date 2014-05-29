#!/usr/bin/env python2

import wx, os, sqlite3

srcDir = os.getcwd()
dataDir = os.path.join(os.path.split(srcDir)[0], 'data')
datafile = os.path.join(dataDir, 'data.db')

import trainingwindow, filewindow, statsdialog



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
		wx.Panel.__init__(self, parent, size=(400,400))
		
		self.SetBackgroundColour("#ededed")
		self.mainSizer = wx.BoxSizer(wx.VERTICAL)

		# DATABASE CODE
		
		with sqlite3.connect(datafile) as data:
			self.cur = data.cursor()
		self.cur.execute("SELECT DISTINCT language FROM contrast_set")
		self.all_languages = sorted(x[0] for x in self.cur)  # cur returns a list of tuples
		print (self.all_languages)
		
		# The following will be updated as options are chosen
		self.all_contrasts = []
		self.language = None
		self.contrast = None
		
		# WIDGET CODE
		
		self.chooseLanguage = wx.ComboBox(self, size=(95,-1), choices=["-"] + self.all_languages, style=wx.CB_READONLY)
		self.chooseContrast = wx.ComboBox(self, size=(95,-1), choices=["-"], style=wx.CB_READONLY)
		# The following line will be removed eventually
		self.chooseLanguage.Append("Polish")
		
		self.train = wx.Button(self, label="Train!")
		self.Bind(wx.EVT_BUTTON, self.OnTrain, self.train)
		self.Bind(wx.EVT_COMBOBOX, self.OnChooseLanguage, self.chooseLanguage)
		self.Bind(wx.EVT_COMBOBOX, self.OnChooseContrast, self.chooseContrast)
		
		# GRID CODE
		
		self.grid = wx.GridBagSizer(hgap=10, vgap=10)
		self.grid.Add(self.chooseLanguage, pos=(3,0))
		self.grid.Add(self.chooseContrast, pos=(3,1))
		self.grid.Add(self.train, pos=(3,2))
		
		self.mainSizer.Add(self.grid, 20, wx.ALL, 20)
		self.SetSizerAndFit(self.mainSizer)
		
	def OnBritish(self, event):
		# This function will probably be removed
		if True: # this should depend on the button label
			chosenLanguage = "British English"
		if True: # need to have actual choice here
			chosenContrast = "th-s"
		trainingTitle = chosenLanguage + " | " + chosenContrast
		secondWindow = trainingwindow.TrainingWindow(None, trainingTitle, self.cur, chosenLanguage, chosenContrast)
		secondWindow.Show()
		secondWindow.moo.Hide(), secondWindow.quack.Hide(), secondWindow.next.Hide()
		#self.english.Hide(), self.polish.Hide()	
	
		#font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
		#font.SetPointSize(20)			
		#self.waitingText = wx.StaticText(self.panel, label="A session is underway.\nPlease finish your session before starting a new one.")
		#self.waitingText.SetFont(font)
		#self.grid.Add(self.waitingText, pos=(3,0))  -- Doesn't seem to respond to grid placement
	
	def OnTrain(self, event):
		# Check that the current settings are valid
		assert self.language in self.all_languages
		assert self.contrast in self.all_contrasts
		# Open a new window
		trainingTitle = self.language + " | " + self.contrast
		self.trainingWindow = trainingwindow.TrainingWindow(None, trainingTitle, self.cur, self.language, self.contrast)
		
	
	def OnChooseLanguage(self, event):
		# Save the chosen language
		print (event.GetString())
		self.language = event.GetString()
		# Find all contrasts for the language
		self.cur.execute("SELECT contrast FROM contrast_set WHERE language = ?", (self.language,))
		self.all_contrasts = sorted(x[0] for x in self.cur)
		print (self.all_contrasts)
		# Update the contrast dropdown menu
		self.chooseContrast.SetItems(['-'] + self.all_contrasts)

	def OnChooseContrast(self, event):
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
	def __init__(self, parent, title):
		wx.Frame.__init__(self, parent, title=title, style=(wx.DEFAULT_FRAME_STYLE | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX | wx.WS_EX_CONTEXTHELP), size=(400,400))

		self.panel = MainWindowPanel(self)	

		# MENU CODE
		
		self.CreateStatusBar()   # would be nice to have Golden Ratio proportions
		
		filemenu = wx.Menu()
		helpmenu = wx.Menu()
		
		menuAdd = filemenu.Append(wx.ID_ANY, "A&dd", "Add sound files to the database")
		menuStats = filemenu.Append(wx.ID_ANY, "View my s&tats", "Statistics of past performance")
		menuHelp = helpmenu.Append(wx.ID_ANY, "&Help topics", "You could always call Stas for help")
		menuAbout = helpmenu.Append(wx.ID_ABOUT, "&About", " Information about this program")
#		helpmenu.AppendSeparator() 
		menuExit = filemenu.Append(wx.ID_EXIT, "E&xit", " Terminate the program")
		# The StausBar messages seem to be persistent. How to get rid of them after rollover?
		# How to send commands to the StatusBar more directly? e.g. for showing today's stats, like in Anki
		
		# lots of menu & help menu code can be added here
		
		menuBar = wx.MenuBar()
		menuBar.Append(filemenu, "&File")
		menuBar.Append(helpmenu, "&Help")
		self.SetMenuBar(menuBar)
		
		self.Bind(wx.EVT_MENU, self.OnFile, menuAdd)
		self.Bind(wx.EVT_MENU, self.OnStats, menuStats)
		self.Bind(wx.EVT_MENU, self.OnHelp, menuHelp)
		self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
		self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
	

	def OnFile(self, event):
		'''Opens FileWindow.'''
		secondWindow = filewindow.FileWindow(None, "File Submission")
		secondWindow.Show()
	def OnStats(self, event):
		'''Brings up stats. Used to be dialogue box, now runs statsdialog's pie chart using pylab.'''
		#dlg = wx.MessageDialog(self, "Your stats are great!\nStas and Guy will have a display ready for you in no time.", "User Statistics", wx.OK) 
		#dlg.ShowModal()
		#dlg.Destroy()
		statsdialog.piechart()  # this has some weird bugginess. 
		# When I run it for the first time in wxGUI it seems to be loading indefinitely. 
		# But if I first load it independently through statsdialog, then run wxGUI, then it works fine. This could be a real issue for users.
	def OnHelp(self, event):
		dlg = wx.MessageDialog(self, "Here is a message.\nEnjoy!", "Help for this program", wx.OK | wx.ICON_INFORMATION)
		dlg.ShowModal()
		dlg.Destroy()
	def OnAbout(self, event):
		dlg = wx.MessageDialog(self, "What's this? Another message?\nWow Stas, you are so full of surprises!", "More fun messages", wx.OK | wx.ICON_INFORMATION)
		dlg.ShowModal()
		dlg.Destroy()
	def OnExit(self, event):
		self.Close(True) # also want to close all other windows


# provider = wx.SimpleHelpProvider()
# wx.HelpProvider_Set(provider)

app = wx.App(False)
frame = MainWindow(None, title="High Variability Phonetic Training software")

# nb = wx.Notebook(frame)
# nb.AddPage(whatever_panel_you_made(nb), "whatever panel name")

frame.Show()
app.MainLoop()