import sqlite3, os

cwd = os.getcwd()
dataDir = os.path.join(os.path.split(cwd)[0], 'data')
datafile = os.path.join(dataDir, 'data_v3.db')

with open(datafile,'wb') as f:
	pass  # Wipe file before starting

with sqlite3.connect(datafile) as data:
	cur = data.cursor()
	
	# Define tables in the database
	cur.execute("PRAGMA foreign_keys = ON")
	
	cur.execute('''CREATE TABLE language_set
		(language TEXT PRIMARY KEY)''')
	
	cur.execute('''CREATE TABLE contrast_set
		(language TEXT,
		 contrast TEXT,
		 FOREIGN KEY (language) REFERENCES language_set(language)
		 	ON DELETE CASCADE ON UPDATE CASCADE,
		 PRIMARY KEY (language, contrast))''')
	
	cur.execute('''CREATE TABLE speaker_set
		(language TEXT,
		 speaker TEXT,
		 FOREIGN KEY (language) REFERENCES language_set(language)
		 	ON DELETE CASCADE ON UPDATE CASCADE,
		 PRIMARY KEY (language, speaker))''')
	
	cur.execute('''CREATE TABLE recordings
		(file TEXT PRIMARY KEY,
		 speaker TEXT,
		 language TEXT,
		 answer TEXT NOT NULL,
		 FOREIGN KEY (language, speaker) REFERENCES speaker_set(language, speaker)
		 	ON DELETE CASCADE ON UPDATE CASCADE)''')
	
	cur.execute('''CREATE TABLE minimal_pairs
		(language TEXT,
		 contrast TEXT,
		 item_1 TEXT,
		 item_2 TEXT,
		 FOREIGN KEY (language, contrast) REFERENCES contrast_set(language, contrast)
		 	ON DELETE CASCADE ON UPDATE CASCADE,
		 PRIMARY KEY (language, contrast, item_1, item_2))''')
	
	# Add some data
	language = 'British English'
	contrast = 'th-s'
	speaker = 'Guy'
	
	words = [('mouth', 'mouse'), ('thing', 'sing'), ('thick', 'sick')]
	
	
	cur.execute("INSERT INTO language_set VALUES (?)", (language,))
	cur.execute("INSERT INTO contrast_set VALUES (?,?)", (language, contrast))
	cur.execute("INSERT INTO speaker_set VALUES (?,?)", (language, speaker))
	
	for a,b in words:
		cur.executemany("INSERT INTO recordings VALUES (?,?,?,?)",
			[(a + '1.wav', speaker, language, a),
			 (b + '1.wav', speaker, language, b)])
		cur.execute("INSERT INTO minimal_pairs VALUES (?,?,?,?)",
			(language, contrast, a, b))
	
	# Print, to check if saved correctly
	print("Entries:")
	cur.execute("SELECT * FROM recordings")
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