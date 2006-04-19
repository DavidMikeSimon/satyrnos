import app
import colors
import resman
import util

import math
from OpenGL.GL import *

class PWireBlock:
	"""Pen that draws a wire-frame block (borders and diagonals).
	
	Data attributes:
	color: The color to draw the lines in.
	size: A 2-tuple with the width and height of the block in meters
	"""
	
	def __init__(self, color = colors.blue, size = (1.0, 1.0)):
		"""Creates a PWireBlock. Size is in meters.
		"""
		self.color = color
		self.size = size
		
	def draw(self, obj):
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


class PBlock:
	"""A pen that draws a solid-colored block.
	
	Data attributes:
	color: The color to draw the lines in.
	size: A 2-tuple with the width and height of the block in meters
	"""
	
	def __init__(self, color = colors.blue, size = (1.0, 1.0)):
		"""Creates an PBlock. Given position and size are in meters.
		"""
		self.color = color
		self.size = size
		
	def draw(self, obj):
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


class PImage:
	"""A pen that draws a static image.

	Data attributes:
	tex: A resman.Texture instance to display.
	size: The size of the image in meters.
	"""
	
	def __init__(self, imgfile, size):
		"""Creates an PImage from the given image file. Size given is in meters.
		"""
		self.tex = resman.Texture(imgfile)
		self.size = size
		
	def draw(self, obj):
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


class PBackground:
	"""Pen that draws a repeating background image.
	
	The pen can create the appearance of parallax by accepting nudges from camera position.
	You can also offset the tiling manually to create effects like the landscape moving outside a train.

	Data attributes:
	tex: A resman.Texture instance to use as the tile.
	size: In meters, the size of the region centered at the object's position over which to tile the image.
	tilesize: The size of one tile in meters.
	parallax: 2-tuple of amount to parallax-nudge in each axis (in meters per meters of camera movement).
	offset: Like parallax, but simply adds the value in meters directly; camera is not involved.
	clamp: 2-tuple of booleans, clamps the respective axis with GL instead of repeating
	"""
	
	def __init__(self, imgfile, size, tilesize, parallax = (0.0, 0.0), offset = (0.0, 0.0), clamp = (False, False)):
		"""Creates an PBackground from the given image file. Size given is in meters.
		"""
		self.tex = resman.Texture(imgfile)
		self.size = size
		self.tilesize = tilesize
		self.parallax = parallax
		self.offset = offset
		self.clamp = clamp
	
	def draw(self, obj):
		topleft = (-self.size[0]/2, -self.size[1]/2)
		topright = (self.size[0]/2, -self.size[1]/2)
		bottomleft = (-self.size[0]/2, self.size[1]/2)
		bottomright = (self.size[0]/2, self.size[1]/2)
		
		texoffset = [0, 0] #For correctly sizing the tile within the polygon
		for axis in range(0, 2):
			texoffset[axis] = (self.size[axis]/self.tilesize[axis] - 1)/2
		
		paraoffset = [0, 0] #For applying parallax
		for axis in range(0, 2):
			paraoffset[axis] = (self.parallax[axis]*app.camera[axis] + self.offset[axis])/self.tilesize[axis]
		
		#Texture coordinates are still mathematically oriented (up-right is +/+, not down-right)
		texbottomleft = (0 - texoffset[0] + paraoffset[0], 0 - texoffset[1] - paraoffset[1])
		texbottomright = (1 + texoffset[0] + paraoffset[0], 0 - texoffset[1] - paraoffset[1])
		textopleft = (0 - texoffset[0] + paraoffset[0], 1 + texoffset[1] - paraoffset[1])
		textopright = (1 + texoffset[0] + paraoffset[0], 1 + texoffset[1] - paraoffset[1])
		
		glEnable(GL_TEXTURE_2D)
		glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
		glBindTexture(GL_TEXTURE_2D, self.tex.glname)
		
		if (self.clamp[0]):
			glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
		else:
			glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
		
		if (self.clamp[1]):
			glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
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
