import ode

import app

class Props:
	"""Defines the collision properties of some object.
		
	The reason for the special exception is because two objects that
	collide physically may require either a ContactJoint between them if they've
	got equal collision priority, or may require a ContactJoint between the world
	and the one with lesser priority. There's no reason I can think of now
	to have any more than two layers of priority, but what the heck. The point
	of this system is to allow things like moving platforms that have bodies
	and geoms but cannot be pushed around by the player, although they can push
	the player around.
	
	Data attributes:
	intersec_push -- If True, creates contact joints at intersections to push this object, the other, or both away.
		Both objects must have this flag on for any intersection prevention to occur.
	intersec_pri -- The numeric collision priority for intersection-stopping (defaults to 1).
	"""
	
	def __init__(self, intersec_push = True, intersec_pri = 1):
		self.intersec_push = intersec_push
		self.intersec_pri = intersec_pri
	
	def handle_collision(self, geom1, geom2, cjointgroup):
		"""Checks for a real collision between geom1 (which should be the geom that has this Props as a
		.coll_props data attribute) and some other geom, also with a valid .coll_props. If there is a
		collision, appropriate action is taken (callbacks, contact joints, etc).
		
		For any given collision, this is only called once, so this method needs to handle
		both this object's reaction as well as the other's.
		
		Newly created contact joints are placed into cjointgroup."""
		
		#TODO: ADD CALLBACK QUEUEING STUFF HERE
		if (self.intersec_push and geom2.coll_props.intersec_push) or (True):
			contacts = ode.collide(geom1, geom2)
			if self.intersec_push and geom2.coll_props.intersec_push:
				for c in contacts:
					c.setMode(ode.ContactApprox1 | ode.ContactBounce)
					c.setBounce(0.5)
					c.setMu(5000)
					cjoint = ode.ContactJoint(app.odeworld, cjointgroup, c)
					if (self.intersec_pri == geom2.coll_props.intersec_pri):
						#Push both objects away from each other
						cjoint.attach(geom1.getBody(), geom2.getBody())
					elif (self.intersec_pri > geom2.coll_props.intersec_pri):
						#Push the other object, but not this one
						cjoint.attach(None, geom2.getBody())
					else:
						#Push this object, not the other one
						cjoint.attach(geom1.getBody(), None)
			if len(contacts) > 0:
				pass #TODO: CALLBACK QUEUEING STUFF HERE
