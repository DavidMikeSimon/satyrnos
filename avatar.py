from __future__ import division
import sys,pygame,math
from pygame.locals import *

import app, colors, drive, image
from geometry import *

class DAvatar(drive.Drive):
	"""Drive that controls/draws the main character.
	
	This drive does not control the camera; use the drives in camera.py for that.
	
	Data attributes:
	sprite -- The sprite being used to draw Satyrn himself at the moment.
		This is also used to figure out some parts of Satyrn's current state.
	charge_push -- How hard to push for each pulse.
	cruise_push -- How hard to push each step when directional buttons are
		pressed without charging up.
	cruise_speed -- The maximum linear speed (in terms of body.getLinearVel) that
		Satyrn can reach without doing a charged boost.
	"""
	
	def __init__(self):
		super(DAvatar, self).__init__(drawing = True, stepping = True)
		self.sprite = image.DImage("satyrn/float.png", Size(1.0, 1.0))
		self.charge_push = 60
		self.cruise_push = 1
		self.cruise_speed = 1
	
	def _draw(self, obj):
		self.sprite.draw(obj)
		if self.charge_begin != -1:
			diff = pygame.time.get_ticks() - self.charge_begin
			if diff < self.charge_gap:
				self.charge_sprite1.draw(obj)
			elif diff < self.charge_gap*2:
				self.charge_sprite2.draw(obj)
			else:
				self.charge_sprite3.draw(obj)
	
	def _step(self, obj):
		# Add strong angular drag; Satyrn has a tendency to make himself stop rotating
		# TODO: Implement this
		
		# Make sure we're working with current key states
		pygame.event.pump()
		keys = pygame.key.get_pressed()
			
		# Figure out which direction the user wants to go in
		push_vec = Point(0, 0)
		if keys[K_UP]:
			push_vec[1] = -1
		if keys[K_LEFT]:
			push_vec[0] = -1
		if keys[K_DOWN]:
			push_vec[1] = 1
		if keys[K_RIGHT]:
			push_vec[0] = 1
		
		if self.charge_begin == -1:
			# If we are not charging up, then the keys just allow minor movement
			# They do not allow you to reach a linear speed greater than cruise_speed
			# TODO: Actually make it limit linear velocity here
			push_vec = push_vec.to_length(self.cruise_push)
			obj.body.addForce(push_vec.fake_3d_tuple())
		elif not keys[K_c]:
			# The user has just released a charge, so let's do a boost
			push_len = self.charge_push * min(math.ceil((pygame.time.get_ticks() - self.charge_begin)/self.charge_gap), 3)
			push_vec = push_vec.to_length(push_len)
			obj.body.addForce(push_vec.fake_3d_tuple())
			self.charge_begin = -1
		
		# Keep track of when the user begins holding down the charge button
		if self.charge_begin == -1 and keys[K_c]:
			self.charge_begin = pygame.time.get_ticks()
