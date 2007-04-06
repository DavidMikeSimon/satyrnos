from __future__ import division

import pygame, math, os, ode, cPickle
from OpenGL.GL import *

import app, image, collision
from geometry import *

# Constants used in mold generation
MAX_TRANSPARENT_ALPHA = 25 #Out of 255, the maximum alpha value of a pixel before it's not transparent
MAX_LINE_OFF = 0.8 #In pixels, how far a pixel can be away from a line before it's not "on" that line

def _save_cache(cache_name, obj):
	"""Pickles an object and saves it under a unique name. Used for caching calculations from
	time-consuming mold-generation routines like ComplexGeomMold."""
	
	cachef = open(cachedpath, "w")
	cPickle.dump(mold, cachedf)
	cachef.close()


def _load_cache(cache_name, img):
	"""Loads a cached object saved with _save_cache and returns it, unless the named image has a
	more recent modification than the cache file, or the cache file doesn't exist, in which case
	None is returned."""
	
	cachepath = os.path.join("moldcache", cache_name)
	imgpath = os.path.join("imgs", img)
	
	if os.access(cachepath, os.F_OK):
		c_mtime = os.stat(cachepath).st_mtime
		if c_mtime < os.stat(imgpath).st_mtime:
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
		
		if cached_radius == None:
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
		if (space == None): space = app.dyn_space
		
		rad = self.radius*((size[0]+size[1])/2.0)
		geom = ode.GeomSphere(space, rad)
		geom.mold = self
		geom.draw_drive = image.DCircle(rad)
		geom.geom_args = (size, space, coll_props)
		
		if (coll_props == -1): geom.coll_props = collision.Props()
		else: geom.coll_props = coll_props
		
		return geom


class BoxGeomMold(GeomMold):
	"""Creates a rectangular mold for an ODE box geom."""
	
	def __init__(self):
		pass
	
	def make_geom(self, size, space = None, coll_props = -1):
		if (space == None): space = app.dyn_space
		geom = ode.GeomBox(space, (size[0], size[1], 1))
		geom.mold = self
		geom.draw_drive = image.DWireBlock(size = size)
		geom.geom_args = (size, space, coll_props)
		
		if (coll_props == -1): geom.coll_props = collision.Props()
		else: geom.coll_props = coll_props
		
		return geom


class ComplexGeomMold(GeomMold):
	"""Creates a (potentially concave) polygonal mold using an ODE triangle mesh.
	
	Data attributes:
	vertices -- A list of Points which define the vertices of the polygon. (0,0) is the center of the object.
	"""
	
	def __init__(self, imgpath):
		pass
	
	def make_geom(self, size, space = None, coll_props = -1):
		if (space == None): space = app.dyn_space
		
		meshverts = []
		for v in self.vertices:
			meshverts.append((v[0], v[1], -0.5))
			meshverts.append((v[0], v[1], 0.5))
		
		meshtris = []
		for x in range(0, len(meshverts), 2):
			meshtris.append((x, (x+1)%len(meshverts), (x+3)%len(meshverts)))
			meshtris.append((x, (x+2)%len(meshverts), (x+3)%len(meshverts)))
		
		tdat = ode.TriMeshData()
		tdat.build(meshverts, meshtris)
		geom = ode.GeomTriMesh(tdat, space)
		geom.mold = self
		geom.geom_args = (size, space, coll_props)
		
		if (coll_props == -1): geom.coll_props = collision.Props()
		else: geom.coll_props = coll_props
		
		return geom
	
	def draw(self, obj):
		poly = image.DPoly(self.vertices)
		poly.draw(obj)
		points = image.DPoints(self.vertices)
		points.draw(obj)
