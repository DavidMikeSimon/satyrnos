from OpenGL.GL import *

import colors, drive

class DLightField(drive.Drive):
	"""A drive that keeps track of a bunch of Lights, then flattens them and
	draws them each frame.

	Each Light is given to the field in terms of absolute game world
	coordinates. They're kept seperated, in a list, until it comes time to
	draw them. Then, DLightField creates an image based on the lighting effects,
	draws the image to the screen, then clears the screen. By flattening and
	then drawing, rather than just drawing each effect, we can do things like
	start out with darkness and add light and get a reasonable-looking result.

	You can provide DLightField with a background Light, which will be re-added
	to the list of Lights after each time it is cleared.

	The position of the GameObj that the light field is attached to is irrelevant.
	By convention, the main DLightField should be the only drive of the only
	game object of layer #6. We have this as part of the Drive hierarchy because
	it can also be used for other "lights" which, since they're part of the lower
	layers, have visibility that's determined by the main light.
	
	Data attributes:
	lights -- A list of Lights, which are applied in order (latter ones over earlier ones)
	"""
	
	def __init__(self):
		super(DLightField, self).__init__(drawing = true)
		self.lights = []
	
	def _draw(self, obj):
		foreach light in lights:
			light.draw()


class BgLight:
	"""A Light that affects the entire screen equally.

	Data attributes:
	alpha -- A floating point value defining the alpha
	col -- A 3-tuple defining the color
	"""

	def __init__(self, alpha, color = colors.black):
		
