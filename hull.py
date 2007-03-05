from __future__ import division

import pygame, math, os, ode, cPickle
from OpenGL.GL import *

import app, image, collision
from geometry import *

# Constants used in hull generation
MAX_TRANSPARENT_ALPHA = 25 #Out of 255, the maximum alpha value of a pixel before it's not transparent
MAX_LINE_OFF = 0.8 #In pixels, how far a pixel can be away from a line before it's not "on" that line

def load_hull(hullname):
	"""Returns a Hull derivative based on the information in the given hull description file.
	
	If a pre-pickled hull exists, and is more recent than the hull description file and the
	image, then it is used instead."""
	
	hullpath = os.path.join("hulls", hullname + ".hull")
	hullf = open(hullpath, "r")
	(imgname, htype) = hullf.read().strip().split(":")
	hullf.close()
	pickledpath = os.path.join("hulls", hullname + ".pickled")
	imgpath = os.path.join("imgs", imgname)
	
	hull = None
	
	if os.access(pickledpath, os.F_OK):
		p_mtime = os.stat(pickledpath).st_mtime
		if p_mtime < os.stat(imgpath).st_mtime and p_mtime < os.stat(hullpath).st_mtime:
			pickledf = open(pickledpath, "r")
			hull = cPickle.load(pickledf)
			pickledf.close()
	
	if hull == None:
		hull_types = {
			'box': BoxHull,
			'circle': CircleHull,
			'complex': ComplexHull
		}
		
		if hull_types.has_key(htype):
			hull = hull_types[htype](imgpath)
		else:
			raise RuntimeError("No such hull type '%s'" % htype)
		pickledf = open(pickledpath, "w")
		cPickle.dump(hull, pickledf)
		pickledf.close()
	
	return hull


class Hull:
	"""Describes how to create an ODE geom.
	
	This class is only to describe the interfaces that all the actual Hull types have.
	Once you've created a Hull object, use its make_geom() method to create an ODE geom
	with a 'hull' member set to the hull. Many parts of Satyrnos expect that collision geoms
	have hulls, so it's important to always create geoms using the make_geom() method,
	instead of by calling the ODE geom constructors directly.
	"""

	def make_geom(self, size, space = None, coll_props = -1):
		"""Returns an ODE geom in the given space based on this hull.
		
		It will have a hull member set to this Hull.
		It will also have a draw_drive member set to a drive that can draw the Hull.
		If no space is specified, app.dyn_space will be used by default.
		If no coll_props is specified, it will make a new collision.Props
		with its default constructor. To disable collision, pass None
		as the coll_props value."""
		return None
	
	def draw(self, obj):
		"""Draws an outline of the hull."""
		pass


class CircleHull(Hull):
	"""Creates a circular hull around an image using an ODE sphere geom."""
	
	def __init__(self, imgpath = None):
		if imgpath == None:
			self.radius = 0.5
			return
		
		# Calculate the distance from the center to the farthest non-transparent pixel
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
		self.radius = cand_dist/((surf.get_width()+surf.get_height())/2.0)

	def make_geom(self, size, space = None, coll_props = -1):
		if (space == None): space = app.dyn_space
		
		rad = self.radius*((size[0]+size[1])/2.0)
		geom = ode.GeomSphere(space, rad)
		geom.hull = self
		geom.draw_drive = image.DCircle(rad)
		
		if (coll_props == -1): geom.coll_props = collision.Props()
		else: geom.coll_props = coll_props
		
		return geom


class BoxHull(Hull):
	"""Creates a rectangular hull using an ODE box geom."""
	
	def __init__(self, imgpath = None):
		# We don't actually even need to look at the image; the hull will just be rectangle the size of the image
		pass
	
	def make_geom(self, size, space = None, coll_props = -1):
		if (space == None): space = app.dyn_space
		geom = ode.GeomBox(space, (size[0], size[1], 1))
		geom.hull = self
		geom.draw_drive = image.DWireBlock(size = size)
		
		if (coll_props == -1): geom.coll_props = collision.Props()
		else: geom.coll_props = coll_props
		
		return geom


class ComplexHull(Hull):
	"""Creates a (potentially concave) polygonal hull using an ODE triangle mesh.
	
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
		geom.hull = self
		
		if (coll_props == -1): geom.coll_props = collision.Props()
		else: geom.coll_props = coll_props
		
		return geom
	
	def draw(self, obj):
		poly = image.DPoly(self.vertices)
		poly.draw(obj)
		points = image.DPoints(self.vertices)
		points.draw(obj)
