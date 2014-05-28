import sqlite3, wx, os
# import winsound  -- doesn't exist on Mac

cwd = os.getcwd()
datadir = os.path.join(os.path.split(cwd)[0], 'data')
datafile = os.path.join(datadir, 'data.db')

with open(datafile,'wb') as f:
	pass  # Wipe file before starting

with sqlite3.connect(datafile) as data:
	cur = data.cursor()
	cur.execute('CREATE TABLE samples (file text, speaker text, language text, contrast text, options text, answer text)')
	cur.execute('CREATE VIEW contrasts AS SELECT language, contrast FROM samples')
	
	language = 'British English'
	contrast = 'th-s'
	speaker = 'me'
	
	words = [('mouth', 'mouse'), ('thing', 'sing'), ('thick', 'sick')]
	
	for pair in words:
		a,b = pair
		cur.execute("INSERT INTO samples VALUES (?,?,?,?,?,?)", (os.path.join(datadir, a + '1.wav'), speaker, language, contrast, '|'.join(pair), a))
		cur.execute("INSERT INTO samples VALUES (?,?,?,?,?,?)", (os.path.join(datadir, b + '1.wav'), speaker, language, contrast, '|'.join(pair), b))
	
	cur.execute("SELECT * FROM samples") # maybe we don't have to play the sounds and we can delete the playing, only having the printing?
	# especially when we get a very large number of sounds, then your computer will play tens or hundreds of words at you without stopping. Annoying.
	for x in cur:
		print(x)
		#winsound.PlaySound(x[0], winsound.SND_FILENAME)  -- doesn't work on Mac
		#wx.Sound(x[0]).Play()
		
#Traceback (most recent call last):
#  File "<stdin>", line 1, in <module>
#  File "setup.py", line 31, in <module>
#    wx.Sound(x[0]).Play()
#  File "/usr/local/lib/wxPython-2.9.4.0/lib/python2.7/site-packages/wx-2.9.4-osx_cocoa/wx/_misc.py", line 2442, in __init__
#    _misc_.Sound_swiginit(self,_misc_.new_Sound(*args, **kwargs))
#wx._core.PyNoAppError: The wx.App object must be created first!