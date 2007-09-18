from __future__ import division

import pygame, math, os, ode, cPickle, sys
from OpenGL.GL import *

import app, image, collision, colors
from geometry import *

# Constants used in mold generation
MAX_TRANSPARENT_ALPHA = 25 #Out of 255, the maximum alpha value of a pixel before it's not transparent
MAX_LINE_OFF = 0.8 #In pixels, how far a pixel can be away from a line before it's not "on" that line

def _save_cache(cache_name, obj):
	"""Pickles an object and saves it under a unique name. Used for caching calculations from
	time-consuming mold-generation routines like ComplexGeomMold."""
	
	cachepath = os.path.join("moldcache", cache_name + ".cache")
	cachef = open(cachepath, "w")
	cPickle.dump(obj, cachef)
	cachef.close()


def _load_cache(cache_name, img):
	"""Loads a cached object saved with _save_cache and returns it, unless the named image has a
	more recent modification than the cache file, or the cache file doesn't exist, in which case
	None is returned."""
	
	cachepath = os.path.join("moldcache", cache_name + ".cache")
	imgpath = os.path.join("imgs", img)
	
	if os.access(cachepath, os.F_OK):
		c_mtime = os.stat(cachepath).st_mtime
		if c_mtime > os.stat(imgpath).st_mtime:
			cachef = open(cachepath, "r")
			cache = cPickle.load(cachef)
			cachef.close()
			return cache
	
	return None


class GeomMold:
	"""Describes how to create an ODE geom.
	
	This class is only to describe the interfaces that all the actual GeomMold types have.
	Once you've created a GeomMold object, use its make_geom() method to create an ODE geom
	with various special members set. Many parts of Satyrnos expect that collision geoms
	have these members, so it's important to always create geoms using the make_geom() method,
	instead of by calling the ODE geom constructors directly.
	"""

	def make_geom(self, size, space = None, coll_props = -1):
		"""Returns an ODE geom in the given space based on this mold.
		
		It will have the following special members set:
		mold - The GeomMold that created it
		coll_props - The collision properties for the geom
		draw_drive - A Drive that can be used to draw an outline of the geom
		geom_args - The arguments (other than self) that were passed to make_geom to create the geom
		
		If no space is specified, app.dyn_space will be used by default.
		If no coll_props is specified, it will make a new collision.Props
		with its default constructor. To disable collision, pass None
		as the coll_props value."""
		return None
	

class CircleGeomMold(GeomMold):
	"""Creates a circular mold around an image for an ODE sphere geom.
	
	The size of the mold is always normalized to assume the image is 1x1 game meters.
	If you don't specify an image, then the size of the mold is exactly 1 game meter
	in diameter."""
	
	def __init__(self, img = None):
		if img == None:
			self.radius = 0.5
			return
		
		cache_name = "CircleGeomMold__" + img
		radius = _load_cache(cache_name, img)
		
		if radius == None:
			# Calculate the distance from the center to the farthest non-transparent pixel
			imgpath = os.path.join("imgs", img)
			surf = pygame.image.load(imgpath)
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
			radius = cand_dist/((surf.get_width()+surf.get_height())/2.0)
			_save_cache(cache_name, radius)
		
		self.radius = radius
	
	def make_geom(self, size, space = None, coll_props = -1):
		if space == None: space = app.dyn_space
		
		rad = self.radius*((size[0]+size[1])/2.0)
		geom = ode.GeomSphere(space, rad)
		geom.mold = self
		geom.draw_drives = [image.DCircle(rad)]
		geom.geom_args = (size, space, coll_props)
		
		if coll_props == -1: geom.coll_props = collision.Props()
		else: geom.coll_props = coll_props
		
		return geom


