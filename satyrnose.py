#!/usr/bin/python

import profile

import pygame
import ode
import math

import app
import gameobj
import colors
import util
import controller
import pen
import consenv

avgx1, avgy1, avgx2, avgy2 = 0, 0, 0, 0
maxx1, maxy1, maxx2, maxy2 = 0, 0, 0, 0
minx1, miny1, minx2, miny2 = 9999, 9999, 9999, 9999

app.disp_init()

runs = 1
for i in range(runs):
	app.sim_init()
	
	app.objects.append(gameobj.GameObj((4, 4.2)))
	app.objects.append(gameobj.GameObj((0.9, 0.9), util.sphere_body(1, 0.375), util.sphere_geom(0.370)))
	app.objects.append(gameobj.GameObj((0.2, 2.5), geom=util.box_geom((0.1, 5))))
	app.objects.append(gameobj.GameObj((2.5, 0.2), geom=util.box_geom((5, 0.1))))
	app.objects.append(gameobj.GameObj((4.8, 2.5), geom=util.box_geom((0.1, 5))))
	app.objects.append(gameobj.GameObj((2.5, 4.8), geom=util.box_geom((5, 0.1))))
	#app.objects.append(gameobj.GameObj((2.5, 2.5), util.sphere_body(1, 0.75), util.box_geom((1.5, 0.2))))
	app.objects.append(gameobj.GameObj((2.5, 2.5), geom=util.box_geom((1.5, 0.2))))
	
	app.objects[0].pens.append(pen.PBackground("swirlybg.png", (100, 100), (2, 2), (-0.9, -0.45)))
	app.objects[0].pens.append(pen.PBackground("hills.png", (100, 100), (1.2, 1.2), (-0.7, -0.35), (False, True)))
	app.objects[1].pens.append(pen.PImage("ball.png", (0.75, 0.75)))
	app.objects[2].pens.append(pen.PBlock(colors.red, (0.1, 5)))
	app.objects[3].pens.append(pen.PBlock(colors.green, (5, 0.1)))
	app.objects[4].pens.append(pen.PBlock(colors.yellow, (0.1, 5)))
	app.objects[5].pens.append(pen.PBlock(colors.blue, (5, 0.1)))
	app.objects[6].pens.append(pen.PBlock(colors.purple, (1.5, 0.2)))
	app.objects[6].ang = 0.3
	
	app.objects[1].controllers.append(controller.CCameraFollow())
	app.objects[6].controllers.append(controller.CBoxMagnet(-0.1, (1.5, 0.2)))
	
	#app.objects[0].body.addForce((150, 150, 0))
	
	#profile.run('app.run()', 'satyrprof')
	app.run()
	
	x1 = app.objects[0].pos[0]
	y1 = app.objects[0].pos[1]
	x2 = app.objects[5].pos[0]
	y2 = app.objects[5].pos[1]
	
	print "%8d : %.5f %.5f      %.5f %.5f     %.5f Revs" % (i, x1, y1, x2, y2, app.objects[0].ang)
	
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

app.disp_deinit()
