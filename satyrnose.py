#!/usr/bin/python

import profile

import pygame
import ode
import math

import app
import drive
import gameobj
import colors
import consenv
import magnet
import joints
import camera
import background
import image
import collision

from geometry import *
from util import *

avgx1, avgy1, avgx2, avgy2 = 0, 0, 0, 0
maxx1, maxy1, maxx2, maxy2 = 0, 0, 0, 0
minx1, miny1, minx2, miny2 = 9999, 9999, 9999, 9999

app.ui.open()

runs = 1
for i in range(runs):
	app.sim_init()

	app.objects.append(TrackerList())
	app.objects[0].append(gameobj.GameObj(Point(0, -6)))
	app.objects[0][0].drives.append(background.DTiledBg("swirlybg.png", Size(100, 100), Size(2, 2), Point(-0.9, -0.9)))
	app.objects[0][0].drives.append(background.DTiledBg("hills_dan.png", Size(100, 100), Size(4, 2), Point(-0.7, -0.7), (False, True), Point(0, 5)))
	
	app.objects.append(TrackerList())
	
	app.objects[1].append(gameobj.GameObj(Point(2.5, 0), geom=box_geom(Size(5, 0.1), app.static_space)))
	app.objects[1].append(gameobj.GameObj(Point(0, 5), 0.25, geom=box_geom(Size(10, 0.1), app.static_space)))
	app.objects[1].append(gameobj.GameObj(Point(5, 10), geom=box_geom(Size(10, 0.1), app.static_space)))
	app.objects[1].append(gameobj.GameObj(Point(10, 7.5), 0.25, geom=box_geom(Size(5, 0.1), app.static_space)))
	app.objects[1].append(gameobj.GameObj(Point(7.5, 5), geom=box_geom(Size(5, 0.1), app.static_space)))
	app.objects[1].append(gameobj.GameObj(Point(5, 2.5), 0.25, geom=box_geom(Size(5, 0.1), app.static_space)))
	
	app.objects[1][0].drives.append(image.DTiledImage("pattern.png", app.objects[1][0].geom.size, Size(1, 0.25)))
	app.objects[1][1].drives.append(image.DTiledImage("pattern.png", app.objects[1][1].geom.size, Size(1, 0.25)))
	app.objects[1][2].drives.append(image.DTiledImage("pattern.png", app.objects[1][2].geom.size, Size(1, 0.25)))
	app.objects[1][3].drives.append(image.DTiledImage("pattern.png", app.objects[1][3].geom.size, Size(1, 0.25)))
	app.objects[1][4].drives.append(image.DTiledImage("pattern.png", app.objects[1][4].geom.size, Size(1, 0.25)))
	app.objects[1][5].drives.append(image.DTiledImage("pattern.png", app.objects[1][5].geom.size, Size(1, 0.25)))
	
	app.objects[1].append(gameobj.GameObj(
		Point(1, 0.8), 
		geom=sphere_geom(0.370, app.static_space),
		drives=[image.DImage("redball.png", Size(0.75, 0.75))]))
	
	app.objects[1].append(gameobj.GameObj(
		Point(1, 2), 0.2,
		geom=sphere_geom(0.74, app.static_space),
		drives=[image.DImage("redball.png", Size(1.5, 1.5))]))
	
	app.objects[1].append(gameobj.GameObj(
		Point(3.75, 3), 0.7,
		geom=sphere_geom(0.370, app.static_space),
		drives=[image.DImage("redball.png", Size(0.75, 0.75))]))
	
	app.objects[1].append(gameobj.GameObj(
		Point(1, 3.7), 0.02,
		geom=sphere_geom(0.74, app.static_space),
		drives=[image.DImage("redball.png", Size(1.5, 1.5))]))
	
	app.objects[1].append(gameobj.GameObj(
		Point(1.5, 5.5), 0.9,
		geom=sphere_geom(0.370, app.static_space),
		drives=[image.DImage("redball.png", Size(0.75, 0.75))]))
	
	app.objects[1].append(gameobj.GameObj(
		Point(1.7, 7), 0.25,
		geom=sphere_geom(0.74, app.static_space),
		drives=[image.DImage("redball.png", Size(1.5, 1.5))]))
	
	app.objects[1].append(gameobj.GameObj(
		Point(2.5, 9),
		geom=sphere_geom(0.185, app.static_space),
		drives=[image.DImage("redball.png", Size(0.375, 0.375))]))
	
	app.objects[1].append(gameobj.GameObj(
		Point(5.6, 6.7), 0.5,
		geom=sphere_geom(0.74, app.static_space),
		drives=[image.DImage("redball.png", Size(1.5, 1.5))]))
	
	app.objects[1].append(gameobj.GameObj(
		Point(7.5, 8.7), 0.97,
		geom=sphere_geom(0.370, app.static_space),
		drives=[image.DImage("redball.png", Size(0.75, 0.75))]))
	
	app.objects[1].append(gameobj.GameObj(
		Point(8.2, 6.3),
		geom=sphere_geom(0.74, app.static_space),
		drives=[image.DImage("redball.png", Size(1.5, 1.5))]))
	
	app.objects.append(TrackerList())
	
	app.objects[2].append(gameobj.GameObj(Point(2.5, 2.5), 0, sphere_body(1, 0.75), box_geom(Size(1.5, 0.08))))
	#app.objects[2].append(gameobj.GameObj(Point(2.5, 2.5), geom=box_geom(Size(1.5, 0.08))))
	app.objects[2][0].drives.append(image.DBlock(colors.purple, Size(1.5, 0.08)))
	#app.objects[2][0].drives.append(magnet.DRectMagnet(-0.1, Size(1.5, 0.2), loss=0.06))
	#app.objects[2][0].drives.append(magnet.DLineMagnet(-0.1, Point(0.75, 0)))
	app.objects[2][0].ang = 0.3
	app.objects[2][0].drives.append(joints.DEnvJoint(util.anchored_joint(ode.BallJoint, app.objects[2][0])))
	
	app.objects[2].append(gameobj.LimbedGameObj(body = sphere_body(1, 0.375)))
	app.objects[2][1].geom = box_geom(Size(0.2, 0.5), app.objects[2][1].space)
	app.objects[2][1].pos = Point(4.5, 9)
	app.objects[2][1].add_limb(gameobj.GameObj(
		Point(4.5, 9.4),
		body=sphere_body(1, 0.6),
		geom=box_geom(Size(0.5, 0.5), app.objects[2][1].space),
		drives=[image.DImage("left.png", Size(0.5, 0.5))])
	, Point(0, -0.2))
	app.objects[2][1].drives.append(image.DBlock(colors.gray, Size(0.2, 0.5)))
	
	app.objects.append(TrackerList())
	
	
	app.objects[3].append(gameobj.GameObj(
		Point(2.5, 1),
		body=sphere_body(1, 0.375),
		geom=sphere_geom(0.37),
		drives=[image.DImage("ball.png", Size(0.75, 0.75))]))
	#app.objects[3][0].drives.append(camera.DCameraLead(bounds=Rect(Point(5, 5), Size(7, 8))))
	app.objects[3][0].drives.append(camera.DCameraDirect())
	
	app.objects.append(TrackerList())
	app.objects.append(TrackerList())
	
	
	#profile.run('app.run()', 'satyrprof')
	app.run()
	
	x1 = app.objects[3][0].pos[0]
	y1 = app.objects[3][0].pos[1]
	x2 = app.objects[2][0].pos[0]
	y2 = app.objects[2][0].pos[1]
	
	print "%8d : %.5f %.5f      %.5f %.5f     %.5f Revs" % (i, x1, y1, x2, y2, app.objects[3][0].ang)
	
	maxx1 = max(x1, maxx1)
	maxy1 = max(y1, maxy1)
	maxx2 = max(x2, maxx2)
	maxy2 = max(y2, maxy2)
	
	minx1 = min(x1, minx1)
	miny1 = min(y1, miny1)
	minx2 = min(x2, minx2)
	miny2 = min(y2, miny2)
	
	avgx1 += x1
	avgy1 += y1
	avgx2 += x2
	avgy2 += y2

	app.sim_deinit()

avgx1 /= runs
avgy1 /= runs
avgx2 /= runs
avgy2 /= runs

print "MAX: %.5f %.5f   %.5f %.5f" % (maxx1, maxy1, maxx2, maxy2)
print "AVG: %.5f %.5f   %.5f %.5f" % (avgx1, avgy1, avgx2, avgy2)
print "MIN: %.5f %.5f   %.5f %.5f" % (minx1, miny1, minx2, miny2)

app.ui.close()
