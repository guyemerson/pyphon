import sqlite3, os

datafile = '..\\data\\data.db'
with sqlite3.connect(datafile) as data:
	cur = data.cursor()
	# Open GUI for importing sound files	
	# Let user choose language and contrast
	chosen_language = 'eng'
	chosen_contrast = 'ee-i'
	# Let user choose a set of options, then files for each option
	files = {'sick':[], 'seek':[]}
	options = '|'.join(files)
	# Let user choose files for each option
	choice = 'sick'
	filename = '..\\data\\sick.wav'
	speaker = 'me'
	if os.path.exists(filename):
		files[choice].append((filename,speaker))
	else:
		raise Exception('file not found')
	# Another choice as above...
	choice = 'seek'
	filename = '..\\data\\seek.wav'
	speaker = 'me'
	if os.path.exists(filename):
		files[choice].append((filename,speaker))
	else:
		raise Exception('file not found')
	# Let user decide to finish
	if min([len(x) for x in files.values()]) == 0:
		raise Exception('each option must have at least one file')
	for answer in files:
		for filename, speaker in files[answer]: # We could optimise this by making a list of new tuples
			cur.execute('INSERT INTO samples VALUES (?,?,?,?,?,?)', (filename, speaker, chosen_language, chosen_contrast, options, answer))

# It could to belpful to:
# allow adding a directory full of files
# include existing languages, contrasts, and speakers in a dropdown menu
# give the option of copying files into the ..\data directory