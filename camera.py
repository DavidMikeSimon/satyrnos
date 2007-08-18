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
	
	def __init__(self, bounds = None, offset = None):
		super(DCameraDirect, self).__init__(drawing = True)
		self.bounds = bounds
		if offset == None: self.offset = Point(0, 0)
		else:	self.offset = offset
	
	def _predraw(self, obj):
		wanted_pos = obj.pos + self.offset
		if self.bounds == None:
			app.camera = wanted_pos
		else:
			app.camera = self.bounds.nearest_pt_to(wanted_pos)

class DCameraLead(drive.Drive):
	"""Drive that changes app.camera to show where the object's going, without going outside bounds.
	
	DCameraLead looks ahead of the object based on its velocity. When
	the object's velocity is higher than a certain amount, the camera pans forward
	to show where the object is going. It pans all the way out to lead_length when
	the object reaches max_speed.
	
	Don't have more than one camera drive active at once.
	
	Data attributes:
	bounds -- A rectangle which the camera's center can never
		move outside of. If it's None, camera can go anywhere.
	max_speed -- How many m/s of object speed before the camera is offset by lead_length, and zoomed out by max_zoom.
	lead_length -- How far the camera can pan ahead.
	cam_speed -- How quickly, in meters per second, the camera moves towards desired offset.
	max_zoom -- How far the camera can zoom out past the neutral 1.0
	zoom_speed -- How quickly, in zoom units per second, the camera can change zoom
	"""
	
	def __init__(self, bounds = None, max_speed = 4.0, lead_length = 0.5, cam_speed = 1, max_zoom = 0.4, zoom_speed = 0.5):
		super(DCameraLead, self).__init__(drawing = True, stepping = True)
		self.bounds = bounds
		self.max_speed = max_speed
		self.lead_length = lead_length
		self.cam_speed = cam_speed
		self.max_zoom = max_zoom
		self.zoom_speed = zoom_speed
		self._cur_offset = Point(0, 0) #The camera's offset as of now
		self._cur_zoom = 0 #The camera's zoom offset as of now (added to the neutral 1.0 zoom)
	
	def _step(self, obj):
		speed = min(obj.vel.mag(), self.max_speed)
		
		des_offset = obj.vel.to_length(self.lead_length * (speed/self.max_speed))
		diff = des_offset - self._cur_offset
		if diff.mag() > self.cam_speed/app.maxfps:
			diff = diff.to_length(self.cam_speed/app.maxfps)
		self._cur_offset += diff
		
		des_zoom = self.max_zoom * (speed/self.max_speed)
		diff = des_zoom - self._cur_zoom
		if abs(diff) > self.zoom_speed/app.maxfps:
			if diff > 0:
				diff = self.zoom_speed/app.maxfps
			else:
				diff = -self.zoom_speed/app.maxfps
		self._cur_zoom += diff
	
	def _predraw(self, obj):
		#app.zoom = 1.0 + self._cur_zoom
		DCameraDirect(self.bounds, self._cur_offset)._predraw(obj)
