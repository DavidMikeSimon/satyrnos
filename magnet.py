from __future__ import division
import app, math, util, drive
from geometry import *

def mag_force(source, target, tgtmass, pow, loss = 0, grav = False):
	"""Returns a 3-tuple, appropriate for passing to body.addForce(), for a magnetic/gravitational force.
	
	Force is emanating from source, affecting target. Both are passed as 2-tuples.
	Pow is the amount of force applied. Negative for pulling, positive for pushing.
	Loss is the amount of force lost per meter distance from the object (brings pow closer to zero).
	If grav is true, then mass of object is ignored; it acts as though objects have a mass of 1.
	"""
	
	#If we have loss, determine the actual amount of force applied
	force = pow
	d = source.dist_to(target)
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


class DMagnet(drive.Drive):
	"""Drive that creates a point of gravitational/magnetic attraction or repulsion.
	
	Data attributes:
	pow -- The amount of force applied per simstep. If negative, pulls instead of pushing.
	rad -- The radius of the effect in meters. If non-positive, unlimited radius.
	loss -- The amount of force lost per meter distance from the object.
		This just brings 'pow' that much closer to zero depending on distance.
		It will never allow pow to go past zero.
	gravity -- If True, then actual mass of object is ignored; act as though object had a mass of 1.
	"""

	def __init__(self, pow, rad = 0, loss = 0, gravity = False):
		super(DMagnet, self).__init__(stepping = True)
		self.pow = pow
		self.rad = rad
		self.loss = loss
		self.gravity = gravity
	
	def _step(self, magobj):
		didit = False
		for first in app.collisions.keys():
			didit = True
			for second in app.collisions[first]:
				print "FIRST: %s   SECOND: %s" % (first, second)
		if didit:
			print "---"
			
		#For every object excluding the actual pulling object, check if we're affecting it
		for o in app.objects:
			if o == magobj:
				continue
			
			#Ignore objects outside the ODE force system
			if o.body == None:
				continue
			
			#Ignore objects outside range, if there's a range set
			if self.rad > 0 and self.rad < magobj.pos.dist_to(o.pos):
				continue
			
			o.body.addForce(mag_force(magobj.pos, o.pos, o.body.getMass().mass, self.pow, self.loss, self.gravity))


class DLineMagnet(drive.Drive):
	"""Drive like DMagnet, only the source is not a point but a line.

	Objects are affected as though by a DMagnet point at the nearest point on
	the line to the object.
	
	Data attributes:
	pow -- The amount of force applied per simstep. If negative, pulls instead of pushing.
	end -- A point, relative to object position, defining one end of the magnet line, where the object's position is the center.
	rad -- The radius of the effect in meters. If non-positive, unlimited radius.
	loss -- The amount of force lost per meter distance from the object.
		This just brings 'pow' that much closer to zero depending on distance.
		It will never allow pow to go past zero.
	gravity -- If True, then actual mass of object is ignored; act as though object had a mass of 1.
	"""
	
	def __init__(self, pow, end, rad = 0, loss = 0, gravity = False):
		super(DLineMagnet, self).__init__(stepping = True)
		self.pow = pow
		self.end = end
		self.rad = rad
		self.loss = loss
		self.gravity = gravity
	
	def _step(self, magobj):
		#For every object excluding the actual pulling object, check if we're affecting it
		for o in app.objects:
			if o == magobj:
				continue
			
			#Ignore objects outside the ODE force system
			if o.body == None:
				continue

			#Find the nearest point on the line to the object
			magline = Line(
				(magobj.pos + self.end).rot(magobj.pos, magobj.ang),
				(magobj.pos - self.end).rot(magobj.pos, magobj.ang))
			nearest = magline.nearest_pt_to(o.pos)
			
			#Ignore objects outside range, if there's a range set
			if self.rad > 0 and self.rad < nearest.dist_to(o.pos):
				continue
			
			o.body.addForce(mag_force(nearest, o.pos, o.body.getMass().mass, self.pow, self.loss, self.gravity))

	

class DRectMagnet(drive.Drive):
	"""Drive like DMagnet, only the source is not a point but a rectangle.

	Objects are affected as though by a DMagnet point at the nearest part of the rect
	to the object.
	
	Data attributes:
	pow -- The amount of force applied per simstep. If negative, pulls instead of pushing.
	size -- The size of the magnet rect, centered at the magnet object's pos.
	rad -- The radius of the effect in meters. If non-positive, unlimited radius.
	loss -- The amount of force lost per meter distance from the object.
	    This just brings 'pow' that much closer to zero depending on distance.
		It will never allow pow to go past zero.
	gravity -- If True, then actual mass of object is ignored; act as though object had a mass of 1.
	"""
	
	def __init__(self, pow, size, rad = 0, loss = 0, gravity = False):
		super(DRectMagnet, self).__init__(stepping = True)
		self.pow = pow
		self.size = size
		self.rad = rad
		self.loss = loss
		self.gravity = gravity
	
	def _step(self, magobj):
		#For every object excluding the actual pulling object, check if we're affecting it
		mag_rect = Rect(magobj.pos, self.size, magobj.ang)
		for o in app.objects:
			if o == magobj:
				continue
			
			#Ignore objects outside the ODE force system
			if o.body == None:
				continue
			
			#Ignore objects outside range, if there's a range set
			nearest = mag_rect.nearest_pt_to(o.pos)
			if self.rad > 0 and self.rad < nearest.dist_to(o.pos):
				continue
			
			o.body.addForce(mag_force(nearest, o.pos, o.body.getMass().mass, self.pow, self.loss, self.gravity))
