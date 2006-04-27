import app, math, util, drive

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
		super(DMagnet, self).__init__(False, True)
		self.pow = pow
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
			
			#Ignore objects outside range, if there's a range set
			if self.rad > 0 and self.rad < util.dist(magobj.pos, o.pos):
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
		super(DLineMagnet, self).__init__(False, True)
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
			right_end = util.rotp(util.tupa(magobj.pos, self.end), magobj.pos, magobj.ang)
			left_end = util.rotp(util.tupa(magobj.pos, util.tupm(self.end, -1)), magobj.pos, magobj.ang)
			nearest = util.nearest_on_line((left_end, right_end), o.pos)
			
			#Ignore objects outside range, if there's a range set
			if self.rad > 0 and self.rad < util.dist(nearest, o.pos):
				continue
			
			o.body.addForce(mag_force(nearest, o.pos, o.body.getMass().mass, self.pow, self.loss, self.gravity))

	

class DBoxMagnet(drive.Drive):
	"""Drive like DMagnet, only the source is not a point but a box.

	Objects are affected as though by a DMagnet point at the nearest part of the box
	to the object.
	
	Data attributes:
	pow -- The amount of force applied per simstep. If negative, pulls instead of pushing.
	size -- The size of the magnet box, centered at the magnet object's pos.
	rad -- The radius of the effect in meters. If non-positive, unlimited radius.
	loss -- The amount of force lost per meter distance from the object.
	    This just brings 'pow' that much closer to zero depending on distance.
		It will never allow pow to go past zero.
	gravity -- If True, then actual mass of object is ignored; act as though object had a mass of 1.
	"""
	
	def __init__(self, pow, size, rad = 0, loss = 0, gravity = False):
		super(DBoxMagnet, self).__init__(False, True)
		self.pow = pow
		self.size = size
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
			
			#Ignore objects outside range, if there's a range set
			nearest = util.nearest_in_box(magobj.pos, self.size, magobj.ang, o.pos)
			if self.rad > 0 and self.rad < util.dist(nearest, o.pos):
				continue
			
			o.body.addForce(mag_force(nearest, o.pos, o.body.getMass().mass, self.pow, self.loss, self.gravity))
