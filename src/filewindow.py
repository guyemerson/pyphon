import wx, os

class FileWindow(wx.Frame):
	'''
	This is the frame where files are to be viewed and potentially inputted to the program.
	At the moment it is blank.
	
	It needs to be:
	- super idiot-proof -- we don't want anyone having any "accidents" with the data!!
	- encouraging (or at least not discouraging) as regards getting stuck in and contributing, especially through ease of use and lack of intimidation
	'''
	def __init__(self, parent, title):
		wx.Frame.__init__(self, parent, title=title, style=(wx.DEFAULT_FRAME_STYLE | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX | wx.WS_EX_CONTEXTHELP), size=(500,300))
		