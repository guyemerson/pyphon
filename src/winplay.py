import winsound

files = ['..\\data\\mouse.wav',
				 '..\\data\\mouth.wav',
				 '..\\data\\thing.wav',
				 '..\\data\\sing.wav']

for x in files:
	winsound.PlaySound(x, winsound.SND_FILENAME)