from OpenGL.GL import *
from OpenGL.GLUT import *

import app, drive, colors

class DDebugText(drive.Drive):
	"""Drive that draws a piece of debugging text in a fixed font.
	
	If the lower left corner of the text is off-screen, then none of the text will be drawn (it seems).
	
	Data attributes:
	text -- The text to draw.
	color -- The color to draw it in.
	"""
	
	def __init__(self, text, color = colors.black):
		"""Creates a DDebugText with the given text."""
		super(DDebugText, self).__init__(drawing = True)
		self.text = text
		self.color = color
	
	def __str__(self):
		return super(DDebugText, self).__str__() + "[" + self.text + "]"
	
	def _draw(self, obj):
		glColor3fv(self.color)
		glRasterPos2f(-((len(self.text)*9)/2.0)/app.pixm + 0.005, 5/app.pixm) #This isn't strictly centered, but looks better
		for c in (self.text):
			glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(c))
