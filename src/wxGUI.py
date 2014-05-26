#!/usr/bin/env python2

import wx, os, sys, sqlite3

srcDir = os.getcwd()
dataDir = os.path.join(os.path.split(srcDir)[0], 'data')
datafile = os.path.join(dataDir, 'data.db')

import trainingwindow, filewindow



class MainWindowPanel(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, size=(400,400))
		
		self.SetBackgroundColour("#ededed")
		self.mainSizer = wx.BoxSizer(wx.VERTICAL)

		# DATABASE CODE
		
		with sqlite3.connect(datafile) as data:
			cur = data.cursor()
		cur.execute("SELECT language FROM samples")
		languages = sorted(set(cur))  # this appears to be a list with a tuple in it?
		print (languages)
		# LANGUAGES SHOULD BE NAMED THE SAME AS BUTTONS/COMBO-BOX OPTIONS for simplicity
		languageOptions = [x[0] for x in languages] # produces a list of strings from a list of tuples - not thoroughly tested yet
		languageOptions.insert(0, "-")
		contrastOptions = ["-"]
		print (languageOptions)
		self.chooseLanguage = wx.ComboBox(self, size=(95,-1), choices=languageOptions, style=wx.CB_READONLY)
		self.chooseContrast = wx.ComboBox(self, size=(95,-1), choices=contrastOptions, style=wx.CB_READONLY)
		self.chooseLanguage.Append("Polish")
		
		# WIDGET CODE
		
		self.english = wx.Button(self, label="British English")
		self.polish = wx.Button(self, label="Polski")
		self.Bind(wx.EVT_BUTTON, self.OnBritish, self.english)
		self.Bind(wx.EVT_BUTTON, self.OnBritish, self.polish)
		self.Bind(wx.EVT_COMBOBOX, self.OnChooseLanguage, self.chooseLanguage)
		self.Bind(wx.EVT_COMBOBOX, self.OnChooseContrast, self.chooseContrast)
		
		# GRID CODE
		
		self.grid = wx.GridBagSizer(hgap=10, vgap=10)
		self.grid.Add(self.english, pos=(0,0))
		self.grid.Add(self.polish, pos=(1,0))
		self.grid.Add(self.chooseLanguage, pos=(3,1))
		self.grid.Add(self.chooseContrast, pos=(3,2))
		
		self.mainSizer.Add(self.grid, 20, wx.ALL, 20)
		self.SetSizerAndFit(self.mainSizer)
		
	def OnBritish(self, event):
		if True: # this should depend on the button label
			chosenLanguage = "British English"
		if True: # need to have actual choice here
			chosenContrast = "s-th"
		trainingTitle = chosenLanguage + " | " + chosenContrast
		secondWindow = trainingwindow.TrainingWindow(None, trainingTitle, chosenLanguage, chosenContrast)
		secondWindow.Show()
		secondWindow.moo.Hide(), secondWindow.quack.Hide(), secondWindow.next.Hide()
#		self.english.Hide(), self.polish.Hide()	

#		font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
#		font.SetPointSize(20)			
#		self.waitingText = wx.StaticText(self.panel, label="A session is underway.\nPlease finish your session before starting a new one.")
#		self.waitingText.SetFont(font)
#		self.grid.Add(self.waitingText, pos=(3,0))  -- Doesn't seem to respond to grid placement

	def OnChooseLanguage(self, event):
		print (event.GetString())
		### This section is not working properly yet
		chosenLanguage = "eng"  # need to change to chosenLanguage = event.GetString()
		with sqlite3.connect(datafile) as data:
			cur = data.cursor()  # this is now done for a second time. Will this produce bugs?
		cur.execute("SELECT contrast FROM samples WHERE language = ?", (chosenLanguage,))
		contrasts = sorted(set(cur))
		print (contrasts)
		contrastOptions = [x[0] for x in contrasts] # produces a list of strings from a list of tuples - not thoroughly tested yet
		contrastOptions.insert(0, "-")
		print (contrastOptions)
		# This works, but the preexisting chooseContrast needs to be removed (from the grid) to allow the new one to enter the grid
		self.chooseContrast = wx.ComboBox(self, size=(95,-1), choices=contrastOptions, style=wx.CB_READONLY)
		self.grid.Add(self.chooseContrast, pos=(3,2))
		### Not working yet, work in progress

	def OnChooseContrast(self, event):
		print (event.GetString())
		


class MainWindow(wx.Frame):
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
		self.Bind(wx.EVT_MENU, self.OnHelp, menuHelp)
		self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
		self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
	

	def OnFile(self, event):
		secondWindow = filewindow.FileWindow(None, "File Submission")
		secondWindow.Show()
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