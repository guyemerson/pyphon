import sqlite3, os

cwd = os.getcwd()
dataDir = os.path.join(os.path.split(cwd)[0], 'data')
datafile = os.path.join(dataDir, 'data.db')

with open(datafile,'wb') as f:
	pass  # Wipe file before starting

with sqlite3.connect(datafile) as data:
	cur = data.cursor()
	cur.execute('CREATE TABLE samples (file text, speaker text, language text, contrast text, options text, answer text)')
	cur.execute('CREATE VIEW contrast_set AS SELECT DISTINCT language, contrast FROM samples')
	
	language = 'British English'
	contrast = 'th-s'
	speaker = 'Guy'
	
	words = [('mouth', 'mouse'), ('thing', 'sing'), ('thick', 'sick')]
	
	for pair in words:
		a,b = pair
		cur.execute("INSERT INTO samples VALUES (?,?,?,?,?,?)", (a + '1.wav', speaker, language, contrast, '|'.join(pair), a))
		cur.execute("INSERT INTO samples VALUES (?,?,?,?,?,?)", (b + '1.wav', speaker, language, contrast, '|'.join(pair), b))
	
	print("Entries:")
	cur.execute("SELECT * FROM samples")
	for x in cur:
		print(x)
	
	print("Contrasts:")
	cur.execute("SELECT DISTINCT * FROM contrast_set")
	for x in cur:
		print(x)