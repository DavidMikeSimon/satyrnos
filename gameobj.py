import math
import ode

import app
import util
from geometry import *

from OpenGL.GL import *

class GameObj(object):
	"""The base class for in-game objects of all kinds.

	Behavior, both in terms of affecting game state and drawing stuff
	to the screen or playing sounds, is determined entirely by
	drives and/or the ODE body and geom.

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
	drives -- A util.TrackerList of drives. Each simstep, each drive's step method
		is called in order. Each frame, every object's predraw method
		is called, then after that's done, every object's draw method
		is called.
	
	"""
	
	def __init__(self, pos = Point(0.0, 0.0), ang = 0, body = None, geom = None, drives = util.TrackerList()):
		"""Creates a GameObj. Pos given overrides the position of body and/or geom.
		
		If the drives argument passed in is not a TrackerList, then it is converted to
		one for you.
		"""
		self._body = None
		self._geom = None
		self.body = body #This calls the smart setter, which loads ang
		self.geom = geom #This also calls smart setter, which associates if possible (and loads ang again, eh)
		self.sync_ode() #Fetch the angle and position from ODE (though we're about to override them)
		self.pos = pos #Overwrite ODE position with the passed-in position
		self.ang = ang #Overwrite ODE angle too
		if not isinstance(drives, util.TrackerList):
			self.drives = drives
		else:
			self.drives = util.TrackerList(drives)
	
	def _get_geom(self): return self._geom
	
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
	
	def _get_body(self): return self._body
	
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
	
	def _get_pos(self): return self._pos
	
	def _set_pos(self, pos):	
		self._pos = pos
		
		#If body and geom are connected, setting pos or ang in one sets it in both
		if self._body != None: self._set_ode_pos(self._body)
		elif self._geom != None: self._set_ode_pos(self._geom)
	
	def _get_ang(self): return self._ang
	
	def _set_ang(self, ang):
		#Wrap to [0-1) revolutions
		self._ang = ang % 1
		
		#If body and geom are connected, setting pos or ang in one sets it in both
		if self._body != None: self._set_ode_ang(self._body)
		elif self._geom != None: self._set_ode_ang(self._geom)
	
	def _fetch_ode_from(self, odething):
		"""Sets position and rotation from the given ODE object (either a body or a geom)."""
		
		#Ignore the z-axis
		odepos = odething.getPosition()
		self._pos = Point(odepos[0], odepos[1])
		
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
		neccessary for drives or game objects to call it themselves.
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
	
	def step(self):
		"""Does a simulation step for the object; calls do() on every drive."""
		for d in self.drives:
			d.step(self)
	
	def predraw(self):
		"""Calls predraw() on every drive."""
		for d in self.drives:
			d.predraw(self)
	
	def draw(self):
		"""Draws the object; pushes correct GL matrix, calls draw() on every drive, restores GL."""
		glPushMatrix()
		glTranslatef(self.pos[0], self.pos[1], 0)
		if (self.ang > 0.00001):
			glRotatef(util.rev2deg(self.ang), 0, 0, 1)
		for d in self.drives:
			d.draw(self)
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
