from __future__ import division

from OpenGL.GL import *
import math

import app, util, drive, colors, resman
from geometry import *

class DImage(drive.Drive):
	"""Drive that draws a static image.

	Data attributes:
	tex -- A resman.Texture instance to display.
	size -- The size of the image in meters.
	"""
	
	def __init__(self, imgfile, size, offset = None, rot_offset = 0):
		"""Creates a DImage from the given image file. Size given is in meters."""
		super(DImage, self).__init__(drawing = True, offset = offset, rot_offset = rot_offset)
		self.tex = resman.Texture(imgfile)
		self.size = size
	
	def __str__(self):
		return super(DImage, self).__str__() + "(" + self.tex.filename + ")"
	
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
	clamp -- 2-tuple of booleans, True causes GL to clamp respective axis instead of repeating.
	tileoffset -- Moves the tiled pattern around within the drawing box.
	"""
	
	def __init__(self, imgfile, size, tilesize, clamp = None, tileoffset = None, offset = None, rot_offset = 0):
		"""Creates an DTiledImage from the given image file. Size given is in meters."""
		super(DTiledImage, self).__init__(drawing = True, offset = offset, rot_offset = rot_offset)
		self.tex = resman.Texture(imgfile)
		self.size = size
		self.tilesize = tilesize
		
		if clamp == None: self.clamp = (False, False)
		else: self.clamp = clamp
		
		if tileoffset == None: self.tileoffset = Point()
		else: self.tileoffset = tileoffset
	
	def __str__(self):
		return super(DTiledImage, self).__str__() + "(" + self.tex.filename + ")"
	
	def _draw(self, obj):
		#For correctly sizing the tile within the boundaries.
		#Since the operation only involves Sizes, we end up with a Size at the end.
		#However, we can do arithmetic between that and a Point.
		#So we still treat this as an offset, though Size isn't really for that.
		texoffset = (self.size/self.tilesize - 1)/2
		
		#Convert to units that are tile-size, rather than meters. Negative for translation.
		gl_tile_offset = (-self.tileoffset)/self.tilesize
		
		#In OpenGL, y-axis is flipped
		gl_tile_offset[1] = -gl_tile_offset[1]
		
		glEnable(GL_TEXTURE_2D)
		glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
		glBindTexture(GL_TEXTURE_2D, self.tex.glname)
		
		#0x812F is GL_CLAMP_TO_EDGE, which seems to be missing from PyOpenGL
		
		if self.clamp[0]:
			glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, 0x812F)
		else:
			glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
		
		if self.clamp[1]:
			glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, 0x812F)
		else:
			glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
		
		texbottomleft = Point(0 - texoffset[0], 0 - texoffset[1])
		texbottomright = Point(1 + texoffset[0], 0 - texoffset[1])
		textopleft = Point(0 - texoffset[0], 1 + texoffset[1])
		textopright = Point(1 + texoffset[0], 1 + texoffset[1])
		
		glBegin(GL_QUADS)
		glTexCoord2fv(textopleft + gl_tile_offset)
		glVertex2fv(self.size.tl())
		glTexCoord2fv(textopright + gl_tile_offset)
		glVertex2fv(self.size.tr())
		glTexCoord2fv(texbottomright + gl_tile_offset)
		glVertex2fv(self.size.br())
		glTexCoord2fv(texbottomleft + gl_tile_offset)
		glVertex2fv(self.size.bl())
		glEnd()
		glDisable(GL_TEXTURE_2D)


class DWireBlock(drive.Drive):
	"""Drive that draws a wire-frame block (borders only).
	
	Data attributes:
	color -- The color to draw the lines in.
	size -- A 2-tuple with the width and height of the block in meters
	"""
	
	def __init__(self, color = None, size = None, offset = None, rot_offset = 0):
		"""Creates a DWireBlock. Size is in meters."""
		super(DWireBlock, self).__init__(drawing = True, offset = offset, rot_offset = rot_offset)

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
		(topright, bottomright)):
			glVertex2fv(pair[0])
			glVertex2fv(pair[1])
		glEnd()


class DBlock(drive.Drive):
	"""Drive that draws a solid-colored block.
	
	Data attributes:
	color -- The color to draw the block in.
	size -- A 2-tuple with the width and height of the block in meters
	"""
	
	def __init__(self, color = None, size = None, offset = None, rot_offset = 0):
		"""Creates a DBlock. Given position and size are in meters."""
		super(DBlock, self).__init__(drawing = True, offset = offset, rot_offset = rot_offset)
		
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

class DCircle(drive.Drive):
	"""Drive that draws either the outline of a circle or a filled-in circle.

	Data attributes:
	color -- The color to draw the circle in.
	radius -- How big the circle is.
	filled -- If true, then the circle is filled
	segs -- How many line segments to use to approximate the circle
	"""

	def __init__(self, radius = 0.0, color = None, filled = False, segs = 50, offset = None):
		"""Creates a DCircle."""
		super(DCircle, self).__init__(drawing = True, offset = offset)

		if color == None: self.color = colors.blue
		else: self.color = color
		
		self.radius = radius
		self.filled = filled
		self.segs = segs
	
	def _draw(self, obj):
		glColor3fv(self.color)
		
		if self.filled:
			glBegin(GL_POLYGON)
		else:
			glBegin(GL_LINE_LOOP)
		
		for x in range(0, self.segs):
			rads = (x/self.segs)*2*math.pi
			glVertex2f(math.cos(rads)*self.radius, math.sin(rads)*self.radius)
		
		glEnd()

class DPoly(drive.Drive):
	"""Drive that draws either a closed polygon or its outline.

	Data attributes:
	color -- The color to draw the polygon in.
	vertices -- A list of Points.
	filled -- If true, then the polygon is filled
	"""

	def __init__(self, vertices, color = None, filled = False, offset = None, rot_offset = 0):
		"""Creates a DPoly.
		
		The vertices list is not copied."""
		super(DPoly, self).__init__(drawing = True, offset = offset, rot_offset = rot_offset)
		
		if color == None: self.color = colors.red
		else: self.color = color
		
		self.filled = filled
		self.vertices = vertices
	
	def _draw(self, obj):
		glColor3fv(self.color)
		
		if self.filled:
			glBegin(GL_POLYGON)
		else:
			glBegin(GL_LINE_LOOP)

		for p in self.vertices:
			glVertex2fv(p)

		glEnd()

class DPoints(drive.Drive):
	"""Drive that draws a bunch of points as dots

	Data attributes:
	color -- The color to draw the dots with.
	points -- A list of Points.
	"""

	def __init__(self, points, color = None, offset = None, rot_offset = 0):
		"""Creates a DPoints.
		
		The points list is not copied."""
		super(DPoints, self).__init__(drawing = True, offset = offset, rot_offset = rot_offset)
		
		if color == None: self.color = colors.green
		else: self.color = color
		
		self.points = points
	
	def _draw(self, obj):
		glColor3fv(self.color)
		
		glBegin(GL_POINTS)
		for p in self.points:
			glVertex2fv(p)
		glEnd()
