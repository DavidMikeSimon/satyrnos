import pygame

import app, math, util

def mag_force(source, target, tgtmass, pow, loss = 0, grav = False):
	"""Returns a 3-tuple, appropriate for passing to body.addForce(), for a magnetic/gravitational force.
	
	Force is emanating from source, affecting target. Both are passed as 2-tuples.
	Pow is the amount of force applied. Negative for pulling, positive for pushing.
	Loss is the amount of force lost per meter distance from the object (brings pow closer to zero).
	If grav is true, then mass of object is ignored; it acts as though objects have a mass of 1.
	"""
	
	#If we have loss, determine the actual amount of force applied
	force = pow
	d = util.dist(source, target)
	if loss != 0:
		diff = d*loss
		if pow > 0:
			diff = -diff
		force += diff
		#If the loss is so powerful that we change from pushing to pulling or vice versa, then cancel
		if (force > 0) != (pow > 0):
			return ((0, 0, 0))
	
	#If we're a gravity-like force (mass of object disregarded), adjust applied force to compensate
	if grav:
		force *= tgtmass
			
	#Calculate and return the force
	ang = math.atan2(target[1]-source[1], target[0]-source[0])
	return ((force*math.cos(ang), force*math.sin(ang), 0))


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
			
			o.body.addForce(mag_force(magobj.pos, o.pos, o.body.getMass().mass, self.pow, self.loss, self.gravity))


class CLineMagnet:
	"""A controller like CMagnet, only the source is not a point but a line.

	Objects are affected as though by a CMagnet point at the nearest point on
	the line to the object.
	
	Data attributes:
	pow -- The amount of force applied per simstep. If negative, pulls instead of pushing.
	end -- A point, relative to object position, defining one end of the magnet line, where the object's position is the center.
	rad -- The radius of the effect in meters. If non-positive, unlimited radius.
	loss -- The amount of force lost per meter distance from the object.
	      This just brings 'pow' that much closer to zero depending on distance.
			It will never allow pow to go past zero.
	gravity -- If True, then actual mass of object is ignored; act as though object had a mass of 1.
	active -- If False, then the effect is disabled.
	"""
	
	def __init__(self, pow, end, rad = 0, loss = 0, gravity = False, active = True):
		self.pow = pow
		self.end = end
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

			#Find the nearest point on the line to the object
			right_end = util.rotp(util.tupa(magobj.pos, self.end), magobj.pos, magobj.ang)
			left_end = util.rotp(util.tupa(magobj.pos, util.tupm(self.end, -1)), magobj.pos, magobj.ang)
			nearest = util.nearest_on_line((left_end, right_end), o.pos)
			
			#Ignore objects outside range, if there's a range set
			if self.rad > 0 and self.rad < util.dist(nearest, o.pos):
				continue
			
			o.body.addForce(mag_force(nearest, o.pos, o.body.getMass().mass, self.pow, self.loss, self.gravity))

	

class CBoxMagnet:
	"""A controller like CMagnet, only the source is not a point but a box.

	Objects are affected as though by a CMagnet point at the nearest part of the box
	to the object.
	
	Data attributes:
	pow -- The amount of force applied per simstep. If negative, pulls instead of pushing.
	size -- The size of the magnet box, centered at the magnet object's pos.
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
			
			#Ignore objects outside range, if there's a range set
			nearest = util.nearest_in_box(magobj.pos, self.size, magobj.ang, o.pos)
			if self.rad > 0 and self.rad < util.dist(nearest, o.pos):
				continue
			
			o.body.addForce(mag_force(nearest, o.pos, o.body.getMass().mass, self.pow, self.loss, self.gravity))


class CCameraFollow:
	"""A controller that changes app.camera to keep the object centered, without going outside bounds.
	
	Don't have more than one camera controller active at once.
	
	Data attributes:
	active -- If false, then do() does nothing.
	boundlist -- A list of rectangles that the camera's center will be restricted to. If there any boxes
	             then the camera will refuse to go anywhere where it isn't in at least one of the boxes.
	             If the list is empty, then the camera can go anywhere. The rectangles are specified
					 as ((pos), (size)).
	"""
	
	def __init__(self, boundlist = [], active = True):
		self.boundlist = boundlist
		self.active = active
	
	def do(self, obj):
		if not self.active:
			return
		app.camera = obj.pos