class BoxGeomMold(GeomMold):
	"""Creates a rectangular mold for an ODE box geom."""
	
	def __init__(self):
		pass
	
	def make_geom(self, size, space = None, coll_props = -1):
		if space == None: space = app.dyn_space
		geom = ode.GeomBox(space, (size[0], size[1], 1))
		geom.mold = self
		geom.draw_drives = [image.DWireBlock(size = size)]
		geom.geom_args = (size, space, coll_props)
		
		if coll_props == -1: geom.coll_props = collision.Props()
		else: geom.coll_props = coll_props
		
		return geom


class ComplexGeomMold(GeomMold):
	"""Creates a (potentially concave) polygonal mold for an ODE triangle mesh.
	
	Data attributes:
	outer_paths -- A list of lists of Points which define the outer edges of the polygon. (0,0) is the center of the object.
	inner_paths -- Like outer_paths, but for the inner edges.
	"""

	def _minimize(self, hull):
		if len(hull) > 3:
			# Create an approximate hull of lines based on the border pixels
			# We'll do this by subtracting superfluous points from the hull list
			death_list_five = [] #Indices for points that will be removed
			start = 0
			while start < (len(hull)-2):
				for end in range(len(hull)-1, start+1, -1):
					line = Line(hull[start], hull[end])
					cullable = True
					for mid in range(start+1, end):
						if line.nearest_pt_to(hull[mid]).dist_to(hull[mid]) > MAX_LINE_OFF:
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
				del hull[i]
		
		# The starting and ending points are arbitrary, and will never be 'mid' in the above loop
		# But, they still might be cullable
		if len(hull) > 4:
			# Check if both first and last are cullable, or just one or the other
			if (
			Line(hull[-2],hull[1]).nearest_pt_to(hull[-1]).dist_to(hull[-1]) <= MAX_LINE_OFF and
			Line(hull[-2],hull[1]).nearest_pt_to(hull[0]).dist_to(hull[0]) <= MAX_LINE_OFF
			):
				del hull[0]
				del hull[-1]
			elif Line(hull[-1], hull[1]).nearest_pt_to(hull[0]).dist_to(hull[0]) <= MAX_LINE_OFF:
				del hull[0]
			elif Line(hull[-2], hull[0]).nearest_pt_to(hull[-1]).dist_to(hull[-1]) <= MAX_LINE_OFF:
				del hull[-1]
		
	
	def _calc(self, surf):
		hull = []
		surf.lock()
		
		# Figure out which pixels are fairly transparent, subdivided into two groups:
		# 1. Outer : Touching the edge, or next to another pixel that is Outer
		# 2. Inner : Not touching the edge, or next to another pixel that is Inner
		inner_trans = set()
		outer_trans = set()
		for x in range(surf.get_width()):
			for y in range(surf.get_height()):
				pos = (x, y)
				
				if pos in inner_trans or pos in outer_trans:
					continue
				
				if surf.get_at(pos)[3] > MAX_TRANSPARENT_ALPHA:
					continue
				
				edge_touching = False
				seen = set()
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
					for s in seen: outer_trans.add(s)
				else:
					for s in seen: inner_trans.add(s)
		
		# Find all the edges that are between a non-transparent pixel and an image border or a border pixel 
		inner_edges = set()
		outer_edges = set()
		for x in range(surf.get_width()):
			for y in range(surf.get_height()):
				pos = (x, y)
				
				# Make sure this is a non-transparent pixel
				if surf.get_at(pos)[3] <= MAX_TRANSPARENT_ALPHA:
					continue
				
				for n in ((pos[0]+1, pos[1]), (pos[0]-1, pos[1])):
					if n[0] < 0 or n[0] >= surf.get_width() or n in outer_trans or n in inner_trans:
						mid = (pos[0]+n[0])/2
						eline = Line(Point(mid, n[1]-0.5), Point(mid, n[1]+0.5))
						if n in inner_trans:
							inner_edges.add(eline)
						else:
							outer_edges.add(eline)
				for n in ((pos[0], pos[1]+1), (pos[0], pos[1]-1)):
					if n[1] < 0 or n[1] >= surf.get_height() or n in outer_trans or n in inner_trans:
						mid = (pos[1]+n[1])/2
						eline = Line(Point(n[0]-0.5, mid), Point(n[0]+0.5, mid))
						if n in inner_trans:
							inner_edges.add(eline)
						else:
							outer_edges.add(eline)
		
		# We're done gathering information from the surface, now we need to organize it
		surf.unlock()
		
		# Sequence the edges into complete hulls (of points) that wrap back around
		outer_hulls = []
		inner_hulls = []
		for (edges, hulls) in ((outer_edges, outer_hulls), (inner_edges, inner_hulls)):
			while (len(edges) > 0):
				# Figure out if we've got any incomplete hulls that we can add an edge onto
				# An incomplete hull is one that doesn't wrap around
				dest_hull = None
				for hull in hulls:
					if len(hull) >= 3 and not hull[-1].near_to(hull[0]):
						dest_hull = hull
						break
				
				if dest_hull == None:
					# Looks like we'll have to create a new hull; let's just pick an edge at random
					hulls.append([])
					dest_hull = hulls[-1]
					victim = edges.pop()
					dest_hull.append(victim.a)
					dest_hull.append(victim.b)
				
				last = dest_hull[-1]
				to_remove = None
				for e in edges:
					if last.near_to(e.a):
						to_remove = e
						dest_hull.append(e.b)
						break
					elif last.near_to(e.b):
						to_remove = e
						dest_hull.append(e.a)
						break
				
				if to_remove != None:
					edges.remove(to_remove)
				else:
					print "Aborting due to dead-end pixel in complex hull: %s" % last
					sys.exit()
			
			for hull in hulls:
				#The last point will be right on top of the first, so it can be removed
				hull.pop()
				
				# Remove unneeded points
				self._minimize(hull)
				
				# Translate/scale the hull so that (0, 0) is the center of the image and it has a size of (1, 1)
				for i in range(0, len(hull)):
					hull[i] = ((hull[i][0]+0.5)/surf.get_width() - 0.5, (hull[i][1]+0.5)/surf.get_height() - 0.5)
		
		return {"outer" : outer_hulls, "inner" : inner_hulls}
	
	def __init__(self, img):
		cache_name = "ComplexGeomMold__" + img
		cache = _load_cache(cache_name, img)
		if cache == None:
			imgpath = os.path.join("imgs", img)
			surf = pygame.image.load(imgpath)
			cache = self._calc(surf)
			_save_cache(cache_name, cache)
		self.inner_paths = cache["inner"]
		self.outer_paths = cache["outer"]
	
	def make_geom(self, size, space = None, coll_props = -1, outer = 1, inner = 0):
		if space == None: space = app.dyn_space
		
		meshverts = []
		meshtris = []
		draw_drives = []
		
		def add_hull(hull):
			verts = []
			tris = []
			
			for p in hull:
				verts.append((p[0]*size[0], p[1]*size[1], -0.5))
				verts.append((p[0]*size[0], p[1]*size[1], 0.5))
			for x in range(0, len(verts), 2):
				tris.append((x, (x+1)%len(verts), (x+3)%len(verts)))
				tris.append((x, (x+2)%len(verts), (x+3)%len(verts)))
			
			prev_verts = len(meshverts)
			for v in verts:
				meshverts.append(v)
			for t in tris:	
				meshtris.append((t[0]+prev_verts, t[1]+prev_verts, t[2]+prev_verts))
		
		if outer:
			for hull in self.outer_paths:
				draw_drives.append(image.DPoly(hull))
				add_hull(hull)
		if inner:
			for hull in self.inner_paths:
				draw_drives.append(image.DPoly(hull, colors.green))
				add_hull(hull)
		
		tdat = ode.TriMeshData()
		tdat.build(meshverts, meshtris)	
		geom = ode.GeomTriMesh(tdat, space)
		geom.mold = self
		geom.draw_drives = draw_drives
		geom.geom_args = (size, space, coll_props, outer, inner)
		
		if coll_props == -1: geom.coll_props = collision.Props()
		else: geom.coll_props = coll_props
		
		return geom
