#!/usr/bin/python

import pygame
import math
import os
import sre
import sys

import app
import drive
import gameobj
import hull
import colors
import consenv
import magnet
import joints
import camera
import background
import image
import collision
import sprite
import light

from geometry import *
from util import *

MAX_TRANSPARENT_ALPHA = 25 #Out of 255
MAX_LINE_OFF = 0.5 #In pixels

def calc_radius(surf):
	"""Returns the radius for a spherical hull of a surface (farthest pixel from center with an alpha over 10%)."""
	surf.lock()
	center = Point(float(surf.get_width()-1)/2, float(surf.get_height()-1)/2)
	cand_pos = Point(0, 0)
	cand_dist = 0
	for x in range(surf.get_width()):
		for y in range(surf.get_height()):
			pos = Point(x, y)
			dist = pos.dist_to(center)
			if dist > cand_dist and surf.get_at((x, y))[3] > MAX_TRANSPARENT_ALPHA:
				cand_pos = pos
				cand_dist = dist
	surf.unlock()
	return cand_dist

def calc_complex_hull(surf):
	"""Returns a sequence of Points defining a (potentially concave) hull around the surface."""
	hull = []
	surf.lock()
	
	# Find all the regions of transparent pixels (we'll only care later about ones that touch the edge)
	outer_clear_pixels = set()
	inner_clear_pixels = set()
	for x in range(surf.get_width()):
		for y in range(surf.get_height()):
			pos = (x, y)
			
			if surf.get_at(pos)[3] > MAX_TRANSPARENT_ALPHA:
				continue
			
			if pos in outer_clear_pixels or pos in inner_clear_pixels:
				continue
			
			edge_touching = False
			queue = set()
			seen = set()
			queue.add(pos)
			while len(queue) > 0:
				q = queue.pop()
				for n in ((q[0]+1, q[1]), (q[0]-1, q[1]), (q[0], q[1]+1), (q[0], q[1]-1)):
					if n[0] < 0 or n[0] >= surf.get_width() or n[1] < 0 or n[1] >= surf.get_height():
						edge_touching = True
					elif surf.get_at(n)[3] <= MAX_TRANSPARENT_ALPHA and n not in queue and n not in seen:
						queue.add(n)
				seen.add(q)
			
			if edge_touching:
				for s in seen: outer_clear_pixels.add(s)
			else:
				for s in seen: inner_clear_pixels.add(s)
	
	# Find all the non-transparent pixels that are next to either an image border or an image-border touching transparent region
	border_pixels = set()
	for x in range(surf.get_width()):
		for y in range(surf.get_height()):
			pos = (x, y)
			
			if surf.get_at(pos)[3] <= MAX_TRANSPARENT_ALPHA:
				continue
			
			for n in ((pos[0]+1, pos[1]), (pos[0]-1, pos[1]), (pos[0], pos[1]+1), (pos[0], pos[1]-1)):
				if n[0] < 0 or n[0] >= surf.get_width() or n[1] < 0 or n[1] >= surf.get_height() or n in outer_clear_pixels:
					border_pixels.add(pos)
	
	# We're done gathering information from the surface, now we need to organize it
	surf.unlock()
	
	def are_neighbors(a, b):
		return abs(a[0] - b[0]) <= 1 and abs(a[1] - b[1]) <= 1
	
	# Sequence the pixels into one list of Points that wraps around back to the first one
	# Complain and die if it doesn't work
	# TODO: One-pixel warts will often break this, and two pixel warts will break this every time
	first_victim = border_pixels.pop()
	vertices = [Point(first_victim[0], first_victim[1])]
	while (len(border_pixels) > 0):
		last = vertices[len(vertices)-1]
		next = None
		for p in border_pixels:
			if are_neighbors(p, last):
				next = p
				break

		if next != None:
			vertices.append(Point(next[0], next[1]))
			border_pixels.remove(next)
		else:
			print "Aborting due to pixel ordering error in complex hull: Dead-end pixel (%i, %i)" % last
			sys.exit()
	
	first = vertices[0]
	last = vertices[len(vertices)-1]
	if not are_neighbors(first, last):
		print "Aborting due to pixel ordering error in complex hull: No wraparound"
		sys.exit()
	
	# Create an approximate hull of lines based on the border pixels
	# We'll do this by subtracting superfluous points from the vertices list
	death_list_five = [] #Pixels that will be removed from the vertices list later
	next_idx = 0
	for n in range(0, len(vertices)-2):
		if n < next_idx: continue
		here = vertices[n]
		f = n+1 #End-point for a line starting at 'here'
		while f < len(vertices)-1:
			s = Line(vertices[n], vertices[f])
			too_far = False
			for p in range(n, f):
				if s.nearest_pt_to(vertices[p]).dist_to(vertices[p]) > MAX_LINE_OFF:
					too_far = True
					break
			if too_far:
				break
			f = f+1
		
		next_idx = f
		if f - n > 1:
			for x in range(n+1, f):
				death_list_five.append(x)
	
	# Since the starting point is arbitrary, it's quite possible that it's deletable
	#first = vertices[0]
	#second = vertices[1]
	#last = vertices[len(vertices)-1]
	#if abs(last.ang_to(first) - last.ang_to(second)) < MAX_SMOOTHING_ANGLE:
	#	death_list_five.insert(0, 0)
	
	death_list_five.reverse() # Keeps us from tripping up the numbering of lower-numbered death-listed pixels
	for t in death_list_five:
		del vertices[t]

	# Translate/scale the vertices so that (0, 0) is the center of the image and it has a size of (1, 1)
	w = float(surf.get_width())
	h = float(surf.get_height())
	return ":".join("%s,%s" % (v[0]/w - 0.5, v[1]/h - 0.5) for v in vertices)


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
	geom=hull.load_image_hull("splat.png", Size(3, 3)).make_geom(),
	drives=[image.DImage("splat.png", Size(3, 3))]))

# Invisible camera object
app.objects[3].append(gameobj.GameObj(
	Point(0, 0),
	body=sphere_body(1, 0.5),
	drives=[camera.DCameraDirect()]))

app.run()

app.sim_deinit()
app.ui.close()
