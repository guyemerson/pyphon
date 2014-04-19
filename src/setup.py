import sqlite3, winsound

datafile = '..\\data\\data.db'

with open(datafile,'wb') as f:
	pass  # Wipe file before starting

with sqlite3.connect(datafile) as data:
	cur = data.cursor()
	cur.execute('CREATE TABLE samples (file text, speaker text, language text, contrast text, options text, answer text)')
	cur.execute('CREATE VIEW contrasts AS SELECT language, contrast FROM samples')
	
	language = 'eng'
	contrast = 'th-s'
	speaker = 'me'
	
	words = [('mouth', 'mouse'), ('thing', 'sing'), ('thick', 'sick')]
	
	for pair in words:
		a,b = pair
		cur.execute("INSERT INTO samples VALUES (?,?,?,?,?,?)", ('..\\data\\{}.wav'.format(a), speaker, language, contrast, '|'.join(pair), a))
		cur.execute("INSERT INTO samples VALUES (?,?,?,?,?,?)", ('..\\data\\{}.wav'.format(b), speaker, language, contrast, '|'.join(pair), b))
	
	cur.execute("SELECT * FROM samples")
	for x in cur:  #fetchall()
		print(x)
		winsound.PlaySound(x[0], winsound.SND_FILENAME)