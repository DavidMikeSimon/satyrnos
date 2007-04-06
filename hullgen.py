#!/usr/bin/python

from __future__ import division
import pygame
import math
import os
import sre
import sys

import app
import gameobj
import hull
import image
import camera

from geometry import *
from util import *


def calc_radius(surf):



def gen_hull(surf, mode):
	"""Creates a string representing the hull of a surface, using the given mode.

	Mode is one of:
		sphere -- Creates a circle around the non-transparent pixels, potentially going over transparent pixels
		minsphere -- Creates the largest possible circle that doesn't contain any transparent pixels
		full -- Creates a box around the entire image
		complex -- Creates a series of lines around the non-transparent pixels
	"""
	
	if mode == "circle":
		if surf.get_width() != surf.get_height():
			raise RuntimeError("Cannot calculate circle hull for weirdly sized image")
		return "circle:%s" % (calc_radius(surf)/surf.get_width())
	elif mode == "full":
		return "box:1.0:1.0"
	else:
		return "%s:%s" % (mode, calc_complex_hull(surf))

app.ui.open() #Initializes PyGame, among other things
app.ui.draw_hulls = True

hull_algos = {}
hullinfo = open(os.path.join("hulls", "hullinfo"))
for line in hullinfo:
	matches = sre.match(r"(.+):(.+)", line)
	if matches:
		hull_algos[matches.group(1)] = matches.group(2)
hullinfo.close()

imgs = os.listdir("imgs")
for imgfn in imgs:
	if hull_algos.has_key(imgfn):
		hullfn = os.path.join("hulls", "%s.hull" % imgfn)
		# Recreate the hull if it doesn't exist or is older than the source image
		if (not os.access(hullfn, os.F_OK)) or (os.stat(hullfn).st_mtime < os.stat(os.path.join("imgs", imgfn)).st_mtime):
			print "Generating hull for %s" % imgfn
			surf = pygame.image.load(os.path.join("imgs", imgfn))
			str = gen_hull(surf, hull_algos[imgfn])
			hullf = open(hullfn, "w")
			hullf.write(str)
			hullf.close()

app.sim_init()

for x in range(7):
	app.objects.append(TrackerList())

app.objects[2].append(gameobj.GameObj(
	Point(0.5, 0.5),
	geom=hull.load_image_hull("splat.png", Size(5, 5)).make_geom(),
	drives=[image.DImage("splat.png", Size(5, 5))]))

# Invisible camera object
app.objects[3].append(gameobj.GameObj(
	Point(0, 0),
	body=sphere_body(1, 0.5),
	drives=[camera.DCameraDirect()]))

app.run()

app.sim_deinit()
app.ui.close()
