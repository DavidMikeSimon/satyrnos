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

avgx1, avgy1, avgx2, avgy2 = 0, 0, 0, 0
maxx1, maxy1, maxx2, maxy2 = 0, 0, 0, 0
minx1, miny1, minx2, miny2 = 9999, 9999, 9999, 9999

app.disp_init()

runs = 1
for i in range(runs):
	app.sim_init()
	
	app.objects.append(gameobj.OImage("ball.png", (0.75, 0.75)))
	#app.objects.append(gameobj.OImage("ball.png"))
	app.objects.append(gameobj.OBlock(colors.red, (0.2, 2.5), (0.1, 5), geom=util.box_geom((0.1, 5))))
	app.objects.append(gameobj.OBlock(colors.green, (2.5, 0.2), (5, 0.1), geom=util.box_geom((5, 0.1))))
	app.objects.append(gameobj.OBlock(colors.yellow, (4.8, 2.5), (0.1, 5), geom=util.box_geom((0.1, 5))))
	app.objects.append(gameobj.OBlock(colors.blue, (2.5, 4.8), (5, 0.1), geom=util.box_geom((5, 0.1))))
	#app.objects.append(gameobj.OBlock(colors.black, (2, 1.5), (0.2, 0.2), geom=util.box_geom((0.2, 0.2))))
	app.objects.append(gameobj.OBlock(colors.purple, (2.5, 2.5), (1.5, 0.2), body=util.sphere_body(1, 0.75), geom=util.box_geom((1.5, 0.2))))
	#app.objects.append(gameobj.OBlock(colors.black, (2, 1.5), (1.5, 0.2), geom=util.box_geom((1.5, 0.2))))
	
	#ballrad = (app.objects[0].img.get_width()-5)/(2.0*app.pixm)
	
	app.objects[0].body = util.sphere_body(1, 0.375)
	app.objects[0].geom = util.sphere_geom(0.375)
	app.objects[0].pos = (0.9, 0.9)
	
	#app.objects[1].body = util.sphere_body(5, ballrad)
	#app.objects[1].geom = util.sphere_geom(ballrad)
	#app.objects[1].pos = (1.4, 1.2)
	
	#app.objects[0].body.addForce((5, 0, 0))
	#app.objects[5].controllers.append(controller.CMagnet(-0.3))
	#app.objects[5].controllers.append(controller.CBoxMagnet(-2, (1.5, 0.2)))
	app.objects[5].controllers.append(controller.CLineMagnet(-1, (0.75, 0)))
	#app.objects[4].controllers.append(controller.CBoxMagnet(-0.2, (5, 0.1)))
	#app.objects[3].controllers.append(controller.CBoxMagnet(-0.03, (0.1, 2.8)))
	app.objects[0].controllers.append(controller.CCameraFollow())
        
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
