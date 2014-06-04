import wx, os, sqlite3
import wxGUI

SRC_DIR = os.getcwd()
DATA_DIR = os.path.join(os.path.split(SRC_DIR)[0], 'data')


def filepath(text):
	"""	If text contains no slashes, add the default data directory	"""
	directory, filename = os.path.split(text)
	if directory == "":
		return os.path.join(DATA_DIR, filename)
	else:
		return text


if __name__ == "__main__":
	# Read settings from file, or else create settings file 
	settingsFile = os.path.join(DATA_DIR, '.pyphonsettings')
	settings = dict()
	if os.path.exists(settingsFile):
		with open(settingsFile, 'r') as fin:
			for line in fin:
				key, value = line.strip().split('\t')
				if value == "TRUE":
					value = True
				elif value == "FALSE":
					value = False
				settings[key] = value
	else:
		settings = {'album':'default_album.db', 'user':'default_user.db', 'copy':True}
		with open(settingsFile, 'w') as fout:
			for key, value in settings.items():
				if value == True:
					value = "TRUE"
				elif value == False:
					value = "FALSE"
				fout.write("{}\t{}\n".format(key, value))
	
	albumFile = filepath(settings['album'])
	userFile  = filepath(settings['user'])
	
	# Open database files, if they exist, or else create empty databases
	# Currently, userFile is not implemented
	if os.path.exists(albumFile):
		with sqlite3.connect(albumFile) as data:
			cursor = data.cursor()
			cursor.execute("PRAGMA foreign_keys = ON")
	
	else:
		with sqlite3.connect(albumFile) as data:
			cursor = data.cursor()
			cursor.execute("PRAGMA foreign_keys = ON")
			
			cursor.execute('''CREATE TABLE language_set
				(language TEXT PRIMARY KEY)''')
			
			cursor.execute('''CREATE TABLE contrast_set
				(language TEXT,
				 contrast TEXT,
				 FOREIGN KEY (language) REFERENCES language_set(language)
				 	ON DELETE CASCADE ON UPDATE CASCADE,
				 PRIMARY KEY (language, contrast))''')
			
			cursor.execute('''CREATE TABLE speaker_set
				(language TEXT,
				 speaker TEXT,
				 FOREIGN KEY (language) REFERENCES language_set(language)
				 	ON DELETE CASCADE ON UPDATE CASCADE,
				 PRIMARY KEY (language, speaker))''')
			
			cursor.execute('''CREATE TABLE recordings
				(file TEXT PRIMARY KEY,
				 speaker TEXT,
				 language TEXT,
				 answer TEXT NOT NULL,
				 FOREIGN KEY (language, speaker) REFERENCES speaker_set(language, speaker)
				 	ON DELETE CASCADE ON UPDATE CASCADE)''')
			
			cursor.execute('''CREATE TABLE minimal_pairs
				(language TEXT,
				 contrast TEXT,
				 item_1 TEXT,
				 item_2 TEXT,
				 FOREIGN KEY (language, contrast) REFERENCES contrast_set(language, contrast)
				 	ON DELETE CASCADE ON UPDATE CASCADE,
				 PRIMARY KEY (language, contrast, item_1, item_2))''')
	
	# Open the main window
	app = wx.App(False)
	frame = wxGUI.MainWindow(None, title="High Variability Phonetic Training software", cursor=cursor)
	frame.Show()
	app.MainLoop()
	
	# Save database changes after exiting
	data.commit()