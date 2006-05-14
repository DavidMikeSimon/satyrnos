#!/usr/bin/python

import profile

import pygame
import ode
import math

import app
import drive
import gameobj
import colors
import util
import consenv
import magnet
import camera
import background
import image

from geometry import *

avgx1, avgy1, avgx2, avgy2 = 0, 0, 0, 0
maxx1, maxy1, maxx2, maxy2 = 0, 0, 0, 0
minx1, miny1, minx2, miny2 = 9999, 9999, 9999, 9999

app.ui.open()

runs = 1
for i in range(runs):
	app.sim_init()
	
	app.objects.append(gameobj.GameObj(Point(2.5, 2.5)))
	app.objects.append(gameobj.GameObj(Point(0.9, 0.9), util.sphere_body(1, 0.375), util.sphere_geom(0.370)))
	#app.objects.append(gameobj.GameObj((2.5, 2.5), util.sphere_body(1, 0.75), util.box_geom((1.5, 0.2))))
	app.objects.append(gameobj.GameObj(Point(2.5, 2.5), geom=util.box_geom(Size(1.5, 0.08))))
	
	app.objects.append(gameobj.GameObj(Point(2.5, 0), geom=util.box_geom(Size(5, 0.1))))
	app.objects.append(gameobj.GameObj(Point(0, 5), geom=util.box_geom(Size(0.1, 10))))
	app.objects.append(gameobj.GameObj(Point(5, 10), geom=util.box_geom(Size(10, 0.1))))
	app.objects.append(gameobj.GameObj(Point(10, 7.5), geom=util.box_geom(Size(0.1, 5))))
	app.objects.append(gameobj.GameObj(Point(7.5, 5), geom=util.box_geom(Size(5, 0.1))))
	app.objects.append(gameobj.GameObj(Point(5, 2.5), geom=util.box_geom(Size(0.1, 5))))
	
	#app.objects.append(gameobj.GameObj((2.5, 2.5)))
	
	app.objects[0].drives.append(background.DBackground("swirlybg.png", Size(100, 100), Size(2, 2), Point(-0.9, -0.45)))
	app.objects[0].drives.append(background.DBackground("hills.png", Size(100, 100), Size(1.2, 1.2), Point(-0.7, -0.35), (False, True), Point(0, 5)))
	app.objects[1].drives.append(image.DImage("ball.png", Size(0.75, 0.75)))
	app.objects[1].drives.append(camera.DCameraLead(bounds=Rect(Point(5, 5), Size(7, 8))))
	app.objects[2].drives.append(image.DBlock(colors.purple, Size(1.5, 0.08)))
	app.objects[2].drives.append(magnet.DRectMagnet(-0.1, Size(1.5, 0.2), loss=0.04))
	#app.objects[2].drives.append(magnet.DLineMagnet(-0.1, Point(0.75, 0)))
	app.objects[2].ang = 0.3
	
	app.objects[3].drives.append(image.DBlock(colors.red, app.objects[3].geom.size))
	app.objects[4].drives.append(image.DBlock(colors.red, app.objects[4].geom.size))
	app.objects[5].drives.append(image.DBlock(colors.red, app.objects[5].geom.size))
	app.objects[6].drives.append(image.DBlock(colors.red, app.objects[6].geom.size))
	app.objects[7].drives.append(image.DBlock(colors.red, app.objects[7].geom.size))
	app.objects[8].drives.append(image.DBlock(colors.red, app.objects[8].geom.size))
	
	#app.objects[9].drives.append(image.DWireBlock(colors.black, app.objects[1].drives[1].bounds[1]))
	
	#consenv.wset(0, "'%5.8f -- %5.8f' % (app.wanted_offset[0], app.wanted_offset[1])")
	#consenv.wset(1, "'%5.8f -- %5.8f' % (app.objvel[0], app.objvel[1])")

	#app.objects[1].body.addForce((150, 150, 0))
	
	#profile.run('app.run()', 'satyrprof')
	app.run()
	
	x1 = app.objects[1].pos[0]
	y1 = app.objects[1].pos[1]
	x2 = app.objects[5].pos[0]
	y2 = app.objects[5].pos[1]
	
	print "%8d : %.5f %.5f      %.5f %.5f     %.5f Revs" % (i, x1, y1, x2, y2, app.objects[1].ang)
	
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
