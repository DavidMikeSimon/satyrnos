import math, ode, sre
from OpenGL.GL import *

import app, util, hull
from geometry import *

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
		Setting geom will cause it to be ssociated with
		body, if there is one set. The old geom is also automatically
		unassociated and destroyed. Additionally, pos and ang
		are automatically loaded from geom after it is set, and body's
		ang and pos are overwritten.
	drives -- A util.TrackerList of drives. Each simstep, each drive's step method
		is called in order. Each frame, every object's predraw method
		is called, then after that's done, every object's draw method
		is called.
	
	"""
	
	def __init__(self, pos = None, ang = 0, body = None, geom = None, drives = None):
		"""Creates a GameObj. Pos and ang given override the position of body and/or geom.
		
		If the drives argument passed in is not a TrackerList, then it is converted to
		one for you.
		"""
		self._body = None
		self._geom = None
		self.body = body #This calls the smart setter,
		self.geom = geom #This also calls smart setter, which associates if possible
		
		if pos == None: self.pos = Point(0.0, 0.0)
		else: self.pos = pos #Overwrite ODE position with the passed-in position
		self.ang = ang #Overwrite ODE angle too
		
		if drives == None: self.drives = util.TrackerList()
		elif isinstance(drives, util.TrackerList): self.drives = drives
		else: self.drives = util.TrackerList(drives)
	
	def __str__(self):
		return " GO: (%7.3f, %7.3f) %s [%s]" % (
			self.pos.x,
			self.pos.y,
			("%06.3f" % self.ang)[2:], #Cut off negative sign (-0.0's are common) and whole number part
			", ".join([str(d) for d in self.drives])
		)
	
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
		odething.setPosition(self._pos.fake_3d_tuple())
	
	def sync_ode(self):
		"""Sets position and rotation based on the ODE state, cancels non-two-dimensional motion.
		
		This is called automatically by the main loop after the simstep is ran, so it isn't
		neccessary for drives or game objects to call it themselves.

		After it's done syncing itself, it calls sync_ode on all the drives.
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
	
	def draw(self, draw_geom = None):
		"""Draws the object; pushes correct GL matrix, calls draw() on every drive, restores GL.
		
		Optionally, specify the draw_hull argument. Set it to False to not draw a hall, True to draw it,
		or None (that is, just leave it unset) to use the value from app.ui.draw_geoms."""
		if draw_geom == None:
			draw_geom = app.ui.draw_geoms
		glPushMatrix()
		glTranslatef(self.pos[0], self.pos[1], 0)
		if (self.ang > 0.00001):
			glRotatef(util.rev2deg(self.ang), 0, 0, 1)
		for d in self.drives:
			d.draw(self)
		if self.geom != None and draw_geom:
			self.geom.draw_drive.draw(self)
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

class LimbedGameObj(GameObj):
	"""A GameObj that has some limbs attached.
	
	The limbs are just other GameObjs. This GameObj's regular geom is kept in a space, the geom_space data
	attribute, which also contains the geoms of all the sub-objects.

	During the process of running step(), draw(), etc., the following steps are made:
	- The regular drives for the object are ran
	- The drives for each limb are ran
	- The 'drives' attribute is temporarily set to the postdrives, those drives are ran, then the attribute is restored
	
	Data attributes (other than ones in GameObj that are still here):
	postdrives -- A TrackerList of drives which are ran _after_ the limb drives are ran.
	space -- An ODE space which contains this object's geom and the geoms of all limbs.
	limbs -- A TrackerList of other GameObjs that are attached to the main one.
	joints -- A TrackerList of HingeJoints connecting the limbs to the main geom. Add to this with the add_limb method.
	"""

	_tabberpat = sre.compile(r"^", sre.M)
	
	def __init__(self, pos = None, ang = 0, body = None, drives = None, space = None, postdrives = None):
		"""Creates a LimbedGameObj. Pos and ang given override the position of body.

		Note that you cannot pass a geom into the constructor. That's because when an ODE geom is created, you have to give it
		a parent at that time, and it's stuck with that parent forever. This means that you have to first create the LimbedGameObj
		with a geom_space, and then assign a geom afterwords with that geom_space as the parent.
		
		If the drives argument passed in is not a TrackerList, then it is converted to
		one for you.

		For draw(), step(), predraw(), and sync_ode(), after the main object is done, the call is propogated on to the limbs.
		"""
		super(LimbedGameObj, self).__init__(pos, ang, body, None, drives)
		
		self.limbs = util.TrackerList()
		self.joints = util.TrackerList()

		if space == None: self.space = ode.SimpleSpace(app.dyn_space)
		else: self.space = space
		
		if postdrives == None: self.postdrives = util.TrackerList()
		elif isinstance(postdrives, util.TrackerList): self.postdrives = postdrives
		else: self.postdrives = util.TrackerList(postdrives)
	
	def __str__(self):
		ret = super(LimbedGameObj, self).__str__().replace(" ", "L", 1) #To make it line up with " GO" lines
		ret += "\n" + sre.sub(self._tabberpat, "   ", str(self.limbs)).rstrip()
		return ret
	
	def add_limb(self, limb, anchor):
		"""Adds a limb to the limbs data attribute, attaching it with a HingeJoint.
		
		Limb objects, when passed in, should already be positioned correctly. It should have
		a geom that is a child of the LimbedGameObj's space. The anchor
		argument should be an offset relative to the object's center where the joint should be attached.
		"""	
		self.limbs.append(limb)
		joint = ode.HingeJoint(app.odeworld)
		joint.attach(limb.body, self.body)
		joint.setAnchor((self.pos[0] + anchor[0], self.pos[1] + anchor[1], 0))
		joint.setAxis((0, 0, 1))
		self.joints.append(joint)
	
	def draw(self):
		super(LimbedGameObj, self).draw()
		for limb in self.limbs:
			limb.draw()
		temp_drives = self.drives
		self.drives = self.postdrives
		super(LimbedGameObj, self).draw(draw_geom = False)
		self.drives = temp_drives
	
	def predraw(self):
		super(LimbedGameObj, self).predraw()
		for limb in self.limbs:
			limb.predraw()
		temp_drives = self.drives
		self.drives = self.postdrives
		super(LimbedGameObj, self).predraw()
		self.drives = temp_drives
	
	def step(self):
		super(LimbedGameObj, self).step()
		for limb in self.limbs:
			limb.step()
		temp_drives = self.drives
		self.drives = self.postdrives
		super(LimbedGameObj, self).step()
		self.drives = temp_drives
	
	def sync_ode(self):
		super(LimbedGameObj, self).sync_ode()
		for limb in self.limbs:
			limb.sync_ode()
