import sqlite3, os, random

system = os.environ['OS']
if system == 'Windows_NT':  # We need to make sure we can play sound files on any reasonable operating system...
	import winsound
	def play(filename):
		winsound.PlaySound(filename, winsound.SND_FILENAME)
else:  # Here we would define a different function "play"
	raise Exception(system)
	#import musicplayer  # This might be a good choice?

datafile = '..\\data\\data.db'
with sqlite3.connect(datafile) as data:
	cur = data.cursor()
	# Open GUI
	cur.execute("SELECT language FROM samples")
	languages = sorted(set(cur))
	# Let the user choose a language
	print(languages)
	chosen_language = 'eng'
	cur.execute("SELECT contrast FROM samples WHERE language = ?", (chosen_language,))
	contrasts = sorted(set(cur))
	# Let the user choose a contrast
	print(contrasts)
	chosen_contrast = 'th-s'
	# Let the user choose options for the study session
	max_rep = 3
	# We might also want: preferring samples that the user hasn't heard (this requires keeping track), allowing repetition
	cur.execute("SELECT file, options, answer FROM samples WHERE language = ? AND contrast = ?", (chosen_language, chosen_contrast))
	training = list(cur)
	random.shuffle(training)
	reps = min(max_rep, len(training))
	correct = 0
	for file, option_string, answer in training[0:reps]:
		# Display each option as a button
		options = option_string.split('|')
		print(options)
		play(file)
		# Let the user choose an option, or replay the sound file
		user_choice = options[random.randint(0,1)]
		if user_choice == answer:
			print("Correct! It was: {}".format(answer))
			correct += 1
		else:
			print("The correct answer was: {}".format(answer))
	print("You answered {} out of {} questions correctly ({:.0%})".format(correct, reps, correct/reps))



# We could introduce more careful user statistics - need to think about the data structure. Two columns for each user? (#heard and #correct) To display statistics over time, we need to record either test sessions or individual answers
# We should check all the files exist when opening the database 