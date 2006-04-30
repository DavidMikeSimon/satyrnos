import app, colors, resman, util, drive

import math
from OpenGL.GL import *

class DBackground(drive.Drive):
	"""Drive that draws a repeating background image.
	
	This can create the appearance of parallax by accepting nudges from camera position.
	You can also offset the tiling manually to create effects like the landscape moving outside a train.

	Data attributes:
	tex -- A resman.Texture instance to use as the tile.
	size -- In meters, the size of the region centered at the object's position over which to tile the image.
	tilesize -- The size of one tile in meters.
	parallax -- 2-tuple of amount to parallax-nudge in each axis (in meters per meters of camera movement).
	clamp -- 2-tuple of booleans, clamps the respective axis with GL instead of repeating.
	offset -- Like parallax, but simply adds the value in meters directly; camera is not involved.
	"""
	
	def __init__(self, imgfile, size, tilesize, parallax = (0.0, 0.0), clamp = (False, False), offset = (0.0, 0.0)):
		"""Creates an DBackground from the given image file. Size given is in meters."""
		super(DBackground, self).__init__(True, False)
		self.tex = resman.Texture(imgfile)
		self.size = size
		self.tilesize = tilesize
		self.parallax = parallax
		self.offset = offset
		self.clamp = clamp
	
	def _draw(self, obj):
		topleft = (-self.size[0]/2, -self.size[1]/2)
		topright = (self.size[0]/2, -self.size[1]/2)
		bottomleft = (-self.size[0]/2, self.size[1]/2)
		bottomright = (self.size[0]/2, self.size[1]/2)
		
		texoffset = [0, 0] #For correctly sizing the tile within the polygon
		for axis in range(0, 2):
			texoffset[axis] = (self.size[axis]/self.tilesize[axis] - 1)/2
		
		paraoffset = [0, 0] #For applying parallax
		for axis in range(0, 2):
			paraoffset[axis] = (self.parallax[axis]*(app.ui.camera[axis]-obj.pos[axis]) + self.offset[axis])/self.tilesize[axis]
		
		#Texture coordinates are still mathematically oriented (up-right is +/+, not down-right)
		texbottomleft = (0 - texoffset[0] + paraoffset[0], 0 - texoffset[1] - paraoffset[1])
		texbottomright = (1 + texoffset[0] + paraoffset[0], 0 - texoffset[1] - paraoffset[1])
		textopleft = (0 - texoffset[0] + paraoffset[0], 1 + texoffset[1] - paraoffset[1])
		textopright = (1 + texoffset[0] + paraoffset[0], 1 + texoffset[1] - paraoffset[1])
		
		glEnable(GL_TEXTURE_2D)
		glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
		glBindTexture(GL_TEXTURE_2D, self.tex.glname)
		
		#0x812F is GL_CLAMP_TO_EDGE, which seems to be missing from PyOpenGL
		
		if (self.clamp[0]):
			glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, 0x812F)
		else:
			glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
		
		if (self.clamp[1]):
			glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, 0x812F)
		else:
			glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
		
		glBegin(GL_QUADS)
		glTexCoord2fv(textopleft)
		glVertex2fv(topleft)
		glTexCoord2fv(textopright)
		glVertex2fv(topright)
		glTexCoord2fv(texbottomright)
		glVertex2fv(bottomright)
		glTexCoord2fv(texbottomleft)
		glVertex2fv(bottomleft)
		glEnd()
		glDisable(GL_TEXTURE_2D)