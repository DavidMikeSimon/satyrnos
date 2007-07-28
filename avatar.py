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
	lantern -- Sprite used for lantern drawn behind Satyrn. Its offset
		is from the center of the Satyrn sprite/object.
	lantern_rot_speed -- How fast (in revolutions per second) the lantern
		can move around Satyrn to the player-desired position. Purely
		visual; lantern's actual position changes instantaneously.
	lantern_rad -- Radius of the circle that lantern moves around.
	lantern_ang -- Current angle of the lantern from Satyrn, controlled by player.
	boost_push -- How hard to push when boosting.
	boost_max_speed -- The maximum linear speed (in terms of body.getLinearVel) that
		Satyrn can reach while boosting.
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
				"float-cruise":image.DImage("satyrn/float-cruise.png", Size(1.0, 1.0)),
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
				"float-boost":sprite.DSprite.Anim([("float-boost", 350)], "float"),
				"float-charge-buffer":sprite.DSprite.Anim([("float", 100)], "float-charge"),
				"float-charge":sprite.DSprite.Anim([("float-charge", 100)], "REPEAT"),
				"float-cruise":sprite.DSprite.Anim([("float-cruise", 200)], "float"),
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
		self.lantern = sprite.DSprite("lantern",
			{
				"lantern":image.DImage("satyrn/lantern.png", Size(0.25, 0.25)),
			}, {
				"lantern":sprite.DSprite.Anim([("lantern", 100)], "REPEAT"),
			}
		)
		self.lantern_rot_speed = 2
		self.lantern_rad = 0.3
		self.lantern_ang = 0.5
		self.boost_push = 1
		self.boost_max_speed = 5
	
	def _draw(self, obj):
		self.lantern.offset = Point(self.lantern_rad, 0).rot(Point(0,0), self.lantern_ang-obj.ang)
		self.lantern.draw(obj)
		self.sprite.draw(obj)
	
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
		
		# This will be the angle that the lantern moves towards, relative to Satyrn
		# By default, until the player hits a button, the lantern just wants to be where it is
		des_angle = self.lantern_ang
		
		cur_vel = Point(obj.body.getLinearVel()[0], obj.body.getLinearVel()[1])
		cur_speed = Point(0,0).dist_to(cur_vel)
		if push_vec[0] != 0 or push_vec[1] != 0:
			# Rotate the lantern around towards the opposite side of where the player is pressing
			# That's because, conceptually, the player should think of the lantern as pushing Satyrn
			des_angle = Point(0,0).ang_to(-push_vec)
			if app.keys[K_b]:
				self.sprite.cur_anim = "float-boost"
				obj.body.addForce(Point(self.boost_push,0).rot(Point(0,0), self.lantern_ang+0.5).fake_3d_tuple())
			else:
				self.sprite.cur_anim = "float"
		elif app.keys[K_b] and cur_speed > 0.0001:
			# If boosting, but not holding a direction, point the lantern into heading, so that Satyrn stalls
			# Only start stalling if lantern is actually facing in the right direction
			des_angle = Point(0,0).ang_to(cur_vel)
			if abs(des_angle%1-self.lantern_ang%1) < 0.001:
				# If this step of stalling would cause Satyrn to reverse direction, just cheat and set velocity to 0
				self.sprite.cur_anim = "float-boost"
				if Point(0,0).dist_to(cur_vel) > self.boost_push/(obj.body.getMass().mass*app.maxfps):
					obj.body.addForce(Point(self.boost_push,0).rot(Point(0,0), self.lantern_ang+0.5).fake_3d_tuple())
				else:
					obj.body.setLinearVel((0,0,0))
			else:
				self.sprite.cur_anim = "float"
		
		# Move the lantern towards the pressed direction
		dist = (des_angle - self.lantern_ang) % 1
		if 1-dist < dist:
			dist = -(1-dist)
		if abs(dist) > self.lantern_rot_speed/app.maxfps:
			dir = 1
			if dist < 0:
				dir = -1
			dist = dir * self.lantern_rot_speed/app.maxfps
		self.lantern_ang += dist
		
		# Figure out if the player just released the boost key
		#boost_released = False
		#for event in app.events:
		#	if event.type == KEYUP and event.key == K_b:
		#		# If the charge key was just released, then do a boost
		#		boost_released = True
		#		break
