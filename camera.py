from __future__ import division
import math
import app, util, drive

class InvalidBoundsError(Exception):
	"""Thrown when a camera drive is passed an unacceptable bounding rectangle.
	
	Typically this happens if the rectangle isn't large enough to contain at
	least one screen."""
	
class DCameraDirect(drive.Drive):
	"""Drive that changes app.camera to keep the object centered, without going outside bounds.
	
	Don't have more than one camera drive active at once.
	
	Data attributes:
	bounds -- A rectangle, specified as ((centerx, centery), (width, height)), which the camera can never
		move outside of. If it's None, camera can go anywhere. Bounds must be at least as big
		as the screen size, or _predraw will throw an InvalidBoundsError.
	offset -- Applied to the position of the camera, relative to the object's position. If
		offset would cause the camera to move outside bounds, the camera places itself as
		close as it can to the desired offset position.
	"""
	
	def __init__(self, bounds = None, offset = (0, 0)):
		self.bounds = bounds
		self.offset = offset
	
	def _predraw(self, obj):
		wanted_pos = util.tupa(obj.pos, self.offset)
		if self.bounds == None:
			app.ui.camera = wanted_pos
		else:
			if self.bounds[0] < app.ui.winmeters[0] or self.bounds[1] < app.ui.winmeters[1]:
				raise InvalidBoundsError
			
			cam_pos_rect = (
				self.bounds[0],
				(self.bounds[1][0]-app.ui.winmeters[0], self.bounds[1][1]-app.ui.winmeters[1]))
			app.ui.camera = util.nearest_in_box(cam_pos_rect[0], cam_pos_rect[1], 0, wanted_pos)

class DCameraLead(drive.Drive):
	"""Drive that changes app.camera to show where the object's going, without going outside bounds.
	
	DCameraLead looks ahead of the object based on its velocity, which is calculated just by
	comparing snapshots (so, it's not neccessary that the object have an ODE body). It moves
	forward in "clicks", pre-notched lengths ahead of the object, and scroll smoothly
	between clicks. The reason to have notched positions, rather than just keeping
	a distance ahead of the object proportionate to its velocity, is that doing it
	the latter way creates a weird sensation of the camera pulling the object around.
	
	Don't have more than one camera drive active at once.
	
	Data attributes:
	bounds -- A rectangle, specified as ((left, top), (width, height)), which the camera can never
		move outside of. If it's None, camera can go anywhere. Bounds must be at least as big
		as the screen size, or _predraw will throw an InvalidBoundsError.
	vel_per_click -- How many m/s of object speed past min_vel_for_offset it takes to move
		one click.
	click_length -- The distance between the clicks. The actual offset moves to a
		position only when the object is going fast enough to push the potential
		desired offset past a click.
	speed -- How quickly, in meters per second, the camera moves towards velocity offset.
	max_offset_scr -- How much (0.0-1.0) of the screen size we can offset to at a maximum.
		This prevents the object from being offseted entirely off the screen.
	"""
	
	def __init__(self, bounds = None, vel_per_click = 1.5, click_length = 0.5, speed = 1, max_offset_scr = 0.36):
		super(DCameraLead, self).__init__(True, False)
		self.bounds = bounds
		self.vel_per_click = vel_per_click
		self.click_length = click_length
		self.speed = speed
		self.max_offset_scr = max_offset_scr
		self._cur_offset = [0, 0] #The camera's offset as of now
		self._last_obj_pos = (0, 0) #The object's last position (for tracking its velocity)
		self._inited = False #So we know that _obj_pos is invalid the first run of _predraw
	
	def _predraw(self, obj):
		time = app.ui.clock.get_time()/1000
		for axis in range(0, 2):
			obj_vel = 0
			if self._inited == True:
				obj_vel = (obj.pos[axis] - self._last_obj_pos[axis])/time
			
			clicked_offset = 0 #The real desired offset, including effects of self.click_length
			wanted_clicks = obj_vel/self.vel_per_click
			
			#Round down to the nearest click that doesn't offset too far
			max_clicks = (self.max_offset_scr*app.ui.winmeters[axis])/self.click_length
			rounded_clicks = max_clicks
			if (wanted_clicks > 0): rounded_clicks = math.floor(wanted_clicks)
			else: rounded_clicks = math.ceil(wanted_clicks)
			clicked_offset = max(-max_clicks, min(max_clicks, rounded_clicks))*self.click_length
			
			if abs(self._cur_offset[axis] - clicked_offset) < self.speed*time:
				self._cur_offset[axis] = clicked_offset
			elif (self._cur_offset[axis] < clicked_offset):
				self._cur_offset[axis] += self.speed*time
			else:
				self._cur_offset[axis] -= self.speed*time
			
		if self._inited == False:
			self._inited = True
		self._last_obj_pos = obj.pos
		
		subdrive = DCameraDirect(self.bounds, self._cur_offset)
		subdrive._predraw(obj)
