import app, util, drive, colors, resman

from OpenGL.GL import *

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
		halfsize = util.tupm(self.size, 0.5)
		topleft = (-halfsize[0], -halfsize[1])
		topright = (halfsize[0], -halfsize[1])
		bottomleft = (-halfsize[0], halfsize[1])
		bottomright = (halfsize[0], halfsize[1])
		
		glEnable(GL_TEXTURE_2D)
		glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
		glBindTexture(GL_TEXTURE_2D, self.tex.glname)
		glBegin(GL_QUADS)
		glTexCoord2f(0.0, 1.0)
		glVertex2fv(topleft)
		glTexCoord2f(1.0, 1.0)
		glVertex2fv(topright)
		glTexCoord2f(1.0, 0.0)
		glVertex2fv(bottomright)
		glTexCoord2f(0.0, 0.0)
		glVertex2fv(bottomleft)
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
		halfsize = util.tupm(self.size, 0.5)
		topleft = (-halfsize[0], -halfsize[1])
		topright = (halfsize[0], -halfsize[1])
		bottomleft = (-halfsize[0], halfsize[1])
		bottomright = (halfsize[0], halfsize[1])
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
		halfsize = util.tupm(self.size, 0.5)
		topleft = (-halfsize[0], -halfsize[1])
		topright = (halfsize[0], -halfsize[1])
		bottomleft = (-halfsize[0], halfsize[1])
		bottomright = (halfsize[0], halfsize[1])
		glColor3fv(self.color)
		glBegin(GL_QUADS)
		glVertex2fv(topleft)
		glVertex2fv(topright)
		glVertex2fv(bottomright)
		glVertex2fv(bottomleft)
		glEnd()