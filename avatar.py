from __future__ import division
import sys,math
from pygame.locals import *

import app, colors, drive, sprite, image
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
		self.sprite = sprite.DSprite("float",
			{
				"crouch-flip":image.DImage("satyrn/crouch-flip.png", Size(1.0, 1.0)),
				"crouch-move":image.DImage("satyrn/crouch-move.png", Size(1.0, 1.0)),
				"crouch":image.DImage("satyrn/crouch.png", Size(1.0, 1.0)),
				"crouch-to-stand":image.DImage("satyrn/crouch-to-stand.png", Size(1.0, 1.0)),
				"float-boost":image.DImage("satyrn/float-boost.png", Size(1.0, 1.0)),
				"float-charge":image.DImage("satyrn/float-charge.png", Size(1.0, 1.0)),
				"float-daze":image.DImage("satyrn/float-daze.png", Size(1.0, 1.0)),
				"float-flip":image.DImage("satyrn/float-flip.png", Size(1.0, 1.0)),
				"float-ow":image.DImage("satyrn/float-ow.png", Size(1.0, 1.0)),
				"float":image.DImage("satyrn/float.png", Size(1.0, 1.0)),
				"float-rotate":image.DImage("satyrn/float-rotate.png", Size(1.0, 1.0)),
				"float-zflip":image.DImage("satyrn/float-zflip.png", Size(1.0, 1.0)),
				"stand-boost":image.DImage("satyrn/stand-boost.png", Size(1.0, 1.0)),
				"stand-charge":image.DImage("satyrn/stand-charge.png", Size(1.0, 1.0)),
				"stand-flip":image.DImage("satyrn/stand-flip.png", Size(1.0, 1.0)),
				"stand-move":image.DImage("satyrn/stand-move.png", Size(1.0, 1.0)),
				"stand":image.DImage("satyrn/stand.png", Size(1.0, 1.0)),
				"stand-to-crouch":image.DImage("satyrn/stand-to-crouch.png", Size(1.0, 1.0)),
			}, {
				"crouch-flip":sprite.DSprite.Anim([("crouch-flip", 100)], "REPEAT"),
				"crouch-move":sprite.DSprite.Anim([("crouch-move", 100)], "REPEAT"),
				"crouch":sprite.DSprite.Anim([("crouch", 100)], "REPEAT"),
				"crouch-to-stand":sprite.DSprite.Anim([("crouch-to-stand", 100)], "REPEAT"),
				"float-boost":sprite.DSprite.Anim([("float-boost", 100)], "REPEAT"),
				"float-charge":sprite.DSprite.Anim([("float-charge", 100)], "REPEAT"),
				"float-daze":sprite.DSprite.Anim([("float-daze", 100)], "REPEAT"),
				"float-flip":sprite.DSprite.Anim([("float-flip", 100)], "REPEAT"),
				"float-ow":sprite.DSprite.Anim([("float-ow", 100)], "REPEAT"),
				"float":sprite.DSprite.Anim([("float", 100)], "REPEAT"),
				"float-rotate":sprite.DSprite.Anim([("float-rotate", 100)], "REPEAT"),
				"float-zflip":sprite.DSprite.Anim([("float-zflip", 100)], "REPEAT"),
				"stand-boost":sprite.DSprite.Anim([("stand-boost", 100)], "REPEAT"),
				"stand-charge":sprite.DSprite.Anim([("stand-charge", 100)], "REPEAT"),
				"stand-flip":sprite.DSprite.Anim([("stand-flip", 100)], "REPEAT"),
				"stand-move":sprite.DSprite.Anim([("stand-move", 100)], "REPEAT"),
				"stand":sprite.DSprite.Anim([("stand", 100)], "REPEAT"),
				"stand-to-crouch":sprite.DSprite.Anim([("stand-to-crouch", 100)], "REPEAT"),
			}
		)
		self.charge_push = 60
		self.cruise_push = 1
		self.cruise_speed = 1
	
	def _draw(self, obj):
		self.sprite.draw(obj)
	
	def _step(self, obj):
		# Add strong angular drag; Satyrn has a tendency to make himself stop rotating
		# TODO: Implement this
		
		# Figure out which direction the user is pressing in
		push_vec = Point(0, 0)
		if app.keys[K_UP]:
			push_vec[1] = -1
		if app.keys[K_LEFT]:
			push_vec[0] = -1
		if app.keys[K_DOWN]:
			push_vec[1] = 1
		if app.keys[K_RIGHT]:
			push_vec[0] = 1
		
		if app.keys[K_c]:
			# If the charge key is held down, then arrow keys just allow finetuning direction
			self.sprite.cur_anim = "float-charge"
		else:
			if push_vec[0] != 0 or push_vec[1] != 0:
				# If the charge key is not held down, then arrow keys are for movement
				self.sprite.cur_anim = "float-boost"
				
				did_boost = False
				for event in app.events:
					if event.type == KEYUP and event.key == K_c:
						# If the charge key was just released, then do a boost
						did_boost = True
						push_vec = push_vec.to_length(self.charge_push)
						obj.body.addForce(push_vec.fake_3d_tuple())
						break
				if not did_boost:
					# If we didn't do a boost, then arrow keys mean cruising
					push_vec = push_vec.to_length(self.cruise_push)
					obj.body.addForce(push_vec.fake_3d_tuple())
			else:
				# Just floating along
				self.sprite.cur_anim = "float"
