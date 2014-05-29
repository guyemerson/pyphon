#import wx
import pylab

def piechart():
	# make a square figure and axes
	pylab.figure(1, figsize=(6,6))
	ax = pylab.axes([0.1, 0.1, 0.8, 0.8]) # do we need this?

	# The slices will be ordered and plotted counter-clockwise.
	labels = "Correct", "Incorrect"
	fracs = [15, 30]
	explode=(0, 0)

	pylab.pie(fracs, explode=explode, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
    # The default startangle is 0, which would start the Frogs slice on the x-axis.
    # With startangle=90, everything is rotated counter-clockwise by 90 degrees, so the plotting starts on the positive y-axis.

	pylab.title("Performance", bbox={'facecolor':'0.8', 'pad':5})

	pylab.show()