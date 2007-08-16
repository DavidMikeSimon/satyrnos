from __future__ import division
import sys,math
from pygame.locals import *

import app, colors, drive, sprite, image, util
from geometry import *

class DAvatar(drive.Drive):
	"""Drive that controls/draws the main character.
	
	This drive does not control the camera; use the drives in camera.py for that.
	
	Data attributes:
	sprite -- The sprite being used to draw Satyrn himself at the moment.
		This is also used to figure out some parts of Satyrn's current state.
	field_boost -- Sprite used for the field that appears when Satyrn uses
		the lantern to move around.
	field_attack -- SPrite used for the field that appears when Satyrn
		attacks stuff with the lantern.
	lantern -- Sprite used for lantern drawn behind Satyrn. Its offset
		is from the center of the Satyrn sprite/object.
	lantern_rot_speed -- How fast (in revolutions per second) the lantern
		can move around Satyrn to the player-desired position.
	lantern_rad -- Radius of the circle that lantern moves around.
	lantern_ang -- Current angle of the lantern from Satyrn, controlled by player.
	attack_rot_speed -- How fast (in revs per second) the attack angle changes
		when the player pushes a direction during an attack. This is also the
		speed at which Satyrn's orientation can be manually changed while the
		attack field is turned on.
	cruise_push -- How hard to push when cruising.
	boost_push_1 -- How hard to push during the initial pulse of a boost.
	boost_push_2 -- How hard to push during when player continues holding down the boost button.
	boost_max_speed -- The maximum linear speed (in terms of body.getLinearVel) that
		Satyrn can reach while boosting.
	stall_speed_diff -- The maximum amount of linear speed that Satyrn can lose per
		second while stalling.
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
				"float-cruise":image.DImage("satyrn/float-cruise.png", Size(1.0, 1.0)),
				"float-daze":image.DImage("satyrn/float-daze.png", Size(1.0, 1.0)),
				"float-flip":image.DImage("satyrn/float-flip.png", Size(1.0, 1.0)),
				"float-ow":image.DImage("satyrn/float-ow.png", Size(1.0, 1.0)),
				"float":image.DImage("satyrn/float.png", Size(1.0, 1.0)),
				"float-rotate":image.DImage("satyrn/float-rotate.png", Size(1.0, 1.0)),
				"float-zflip":image.DImage("satyrn/float-zflip.png", Size(1.0, 1.0)),
				"stand-boost":image.DImage("satyrn/stand-boost.png", Size(1.0, 1.0)),
				"stand-flip":image.DImage("satyrn/stand-flip.png", Size(1.0, 1.0)),
				"stand-move":image.DImage("satyrn/stand-move.png", Size(1.0, 1.0)),
				"stand":image.DImage("satyrn/stand.png", Size(1.0, 1.0)),
				"stand-to-crouch":image.DImage("satyrn/stand-to-crouch.png", Size(1.0, 1.0)),
			}, {
				"crouch-flip":sprite.DSprite.Anim([("crouch-flip", 100)], "REPEAT"),
				"crouch-move":sprite.DSprite.Anim([("crouch-move", 100)], "REPEAT"),
				"crouch":sprite.DSprite.Anim([("crouch", 100)], "REPEAT"),
				"crouch-to-stand":sprite.DSprite.Anim([("crouch-to-stand", 100)], "REPEAT"),
				"float-boost":sprite.DSprite.Anim([("float-boost", 350)], "REPEAT"),
				"float-cruise":sprite.DSprite.Anim([("float-cruise", 350)], "REPEAT"),
				"float-daze":sprite.DSprite.Anim([("float-daze", 100)], "REPEAT"),
				"float-flip":sprite.DSprite.Anim([("float-flip", 100)], "REPEAT"),
				"float-ow":sprite.DSprite.Anim([("float-ow", 100)], "REPEAT"),
				"float":sprite.DSprite.Anim([("float", 100)], "REPEAT"),
				"float-rotate":sprite.DSprite.Anim([("float-rotate", 100)], "REPEAT"),
				"float-zflip":sprite.DSprite.Anim([("float-zflip", 100)], "REPEAT"),
				"stand-boost":sprite.DSprite.Anim([("stand-boost", 100)], "REPEAT"),
				"stand-flip":sprite.DSprite.Anim([("stand-flip", 100)], "REPEAT"),
				"stand-move":sprite.DSprite.Anim([("stand-move", 100)], "REPEAT"),
				"stand":sprite.DSprite.Anim([("stand", 100)], "REPEAT"),
				"stand-to-crouch":sprite.DSprite.Anim([("stand-to-crouch", 100)], "REPEAT"),
			}
		)
		self.field_attack = sprite.DSprite("null",
			{
				"null":drive.Drive(),
				"field-attack-1":image.DImage("satyrn/field-attack-1.png", Size(2.0, 2.0)),
				"field-attack-2":image.DImage("satyrn/field-attack-2.png", Size(2.0, 2.0)),
			}, {
				"null":sprite.DSprite.Anim([("null", 100)], "REPEAT"),
				"field-attack-1":sprite.DSprite.Anim([("field-attack-1", 300)], "field-attack-2"),
				"field-attack-2":sprite.DSprite.Anim([("field-attack-2", 100)], "REPEAT"),
			}
		)
		self.field_boost = sprite.DSprite("null",
			{
				"null":drive.Drive(),
				"field-boost-1":image.DImage("satyrn/field-boost-1.png", Size(1.0, 1.0)),
				"field-boost-2":image.DImage("satyrn/field-boost-2.png", Size(1.0, 1.0)),
			}, {
				"null":sprite.DSprite.Anim([("null", 100)], "REPEAT"),
				"field-boost-1":sprite.DSprite.Anim([("field-boost-1", 200)], "field-boost-2"),
				"field-boost-2":sprite.DSprite.Anim([("field-boost-2", 100)], "REPEAT"),
			}
		)
		self.lantern = sprite.DSprite("lantern",
			{
				"lantern":image.DImage("satyrn/lantern.png", Size(0.25, 0.25)),
			}, {
				"lantern":sprite.DSprite.Anim([("lantern", 100)], "REPEAT"),
			}
		)
		self.lantern_rot_speed = 3
		self.lantern_rad = 0.3
		self.lantern_ang = 0.5
		self.attack_rot_speed = 3
		self.cruise_push = 0.5
		self.boost_push_1 = 1.5
		self.boost_push_2 = 0.7
		self.boost_max_speed = 5
		self.stall_speed_diff = 5
	
	def _draw(self, obj):
		self.lantern.offset = Point(self.lantern_rad, 0).rot(Point(0,0), self.lantern_ang-obj.ang)
		self.lantern.draw(obj)
		self.sprite.draw(obj)
		self.field_boost.rot_offset = self.lantern_ang-obj.ang
		self.field_boost.draw(obj)
		self.field_attack.draw(obj)
	
	def _step(self, obj):
		# Add strong angular drag; Satyrn has a tendency to make himself stop rotating
		angVel = obj.body.getAngularVel()[2]
		obj.body.addTorque((0, 0, -angVel/4))
		
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
		
		# Turn on the attack animation if they're holding down the sword key
		if app.keys[K_v]:
			if self.field_attack.cur_anim == "null":
				self.field_attack.cur_anim = "field-attack-1"
		elif self.field_attack.cur_anim == "field-attack-2":
			self.field_attack.cur_anim = "null"

		# Turn on the boost animation if they're holding down the boost key
		if app.keys[K_b]:
			if self.field_boost.cur_anim == "null":
				self.field_boost.cur_anim = "field-boost-1"
		elif self.field_boost.cur_anim == "field-boost-2":
			self.field_boost.cur_anim = "null"
		
		if self.field_boost.cur_anim != "null":
			self.sprite.cur_anim = "float-boost"
		
		# Figure out how hard we would move this step, based on what stage of boosting the player is in
		bpush = self.cruise_push
		if self.field_boost.cur_anim == "field-boost-1":
			bpush = self.boost_push_1
		elif self.field_boost.cur_anim == "field-boost-2":
			bpush = self.boost_push_2
		
		# This will be the angle that the lantern moves towards, relative to Satyrn
		# By default, until the player hits a button, the lantern just wants to be where it is
		des_lantern_ang = self.lantern_ang
		
		# Rotate the lantern around towards the opposite side of where the player is pressing
		# That's because, conceptually, the player should think of the lantern as pushing Satyrn
		if push_vec[0] != 0 or push_vec[1] != 0:
			des_lantern_ang = Point(0,0).ang_to(-push_vec)
		
		if self.field_attack.cur_anim != "null":	
			# When an attack field is up, orient Satyrn (and also, the sword) to face away from the lantern
			obj.ang += util.cap_ang_diff(util.min_ang_diff(obj.ang, des_lantern_ang + 0.5), self.attack_rot_speed/app.maxfps)
			
			# Holding down the attack field means killing rotation and slowing/killing linear velocity
			obj.body.setAngularVel((0,0,0))
			vel_diff = -obj.vel
			if Point(0,0).dist_to(obj.vel) > self.stall_speed_diff/app.maxfps:
				obj.vel = obj.vel - Point(self.stall_speed_diff/app.maxfps,0).rot(Point(0,0), Point(0,0).ang_to(obj.vel))
			else:
				obj.vel = Point(0,0)
		
		# If player is not attacking, but is pushing the boost button and/or holding a direction, move Satyrn
		# Either way, set his animation to be appropriate to his movement/non-movement
		if self.field_attack.cur_anim == "null" and (push_vec[0] != 0 or push_vec[1] != 0 or self.field_boost.cur_anim != "null"):
			if self.field_boost.cur_anim == "null":
				self.sprite.cur_anim = "float-cruise"
			
			obj.body.addForce(Point(bpush,0).rot(Point(0,0), des_lantern_ang+0.5).fake_3d_tuple())
		elif self.field_boost.cur_anim == "null":
			self.sprite.cur_anim = "float"
		
		# Move the lantern towards the pressed direction
		self.lantern_ang += util.cap_ang_diff(util.min_ang_diff(self.lantern_ang, des_lantern_ang), self.lantern_rot_speed/app.maxfps)
