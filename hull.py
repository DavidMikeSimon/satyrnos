from __future__ import division

import os, ode
from OpenGL.GL import *

import app, image
from geometry import *

import collision

def load_image_hull(imgname, size):
	"""Returns a Hull derivative based on hullgen.py precalculated info for some image."""
	
	hullpath = os.path.join("hulls", imgname + ".hull")
	hullf = open(hullpath, "r")
	hull = hullf.read().split(":")
	hullf.close()
	
	#First element is the hull type, everything after that is data
	htype = hull[0]
	del hull[0]
	
	if htype == "circle":
		#FIXME: This doesn't deal well with uneven x/y scaling, but it'll do temporarily
		coef = (size[0] + size[1])/2
		return CircleHull(float(hull[0]) * coef)
	elif htype == "box":
		return BoxHull(Size(hull[0], hull[1]) * size)
	elif htype == "complex":
		points = []
		for x in hull:
			p = x.split(",")
			p[0], p[1] = float(p[0]), float(p[1])
			points.append(Point(*p) * size)
		return ComplexHull(points)

class Hull:
	"""Describes how to create an ODE geom.
	
	This class is only to describe the interfaces that all the actual Hull types have.
	Once you've created a Hull object, use its make_geom() method to create an ODE geom
	with a 'hull' member set to the hull. Many parts of Satyrnose expect that collision geoms
	have hulls, so it's important to always create geoms using the make_geom() method,
	instead of manually.
	"""
	
	def make_geom(self, space = None, coll_props = -1):
		"""Returns an ODE geom in the given space based on this hull.
		
		It will have a hull member set to this Hull.
		If no space is specified, app.dyn_space will be used by default.
		If no coll_props is specified, it will make a new collision.Props
		with its default constructor. To disable collision, pass None
		as the coll_props value."""
		return None
	
	def draw(self, obj):
		"""Draws an outline of the hull in the current OpenGL mode."""
		pass

class CircleHull(Hull):
	"""Creates a circular hull using an ODE sphere geom."""
	
	def __init__(self, radius):
		self.radius = radius
	
	def make_geom(self, space = None, coll_props = -1):
		if (space == None): space = app.dyn_space
		geom = ode.GeomSphere(space, self.radius)
		geom.hull = self
		
		if (coll_props == -1): geom.coll_props = collision.Props()
		else: geom.coll_props = coll_props
		
		return geom

	def draw(self, obj):
		circ = image.DCircle(self.radius)
		circ.draw(obj)

class BoxHull(Hull):
	"""Creates a rectangular hull using an ODE box geom."""
	
	def __init__(self, size):
		self.size = size
	
	def make_geom(self, space = None, coll_props = -1):
		if (space == None): space = app.dyn_space
		geom = ode.GeomBox(space, (self.size[0], self.size[1], 1))
		geom.hull = self
		
		if (coll_props == -1): geom.coll_props = collision.Props()
		else: geom.coll_props = coll_props
		
		return geom
	
	def draw(self, obj):
		box = image.DWireBlock(size = self.size)
		box.draw(obj)

class ComplexHull(Hull):
	"""Creates a (potentially concave) polygonal hull using an ODE triangle mesh.
	
	Data attributes:
	vertices -- A list of Points which define the vertices of the polygon. (0,0) is the center of the object.
	"""
	
	def make_geom(self, space = None, coll_props = -1):
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
	
	def __init__(self, vertices):
		"""Creates a ComplexHull.

		The vertices list is not copied."""
		self.vertices = vertices
	
	def draw(self, obj):
		poly = image.DPoly(self.vertices)
		poly.draw(obj)
		points = image.DPoints(self.vertices)
		points.draw(obj)
