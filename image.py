from OpenGL.GL import *

import app, util, drive, colors, resman
from geometry import *

class DImage(drive.Drive):
	"""Drive that draws a static image.

	Data attributes:
	tex -- A resman.Texture instance to display.
	size -- The size of the image in meters.
	"""
	
	def __init__(self, imgfile, size):
		"""Creates a DImage from the given image file. Size given is in meters."""
		super(DImage, self).__init__(True, False)
		self.tex = resman.Texture(imgfile)
		self.size = size
		
	def _draw(self, obj):
		glEnable(GL_TEXTURE_2D)
		glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
		glBindTexture(GL_TEXTURE_2D, self.tex.glname)
		glBegin(GL_QUADS)
		glTexCoord2f(0.0, 1.0)
		glVertex2fv(self.size.tl())
		glTexCoord2f(1.0, 1.0)
		glVertex2fv(self.size.tr())
		glTexCoord2f(1.0, 0.0)
		glVertex2fv(self.size.br())
		glTexCoord2f(0.0, 0.0)
		glVertex2fv(self.size.bl())
		glEnd()
		glDisable(GL_TEXTURE_2D)


class DWireBlock(drive.Drive):
	"""Drive that draws a wire-frame block (borders and diagonals).
	
	Data attributes:
	color -- The color to draw the lines in.
	size -- A 2-tuple with the width and height of the block in meters
	"""
	
	def __init__(self, color = colors.blue, size = (1.0, 1.0)):
		"""Creates a DWireBlock. Size is in meters."""
		super(DWireBlock, self).__init__(True, False)
		self.color = color
		self.size = size
		
	def _draw(self, obj):
		topleft = self.size.tl()
		topright = self.size.tr()
		bottomleft = self.size.bl()
		bottomright = self.size.br()
		glColor3fv(self.color)
		glBegin(GL_LINES)
		for pair in (
		(topleft, topright),
		(bottomleft, bottomright),
		(topleft, bottomleft),
		(topright, bottomright),
		(topleft, bottomright),
		(topright, bottomleft)):
			glVertex2fv(pair[0])
			glVertex2fv(pair[1])
		glEnd()


class DBlock(drive.Drive):
	"""Drive that draws a solid-colored block.
	
	Data attributes:
	color -- The color to draw the block in.
	size -- A 2-tuple with the width and height of the block in meters
	"""
	
	def __init__(self, color = colors.blue, size = (1.0, 1.0)):
		"""Creates an DBlock. Given position and size are in meters."""
		super(DBlock, self).__init__(True, False)
		self.color = color
		self.size = size
		
	def _draw(self, obj):
		glColor3fv(self.color)
		glBegin(GL_QUADS)
		glVertex2fv(self.size.tl())
		glVertex2fv(self.size.tr())
		glVertex2fv(self.size.br())
		glVertex2fv(self.size.bl())
		glEnd()