import sqlite3, os

cwd = os.getcwd()
dataDir = os.path.join(os.path.split(cwd)[0], 'data')
datafile = os.path.join(dataDir, 'data_v2.db')

with open(datafile,'wb') as f:
	pass  # Wipe file before starting

with sqlite3.connect(datafile) as data:
	cur = data.cursor()
	cur.execute('''CREATE TABLE samples
		(file text NOT NULL PRIMARY KEY,
		 speaker text NOT NULL,
		 language text NOT NULL,
		 answer text NOT NULL)''')
	
	cur.execute('''CREATE TABLE minimal_pairs
		(language text NOT NULL,
		 contrast text NOT NULL,
		 option_1 text NOT NULL,
		 option_2 text NOT NULL)''')
	
	cur.execute('''CREATE VIEW contrast_set
		AS SELECT DISTINCT language, contrast FROM minimal_pairs''')
	
	# Maybe we should JOIN 'samples' and 'minimal_pairs' 
	
	language = 'British English'
	contrast = 'th-s'
	speaker = 'Guy'
	
	words = [('mouth', 'mouse'), ('thing', 'sing'), ('thick', 'sick')]
	
	for a,b in words:
		cur.executemany("INSERT INTO samples VALUES (?,?,?,?)",
			[(a + '1.wav', speaker, language, a),
			 (b + '1.wav', speaker, language, b)])
		cur.execute("INSERT INTO minimal_pairs VALUES (?,?,?,?)",
			(language, contrast, a, b))
	
	
	print("Entries:")
	cur.execute("SELECT * FROM samples")
	for x in cur:
		print(x)
	
	print("\nMinimal pairs:")
	cur.execute("SELECT * FROM minimal_pairs")
	for x in cur:
		print(x)
	
	print("\nContrasts:")
	cur.execute("SELECT * FROM contrast_set")
	for x in cur:
		print(x)