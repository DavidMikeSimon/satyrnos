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
		super(DImage, self).__init__(drawing = True)
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

class DTiledImage(drive.Drive):
	"""Drive that draws an image tiled over an area.
	
	Data attributes:
	tex -- A resman.Texture instance to use as the tile.
	size -- In meters, the size of the region centered at the object's position over which to tile the image.
	tilesize -- The size of one tile in meters.
	clamp -- 2-tuple of booleans, clamps the respective axis with GL instead of repeating.
	offset -- Moves the tiled pattern around within the drawing box.
	"""
	
	def __init__(self, imgfile, size, tilesize, clamp = None, offset = None):
		"""Creates an DBackground from the given image file. Size given is in meters."""
		super(DTiledImage, self).__init__(drawing = True)
		self.tex = resman.Texture(imgfile)
		self.size = size
		self.tilesize = tilesize
		
		if clamp == None: self.clamp = (False, False)
		else: self.clamp = clamp
		
		if offset == None: self.offset = Point()
		else: self.offset = offset
	
	def _draw(self, obj):
		#For correctly sizing the tile within the boundaries.
		#Since the operation only involves Sizes, we end up with a Size at the end.
		#However, we can do arithmetic between that and a Point.
		#So we still treat this as an offset, though Size isn't really for that.
		texoffset = (self.size/self.tilesize - 1)/2
		
		#Convert to units that are tile-size, rather than meters. Negative for translation.
		tile_offset = (-self.offset)/self.tilesize
		
		#In OpenGL, y-axis is flipped
		tile_offset[1] = -tile_offset[1]
		
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
		glTexCoord2fv(textopleft + tile_offset)
		glVertex2fv(self.size.tl())
		glTexCoord2fv(textopright + tile_offset)
		glVertex2fv(self.size.tr())
		glTexCoord2fv(texbottomright + tile_offset)
		glVertex2fv(self.size.br())
		glTexCoord2fv(texbottomleft + tile_offset)
		glVertex2fv(self.size.bl())
		glEnd()
		glDisable(GL_TEXTURE_2D)

class DWireBlock(drive.Drive):
	"""Drive that draws a wire-frame block (borders and diagonals).
	
	Data attributes:
	color -- The color to draw the lines in.
	size -- A 2-tuple with the width and height of the block in meters
	"""
	
	def __init__(self, color = None, size = None):
		"""Creates a DWireBlock. Size is in meters."""
		super(DWireBlock, self).__init__(drawing = True)

		if color == None: self.color = colors.blue
		else: self.color = color
		
		if size == None: self.size = (1.0, 1.0)
		else: self.size = size
		
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
	
	def __init__(self, color = None, size = None):
		"""Creates an DBlock. Given position and size are in meters."""
		super(DBlock, self).__init__(drawing = True)
		
		if color == None: self.color = colors.blue
		else: self.color = color
		
		if size == None: self.size = (1.0, 1.0)
		else: self.size = size
		
	def _draw(self, obj):
		glColor3fv(self.color)
		glBegin(GL_QUADS)
		glVertex2fv(self.size.tl())
		glVertex2fv(self.size.tr())
		glVertex2fv(self.size.br())
		glVertex2fv(self.size.bl())
		glEnd()
