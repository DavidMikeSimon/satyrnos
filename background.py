import math
import copy
from OpenGL.GL import *

import app, colors, resman, util, image
from geometry import *

class DTiledBg(image.DTiledImage):
	"""Drive that draws a repeating background image with a parallax effect.
	
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
	
	def __init__(self, imgfile, size, tilesize, parallax = None, clamp = None, offset = None):
		"""Creates an DBackground from the given image file. Size given is in meters."""
		super(DTiledBg, self).__init__(imgfile, size, tilesize, clamp, offset)
		if parallax == None: self.parallax = Point()
		else: self.parallax = parallax
	
	def _draw(self, obj):
		#Apply the parallax, do the draw, then revert the DTiledImage to its original state
		old_offset = copy.copy(self.offset)
		self.offset -= self.parallax*(app.ui.camera-obj.pos)
		super(DTiledBg, self)._draw(obj)
		self.offset = old_offset
