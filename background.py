import math
from OpenGL.GL import *

import app, colors, resman, util, drive
from geometry import *

class DBackground(drive.Drive):
	"""Drive that draws a repeating background image.
	
	This can create the appearance of parallax by accepting nudges from camera position.
	You can also offset the tiling manually to create effects like the landscape moving outside a train.

	Data attributes:
	tex -- A resman.Texture instance to use as the tile.
	size -- In meters, the size of the region centered at the object's position over which to tile the image.
	tilesize -- The size of one tile in meters.
	parallax -- Point with offset of amount to parallax-nudge in each axis (in meters per meters of camera movement).
	clamp -- 2-tuple of booleans, clamps the respective axis with GL instead of repeating.
	offset -- Like parallax, but simply adds the value in meters directly; camera is not involved.
	"""
	
	def __init__(self, imgfile, size, tilesize, parallax = Point(), clamp = (False, False), offset = Point()):
		"""Creates an DBackground from the given image file. Size given is in meters."""
		super(DBackground, self).__init__(True, False)
		self.tex = resman.Texture(imgfile)
		self.size = size
		self.tilesize = tilesize
		self.parallax = parallax
		self.offset = offset
		self.clamp = clamp
	
	def _draw(self, obj):
		#For correctly sizing the tile within the polygon.
		#Since the operation only involves Sizes, we end up with a Size at the end.
		#However, we can do arithmetic between that and a Point.
		#So we still treat this as an offset, though Size isn't really for that.
		texoffset = (self.size/self.tilesize - 1)/2
		
		#For applying parallax
		paraoffset = (self.parallax*(app.ui.camera-obj.pos)-self.offset)/self.tilesize
		
		#In OpenGL, y-axis is flipped
		paraoffset[1] = -paraoffset[1]
		
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
		
		texbottomleft = Point(0 - texoffset[0], 0 - texoffset[1])
		texbottomright = Point(1 + texoffset[0], 0 - texoffset[1])
		textopleft = Point(0 - texoffset[0], 1 + texoffset[1])
		textopright = Point(1 + texoffset[0], 1 + texoffset[1])
		
		glBegin(GL_QUADS)
		glTexCoord2fv(textopleft + paraoffset)
		glVertex2fv(self.size.tl())
		glTexCoord2fv(textopright + paraoffset)
		glVertex2fv(self.size.tr())
		glTexCoord2fv(texbottomright + paraoffset)
		glVertex2fv(self.size.br())
		glTexCoord2fv(texbottomleft + paraoffset)
		glVertex2fv(self.size.bl())
		glEnd()
		glDisable(GL_TEXTURE_2D)