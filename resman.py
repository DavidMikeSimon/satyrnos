import pygame
import os
from OpenGL.GL import *
from OpenGL.GLU import *

import app
from geometry import *

class Texture(object):
	"""An OpenGL 2D texture.

	Data attributes:
	filename -- The filename that the texture was loaded from, or an empty string
	glname -- The OpenGL texture name.
	size -- The dimensions of the texture as a Size.
	surf -- The PyGame surface.
	"""
	
	cache = {} #Key: filename, value: Texture instance

	def __new__(cls, filename):
		"""Creates a Texture from an image file, using pre-cached version if it exists."""
		
		if (Texture.cache.has_key(filename)):
			return Texture.cache[filename]
		else:
			obj = object.__new__(cls)
			obj.filename = filename
			Texture.cache[filename] = obj
			obj.glname = glGenTextures(1)
			fullpath = os.path.join('imgs', filename)
			surf = pygame.image.load(fullpath)
			obj.surf = surf
			obj.size = Size(surf.get_width(), surf.get_height())
			texData = pygame.image.tostring(surf, "RGBA", 1)
			glBindTexture(GL_TEXTURE_2D, obj.glname)
			glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, surf.get_width(), surf.get_height(), 0, GL_RGBA, GL_UNSIGNED_BYTE, texData)
			glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
			glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
			return obj

def unload_all():
	"""Unloads all resources.
	
	Invalidates all instances of any of the classes in this module."""
	if (len(Texture.cache) > 0):
		glDeleteTextures([ x.glname for x in Texture.cache.values() ])
		Texture.cache = {}
