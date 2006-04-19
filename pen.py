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
	
	This pen appears to make the background move by translating a bit more depending on camera position.

	Data attributes:
	tex: A resman.Texture instance to display.
	size: The size of the image in meters (as though bg was at same z-distance as regular objects).
	repx: If this is true, then the image is repeated along the x axis.
	repy: If this is true, then the image is repeated along the y axis.
	coefx: Multiply camera pos by this, then translate x in that direction before drawing.
	coefy: Just like coefx, only for y translation.
	"""
	
	def __init__(self, imgfile, size, repx = True, repy = True, coefx = 0.0, coefy = 0.0):
		"""Creates an PBackground from the given image file. Size given is in meters.
		"""
		self.tex = resman.Texture(imgfile)
		self.size = size
		self.repx = repx
		self.repy = repy
		self.coefx = coefx
		self.coefy = coefy
	
	def draw(self, obj):
		halfsize = util.tupm(self.size, 0.5)
		scrhalfsize = (2, 1.5)

		offset = [0, 0] #This will later be added to each of the corner position coordinates
		repoffset = [0, 0] #Rectangle corners will be moved this much farther away from pos's center
		texoffset = [0, 0] #Distance to go from edge of original texture box to edge of repeating texture box
		
		#Translate and enable repetition for each axis as needed.
		for axis in range(0, 2):
			if (axis == 0 and self.repx) or (axis == 1 and self.repy):
				#Make sure the texture repetition is big enough to cover the whole viewing window (4x3 meters)
				repoffset[axis] = scrhalfsize[axis]*2
				texoffset[axis] = repoffset[axis]/self.size[axis]
				
				#Besides translating for faking parallax, we also do so to fake
				# the repeat so we start from a center position inside view window.
				obj_pedge = obj.pos[axis] + halfsize[axis]
				obj_nedge = obj.pos[axis] - halfsize[axis]
				cam_pedge = app.camera[axis] + scrhalfsize[axis]
				cam_nedge = app.camera[axis] - scrhalfsize[axis]
				if obj_pedge < cam_nedge:
					#Need to scooch right/down so that part of the image appears onscreen.
					#Scooch in chunks equal to the image's size.
					offset[axis] += math.ceil((cam_nedge - obj_pedge)/self.size[axis])*self.size[axis]
				if obj_nedge > cam_pedge:
					#Need to scooch left/up.
					offset[axis] -= math.ceil((obj_nedge - cam_pedge)/self.size[axis])*self.size[axis]
		
		topleft = (-halfsize[0] + offset[0] - repoffset[0], -halfsize[1] + offset[1] - repoffset[1])
		topright = (halfsize[0] + offset[0] + repoffset[0], -halfsize[1] + offset[1] - repoffset[1])
		bottomleft = (-halfsize[0] + offset[0] - repoffset[0], halfsize[1] + offset[1] + repoffset[1])
		bottomright = (halfsize[0] + offset[0] + repoffset[0], halfsize[1] + offset[1] + repoffset[1])
		
		#Texture coordinates are still mathematically oriented (up-right is +/+, not down-right)
		texbottomleft = (0 - texoffset[0], 0 - texoffset[1])
		texbottomright = (1 + texoffset[0], 0 - texoffset[1])
		textopleft = (0 - texoffset[0], 1 + texoffset[1])
		textopright = (1 + texoffset[0], 1 + texoffset[1])
		
		glEnable(GL_TEXTURE_2D)
		glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
		glBindTexture(GL_TEXTURE_2D, self.tex.glname)
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
