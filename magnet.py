from __future__ import division
import app, math, util, drive, geommold, collision
from geometry import *

def mag_force(source, target, tgtmass, pow, loss = 0, grav = False):
	"""Returns a 3-tuple, appropriate for passing to body.addForce(), for a magnetic/gravitational force.
	
	Force is emanating from source, affecting target. Both are passed as 2-tuples.
	Pow is the amount of force applied. Negative for pulling, positive for pushing.
	Loss is the amount of force lost per meter distance between magnet source and magnetized point of target object.
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
			return Point(0, 0)
	
	#If we're a gravity-like force (mass of object disregarded), adjust applied force to compensate
	if grav:
		force *= tgtmass
			
	#Calculate and return the force
	ang = math.atan2(target[1]-source[1], target[0]-source[0])
	return Point(force*math.cos(ang), force*math.sin(ang))


class DMagnet(drive.Drive):
	"""Drive that creates a point of gravitational/magnetic attraction or repulsion.
	
	Data attributes:
	pow -- The amount of force applied per simstep. If negative, pulls instead of pushing.
	rad -- The radius of the effect in meters. If non-positive, unlimited radius.
	loss -- The amount of force lost per meter distance between magnet's center and magnetized point of target object.
		This just brings 'pow' that much closer to zero depending on distance.
		It will never allow pow to go past zero, or to go above its normal distance.
	gravity -- If True, then actual mass of object is ignored; act as though object had a mass of 1.
	"""

	def __init__(self, pow, rad = 0, loss = 0, gravity = False):
		super(DMagnet, self).__init__(stepping = True)
		self.pow = pow
		self.rad = rad
		self.loss = loss
		self.gravity = gravity
		
		# A non-intersec-pushing sphere so we can easily figure out which things are in range
		if rad != 0:
			self._geom = geommold.CircleGeomMold().make_geom(Size(abs(rad)*2,abs(rad)*2), coll_props = collision.Props(False))
			self._geom_placed = False
		else:
			self._geom = None
	
	def _step(self, magobj):
		#If this one has limited range
		#No magnetism on the first step, since that step has to be used to initially set the magnet's range geom
		#Also, we use setPosition, not setBody, since the magnet doesn't necessarily have to have a body
		if self._geom != None:
			self._geom.setPosition(magobj.pos.fake_3d_tuple())
			self._geom_placed = True
		
		# Figure out which objects are in range of the magnet
		targets = []
		if self._geom != None and self._geom_placed and app.collisions.has_key(id(self._geom)):
			for other in app.collisions[id(self._geom)]:
				targets.append((other.geom.gameobj, other.avg_pos))
		elif self._geom == None:
			for obj in app.objects:
				targets.append((obj, obj.pos))
		
		#For each object in range, affect it magnetically if we should 
		for (obj, mpoint) in targets:
			# Magnet shouldn't affect itself
			if obj is magobj:
				continue
			
			if obj.body != None:
				force = mag_force(magobj.pos, mpoint, obj.body.getMass().mass, self.pow, self.loss, self.gravity)
				obj.body.addForceAtPos(force.fake_3d_tuple(), mpoint.fake_3d_tuple())
			
			if magobj.body != None:
				force = mag_force(mpoint, magobj.pos, magobj.body.getMass().mass, self.pow, self.loss, self.gravity)
				magobj.body.addForce(force.fake_3d_tuple())


class DLineMagnet(drive.Drive):
	"""Drive like DMagnet, only the source is not a point but a line.
	
	Objects with this drive should probably have "magnetic" in their props set as well. Otherwise, it
	will not be possible for other magnets to push or pull this one.

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
	
	Objects with this drive should probably have "magnetic" in their props set as well. Otherwise, it
	will not be possible for other magnets to push or pull this one.

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
