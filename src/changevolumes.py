import pydub

# change directory if necessary

def changeMyVolumes(myList, prefix, decibels)
for filename in myList:
	if filename[:len(prefix)] == prefix:
		song = pydub.AudioSegment.from_wav(filename)
		song += decibels
		song.export(filename, format="wav")