import sqlite3, winsound, os

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
	
	cur.execute("SELECT * FROM samples")
	for x in cur:
		print(x)
		winsound.PlaySound(x[0], winsound.SND_FILENAME)