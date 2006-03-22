import pygame

import app, math, util

class CMagnet:
	"""A controller that creates a point of gravitational/magnetic attraction or repulsion.
	
	Data attributes:
	pow -- The amount of force applied per simstep. If negative, pulls instead of pushing.
	rad -- The radius of the effect in meters. If non-positive, unlimited radius.
	loss -- The amount of force lost per meter distance from the object.
	        This just brings 'pow' that much closer to zero depending on distance.
			  It will never allow pow to go past zero.
	gravity -- If True, then actual mass of object is ignored; act as though object had a mass of 1.
	active -- If False, then the effect is disabled.
	"""

	def __init__(self, pow, rad = 0, loss = 0, gravity = False, active = True):
		self.pow = pow
		self.rad = rad
		self.loss = loss
		self.gravity = gravity
		self.active = active
	
	def do(self, magobj):
		if not self.active:
			return
		
		#For every object excluding the actual pulling object, check if we're affecting it
		for o in app.objects:
			if o == magobj:
				continue
			
			#Ignore objects outside the ODE force system
			if o.body == None:
				continue
			
			#Ignore objects outside range, if there's a range set
			if self.rad > 0 and self.rad < util.dist(magobj.pos, o.pos):
				continue
			
			o.body.addForce(util.mag_force(magobj.pos, o.pos, o.body.getMass().mass, self.pow, self.loss, self.gravity))

class CBoxMagnet:
	"""A controller like CMagnet, only the source is not a point but a box.

	Objects are affected as though by a CMagnet point at the nearest part of the box
	to the object.
	
	Data attributes:
	pow -- The amount of force applied per simstep. If negative, pulls instead of pushing.
	size -- The size of the magnet box, centered at the magnet object's pos
	rad -- The radius of the effect in meters. If non-positive, unlimited radius.
	loss -- The amount of force lost per meter distance from the object.
	      This just brings 'pow' that much closer to zero depending on distance.
			It will never allow pow to go past zero.
	gravity -- If True, then actual mass of object is ignored; act as though object had a mass of 1.
	active -- If False, then the effect is disabled.
	"""
	
	def __init__(self, pow, size, rad = 0, loss = 0, gravity = False, active = True):
		self.pow = pow
		self.size = size
		self.rad = rad
		self.loss = loss
		self.gravity = gravity
		self.active = active
	
	def do(self, magobj):
		if not self.active:
			return
		
		#For every object excluding the actual pulling object, check if we're affecting it
		for o in app.objects:
			if o == magobj:
				continue
			
			#Ignore objects outside the ODE force system
			if o.body == None:
				continue

			#Find the nearest point on the box to the object
			#If the object is inside the box, then the object's position is the nearest point
			#Otherwise, check all four outer lines and see which resulting point is the nearest
			rect = pygame.Rect((0,0), self.size)
			rect.center = magobj.pos
			nearest = o.pos
			if not rect.collidepoint(o.pos[0], o.pos[1]):
				halfwidth = self.size[0]/2.0
				halfheight = self.size[1]/2.0
				nearest = magobj.pos
				dist = util.dist(nearest, o.pos)
				tl = (magobj.pos[0]-halfwidth, magobj.pos[1]-halfheight)
				tr = (magobj.pos[0]+halfwidth, magobj.pos[1]-halfheight)
				bl = (magobj.pos[0]-halfwidth, magobj.pos[1]+halfheight)
				br = (magobj.pos[0]+halfwidth, magobj.pos[1]+halfheight)
				for s in ((tl,tr), (bl,br), (tl,bl), (tr,br)):
					cand = util.nearest_on_line(s[0], s[1], o.pos)
					cand_dist = util.dist(cand, o.pos)
					if cand_dist < dist:
						dist = cand_dist
						nearest = cand
			
			#Ignore objects outside range, if there's a range set
			if self.rad > 0 and self.rad < util.dist(nearest, o.pos):
				continue
			
			o.body.addForce(util.mag_force(nearest, o.pos, o.body.getMass().mass, self.pow, self.loss, self.gravity))


class CCameraFollow:
	"""A controller that changes app.camera to keep the object centered, without going outside bounds.
	
	Don't have more than one camera controller active at once.
	
	Data attributes:
	active -- If false, then do() does nothing.
	bounds -- Prevents the player from viewing anything outside this rectangle (in meters). Can be None.
	"""
	
	def __init__(self, bounds = None, active = True):
		self.bounds = bounds
		self.active = active

	def do(self, obj):
		if not self.active:
			return
		app.camera = obj.pos
