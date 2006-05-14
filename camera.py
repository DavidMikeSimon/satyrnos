from __future__ import division
import math, copy
import app, util, drive
from geometry import *

class DCameraDirect(drive.Drive):
	"""Drive that changes app.camera to keep the object centered, without going outside bounds.
	
	Don't have more than one camera drive active at once.
	
	Data attributes:
	bounds -- A rectangle which the camera's center can never
		move outside of. If it's None, camera can go anywhere.
	offset -- Applied to the position of the camera, relative to the object's position. If
		offset would cause the camera to move outside bounds, the camera places itself as
		close as it can to the desired offset position.
	"""
	
	def __init__(self, bounds = None, offset = Point(0, 0)):
		self.bounds = bounds
		self.offset = offset
	
	def _predraw(self, obj):
		wanted_pos = obj.pos + self.offset
		if self.bounds == None:
			app.ui.camera = wanted_pos
		else:
			app.ui.camera = self.bounds.nearest_pt_to(wanted_pos)

class DCameraLead(drive.Drive):
	"""Drive that changes app.camera to show where the object's going, without going outside bounds.
	
	DCameraLead looks ahead of the object based on its velocity, which is calculated just by
	comparing snapshots (so, it's not neccessary that the object have an ODE body). When
	the object's velocity is higher than a certain amount, the camera pans forward
	to show where the object is going. The amount of desired pan is fixed (either no pan, or full pan
	once velocity is high enough), but the camera approaches the desired pan at a steady speed so
	that it seems smoother.
	
	Don't have more than one camera drive active at once.
	
	Data attributes:
	bounds -- A rectangle which the camera's center can never
		move outside of. If it's None, camera can go anywhere.
	min_vel -- How many m/s of object speed required for the camera to want to pan ahead.
	lead_length -- How far the camera wants to pan ahead.
	speed -- How quickly, in meters per second, the camera moves towards desired offset.
	"""
	
	def __init__(self, bounds = None, min_vel = 1.5, lead_length = 0.6, speed = 0.4):
		super(DCameraLead, self).__init__(True, False)
		self.bounds = bounds
		self.min_vel = min_vel
		self.lead_length = lead_length
		self.speed = speed
		self._cur_offset = Point(0, 0) #The camera's offset as of now
		self._last_obj_pos = Point(0, 0) #The object's last position (for tracking its velocity)
		self._inited = False #So we know that _obj_pos is invalid the first run of _predraw
	
	def _predraw(self, obj):
		time = app.ui.msecs/1000
		for axis in range(0, 2):
			obj_vel = 0
			if self._inited == True:
				obj_vel = (obj.pos[axis] - self._last_obj_pos[axis])/time

			wanted_offset = 0
			if obj_vel > self.min_vel:
				wanted_offset = self.lead_length
			elif -obj_vel > self.min_vel:
				wanted_offset = -self.lead_length

			if (axis == 0):
				app.calcvel = obj_vel
			
			if abs(self._cur_offset[axis] - wanted_offset) < self.speed*time:
				self._cur_offset[axis] = wanted_offset
			elif (self._cur_offset[axis] < wanted_offset):
				self._cur_offset[axis] += self.speed*time
			else:
				self._cur_offset[axis] -= self.speed*time
			
		if self._inited == False: self._inited = True
		self._last_obj_pos = obj.pos
		
		DCameraDirect(self.bounds, self._cur_offset)._predraw(obj)
