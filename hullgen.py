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

def calc_complex_hull(surf):
	"""Returns a sequence of Points defining a (potentially concave) hull around the surface."""
	hull = []
	surf.lock()
	
	# Figure out which pixels are border pixels. Such pixels are:
	# 1. Fairly transparent
	# 2. Next to one edge of the image, or next to another border pixel
	border_pixels = set()
	seen = set()
	for x in range(surf.get_width()):
		for y in range(surf.get_height()):
			pos = (x, y)
			
			if surf.get_at(pos)[3] > MAX_TRANSPARENT_ALPHA:
				continue
			
			if pos in border_pixels:
				continue
			
			edge_touching = False
			queue = set()
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
				for s in seen: border_pixels.add(s)
	
	# Find all the edges that are between a non-transparent pixel and an image border or a border pixel 
	hull_edges = set()
	for x in range(surf.get_width()):
		for y in range(surf.get_height()):
			pos = (x, y)
			
			if surf.get_at(pos)[3] <= MAX_TRANSPARENT_ALPHA:
				continue
			
			for n in ((pos[0]+1, pos[1]), (pos[0]-1, pos[1])):
				if n[0] < 0 or n[0] >= surf.get_width() or n in border_pixels:
					mid = (pos[0]+n[0])/2
					hull_edges.add(Line(Point(mid, n[1]-0.5), Point(mid, n[1]+0.5)))
			for n in ((pos[0], pos[1]+1), (pos[0], pos[1]-1)):
				if n[1] < 0 or n[1] >= surf.get_height() or n in border_pixels:
					mid = (pos[1]+n[1])/2
					hull_edges.add(Line(Point(n[0]-0.5, mid), Point(n[0]+0.5, mid)))
	
	# We're done gathering information from the surface, now we need to organize it
	surf.unlock()

	# Sequence the list of edges into one list of Points that wraps around back to the first one
	first_victim = hull_edges.pop()
	vertices = [first_victim.a, first_victim.b]
	while (len(hull_edges) > 0):
		last = vertices[len(vertices)-1]
		to_remove = None
		for e in hull_edges:
			if last.near_to(e.a):
				to_remove = e
				vertices.append(e.b)
				break
			elif last.near_to(e.b):
				to_remove = e
				vertices.append(e.a)
				break
			
		if to_remove != None:
			hull_edges.remove(to_remove)
		else:
			print "Aborting due to dead-end pixel in complex hull: (%f, %f)" % last
			sys.exit()
	
	first = vertices[0]
	last = vertices[-1]
	if not first.near_to(last):
		print "Aborting due to lack of wraparound in complex hull"
		sys.exit()
	else:
		vertices.pop()
	
	if len(vertices) > 3:
		# Create an approximate hull of lines based on the border pixels
		# We'll do this by subtracting superfluous points from the vertices list
		death_list_five = [] #Indices for points that will be removed
		start = 0
		while start < (len(vertices)-2):
			for end in range(len(vertices)-1, start+1, -1):
				line = Line(vertices[start], vertices[end])
				cullable = True
				for mid in range(start+1, end):
					if line.nearest_pt_to(vertices[mid]).dist_to(vertices[mid]) > MAX_LINE_OFF:
						cullable = False
						break
				if cullable:
					for c in range(start+1, end):
						death_list_five.append(c)
					start = end-1
					break
			start += 1
		
		death_list_five.reverse() # Keeps us from tripping up the numbering of lower-numbered death-listed pixels
		for i in death_list_five:
			del vertices[i]
		
		# The starting and ending points are arbitrary, and will never be 'mid' in the above loop
		# But, they still might be cullable
		if len(vertices) > 4:
			# Check if both first and last are cullable, or just one or the other
			line = Line(vertices[-2],vertices[1])
			if line.nearest_pt_to(vertices[-1]).dist_to(vertices[-1]) <= MAX_LINE_OFF and line.nearest_pt_to(vertices[0]).dist_to(vertices[0]) <= MAX_LINE_OFF:
				del vertices[0]
				del vertices[-1]
			elif Line(vertices[-1], vertices[1]).nearest_pt_to(vertices[0]).dist_to(vertices[0]) <= MAX_LINE_OFF:
				del vertices[0]
			elif Line(vertices[-2], vertices[0]).nearest_pt_to(vertices[-1]).dist_to(vertices[-1]) <= MAX_LINE_OFF:
				del vertices[-1]
	
	# Translate/scale the vertices so that (0, 0) is the center of the image and it has a size of (1, 1)
	w = float(surf.get_width())
	h = float(surf.get_height())
	return ":".join("%s,%s" % ((v[0]+0.5)/w - 0.5, (v[1]+0.5)/h - 0.5) for v in vertices)


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
