from OpenGL.GL import *
from __future__ import division

import app, colors, drive, interface

def _vi_color(vis_pixel):
	"""Given a 4-tuple of light color and vis index, creates
	an overlay color."""
	
	other_col = colors.black
	x = vis_pixel[3]
	if (x < 1.0):
		x = 1.0 - x
	else:
		other_col = colors.white
		x -= 1.0
	
	r = 1.0 - x
	
	return (
		other_col[0]*x + vis_pixel[0]*r,
		other_col[1]*x + vis_pixel[1]*r,
		other_col[2]*x + vis_pixel[2]*r,
		pow(x, 2))

class DLightField(drive.Drive):
	"""A drive that contains a bunch of Lights, then each frame draws them and deletes
	them.
	
	GameObjs that wish to affect lighting use their predraw or draw calls to add some
	Light objects (such as the ones in this module) to the DLightField in layer 6.
	When DLightField's draw is called, it creates an overlay based on those lights,
	draws it, then clears the list of lights.
	
	Each Light is given to the field in terms of absolute game world
	coordinates. They're kept seperated, in a list, until it comes time to
	draw them. Then, DLightField creates an image based on the lighting effects,
	draws the image to the screen, then clears the screen. By flattening and
	then drawing, rather than just drawing each light, we can start out with
	darkness, add light, and thereby reveal objects that would normally be 
	obscured.
	
	The visibility index of a pixel is what's determined by lights. The color
	of light at each pixel is determined by averaging the color of the lights,
	weighted by the visibility index at that pixel. The final visibility index of
	a pixel is calculated by adding the visibility indices of the lights at that pixel.

	Here's what the visiblity indices imply:
	0.0 - Pixel is unlit, and solid black. Light overlay is black, alpha 1.0
	0.5 - Pixel is half-lit. Light overlay is 50% black, 50% light color, alpha 0.25 (exp scale).
	1.0 - Pixel is perfectly visible. Light overlay has alpha 0.0.
	1.5 - Pixel is half-overlit. Light overlay is 50% light color, 50% white, alpha 0.25 (exp scale).
	2.0 - Pixel is overlit. Light overlay is 100% white, alpha 1.0.

	Color blending for light follows a linear scale, while alpha blending follows an exponential scale.
	Therefore, lights attenuate their visibility index linearly, not exponentially.
	
	The position of the GameObj that the light field is attached to is irrelevant.
	By convention, the main DLightField should be the only drive of the only
	game object of layer #6. We have this as part of the Drive hierarchy because
	it can also be used for other "lights" which, since they're part of the lower
	layers, have a visibility that's determined by the main light.
	
	Data attributes:
	lights -- A list of Lights, which are applied in order (latter ones over earlier ones)
	base_vis_index -- The visibility index of areas that are unaffected by lights.
	base_vis_col -- The initial color of the visibility mask (only matters if base_vis_index > 0.0)
	"""
	
	def __init__(self, base_vis_index = 0.0, base_vis_color = colors.black):
		super(DLightField, self).__init__(drawing = True)
		self.lights = []
		self.base_vis_index = base_vis_index
		self.base_vis_color = base_vis_color
		
		self.vis_mask = []
		for x in range(0, app.ui.winsize[0]):
			self.vis_mask.append([])
			for y in range(0, app.ui.winsize[1]):
				self.vis_mask[x].append(None)
		
		#Create a visibility mask which will be affected by the lights, at the default visibility
		#This mask seems like RGBA, but the last component is a vis index, not an alpha channel
		vis_mask = self.vis_mask
		for row in vis_mask:
			for pixel in row:
				pixel = (self.base_vis_color[0], self.base_vis_color[1], self.base_vis_color[2], self.base_vis_index)
		
		#Convert the mask into an image we can then blit to OpenGL
		for row in vis_mask:
			for pixel in row:
		 		pixel = _vi_color(pixel)
		
	def _draw(self, obj):
		for light in self.lights:
			light.draw(vis_mask)
		
		glDrawPixelsf(GL_RGBA, vis_mask)
		


#class BasicLight:
#	"""A light that emits light equally in all directions with linear attenuation of the vis index.
#	
#	Data attributes:
#	"""
#	
#	def __init__(self):
#		
