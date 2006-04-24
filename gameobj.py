import math
import ode

import app
import util

from OpenGL.GL import *

class GameObj(object):
	"""The base class for in-game objects of all kinds.

	This base class can also be used for objects which are not drawn, but which
	still have physical effects through controllers and/or ODE. You'll have
	to use a derivative of GameObj if you actually want to see anything, but
	the actual simulation behavior of game objects is determined by ODE settings
	and by controllers, both of which are part of this base object.

	Data attributes:
	pos -- 2-tuple of the absolute location of the center of the object, in meters.
	ang -- The angle of the object, in clockwise revolutions.
	       Set these instead of calling methods on body or geom: ODE
	       will automatically be updated when these are set, and
	       changes in ODE will be restored back to these when restorePhys()
	       is called. Note that ang will be wrapped to (-0.5, 0.5) both
	       when being set and when being fetched from ODE.
			 
	body -- The ODE body used for physical dynamics.
	        This can be None if you don't want an object to ever move.
	        Setting body automatically adjusts geom as needed
	        (i.e. setting collision groups, calling set_body(), etc).
	        The old body is also automatically unassociated and destroyed.
	        Additionally, pos and ang are automatically loaded from body
	        after it is set, and geom's ang and pos are overwritten.
	geom -- The ODE geometry used for collision detection.
	        This can be None if you don't want an object to ever collide.
	        Setting geom automatically results it in being associated with
	        body, if there is one set. The old geom is also automatically
	        unassociated and destroyed. Additionally, pos and ang
	        are automatically loaded from geom after it is set, and body's
			  ang and pos are overwritten.
			  
	controllers -- A list of controllers. Each simstep, each controller's
	               method 'do' is called in order, passed this GameObj as a parameter.
	pens        -- A list of pens. Each draw step, each pen's method 'draw' is called
	               in order, passed this GameObj as a parameter. However, most pens
						probably won't need that GameObj parameter anyways, since draw()
						is called with GL already translated and rotated correctly.
	
	"""
	
	def __init__(self, pos = (0.0, 0.0), body = None, geom = None):
		"""Creates a GameObj. Pos given overrides the position of body and/or geom.
		"""
		self._ang = 0.0 #A reasonable default (assume whatever original orientation is to be 0.0)
		self._body = None
		self._geom = None
		self.body = body #This calls the smart setter, which loads ang
		self.geom = geom #This also calls smart setter, which associates if possible (and loads ang again, eh)
		self.sync_ode() #Fetch the angle and position from ODE (though we're about to override the position)
		self.pos = pos #Overwrite ODE position with the passed-in position
		self.controllers = util.TrackerList()
		self.pens = util.TrackerList()
	
	def _get_geom(self):
		return self._geom
	
	def _set_geom(self, geom):
		#Remove and disassociate existing geom if any
		if self._geom != None:
			self._geom.setBody(None)
			app.odeworld.remove(self._geom)
		
		#Set the new geom, load its ang and pos, and associate it if possible
		self._geom = geom
		if self._geom != None:
			self._fetch_ode_from(self._geom)
			if self._body != None:
				self._set_ode_pos(self._body)
				self._set_ode_ang(self._body)
				self._geom.setBody(self._body)
	
	def _get_body(self):
		return self._body
	
	def _set_body(self, body):
		#Remove and disassociate existing body if any
		if self._geom != None:
			self._geom.setBody(None)
		#if self._body != None:
		
		#Set the new body, load its ang and pos, and associate it if possible
		self._body = body
		if self._body != None:
			self._fetch_ode_from(self._body)
			if self._geom != None:
				self._set_ode_pos(self._geom)
				self._set_ode_ang(self._geom)
		if self._geom != None:
			self._geom.setBody(self._body)
	
	def _get_pos(self):
		return self._pos
	
	def _set_pos(self, pos):	
		self._pos = pos
		
		#If body and geom are connected, setting pos or ang in one sets it in both
		if self._body != None: self._set_ode_pos(self._body)
		elif self._geom != None: self._set_ode_pos(self._geom)
	
	def _get_ang(self):
		return self._ang
	
	def _set_ang(self, ang):
		#Wrap to [0-1) revolutions
		self._ang = ang % 1
		
		#If body and geom are connected, setting pos or ang in one sets it in both
		if self._body != None: self._set_ode_ang(self._body)
		elif self._geom != None: self._set_ode_ang(self._geom)
	
	def _fetch_ode_from(self, odething):
		"""Sets position and rotation from the given ODE object (either a body or a geom)."""
		
		#Ignore the z-axis
		self._pos = odething.getPosition()[0:2]
		
		#Convert ccw radians to cw revolutions
		rot = odething.getRotation()
		uncos = math.acos(rot[0])
		unsin = math.asin(rot[1])
		self._ang = uncos/(-2.0 * math.pi)
		if unsin < 0:
			self._ang = -self._ang

		#Wrap to [0-1) revolutions
		self._ang = self.ang % 1
	
	def _set_ode_ang(self, odething):
		"""Sets the angle in an ODE object (body or geom) from the GameObj's angle.
		
		Converts from GameObj angles (cw revolutions) to ODE angles (ccw radians).
		"""
		a = util.rev2rad(self._ang)
		s = math.sin(a)
		c = math.cos(a)
		rotmatr = (c, s, 0.0, -s, c, 0.0, 0.0, 0.0, 1.0)
		odething.setRotation(rotmatr)
	
	def _set_ode_pos(self, odething):
		"""Sets the position in an ODE object (body or geom) from the GameObj's position."""
		odething.setPosition((self._pos[0], self._pos[1], 0))
	
	def sync_ode(self):
		"""Sets position and rotation based on the ODE state, cancels non-two-dimensional motion.
		
		This is called automatically by the main loop after the simstep is ran, so it isn't
		neccessary for controllers or game objects to call it themselves.
		"""
		
		if self._body != None:
			#Kill z-axis motion
			vel = self._body.getLinearVel()
			self._body.setLinearVel((vel[0], vel[1], 0.0))
			self._body.setAngularVel((0.0, 0.0, self._body.getAngularVel()[2]))

			#Load pos and ang, then set them both back into ODE, sans 3rd dimension
			self._fetch_ode_from(self._body)
			self._set_ode_pos(self._body)
			self._set_ode_ang(self._body)
		elif self._geom != None:
			self._fetch_ode_from(self._geom)
	
	def sim(self):
		"""Does a simulation step for the object; calls do() on every controller."""
		for c in self.controllers:
			c.do(self)
	
	def draw(self):
		"""Draws the object; pushes correct GL matrix, calls draw() on every pen, restores GL."""
		glPushMatrix()
		glTranslatef(self.pos[0], self.pos[1], 0)
		if (self.ang > 0.00001):
			glRotatef(util.rev2deg(self.ang), 0, 0, 1)
		for p in self.pens:
			p.draw(self)
		glPopMatrix()
	
	def freeze(self):
		"""Kills the object's linear and angular velocity."""
		if (self._body == None):
			return
		
		self._body.setLinearVel((0, 0, 0))
		self._body.setAngularVel((0, 0, 0))
	
	def info(self):
		"""Returns a string like so '(x,y) ang', all values expanded to three decimal places."""
		return "(%2.3f, %2.3f) %2.3f" % (self.pos[0], self.pos[1], self.ang)
	
	pos = property(_get_pos, _set_pos)
	ang = property(_get_ang, _set_ang)
	body = property(_get_body, _set_body)
	geom = property(_get_geom, _set_geom)
