import pygame
import os
from OpenGL.GL import *
from OpenGL.GLU import *

import app

class Texture(object):
	"""An OpenGL 2D texture.

	If app.maxfps is None (signifying that app.disp_init() was never called), then Texture objects are empty.
	
	Data attributes:
	glname -- The OpenGL texture name.
	size -- The size of the texture in pixels.
	"""
	
	cache = {} #Key: filename, value: Texture instance

	def __new__(cls, filename):
		"""Creates a Texture from an image file, using pre-cached version if it exists."""
		if (app.maxfps):
			if (Texture.cache.has_key(filename)):
				return Texture.cache[filename]
			else:
				obj = object.__new__(cls)
				Texture.cache[filename] = obj
				obj.glname = glGenTextures(1)
				fullpath = os.path.join('imgs', filename)
				img = pygame.image.load(fullpath)
				obj.size = img.get_size()
				texData = pygame.image.tostring(img, "RGBA", 1)
				glBindTexture(GL_TEXTURE_2D, obj.glname)
				glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img.get_width(), img.get_height(), 0, GL_RGBA, GL_UNSIGNED_BYTE, texData)
				glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
				glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
				return obj
		else:
			return object.__new__(cls)


def unload_all():
	"""Unloads all resources.
	
	Invalidates all instances of any of the classes in this module."""
	glDeleteTextures(map(lambda x: x.glname, Texture.cache.values()))
	Texture.cache = {}
