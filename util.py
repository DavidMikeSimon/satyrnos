from __future__ import division

import pygame, os, ode, math

import app

def rev2rad(ang):
	"""Converts an angle in cw revolutions to ccw radians.
	
	This is mostly used when handing angles to ODE.
	"""
	return -2.0 * ang * math.pi

def rev2deg(ang):
	"""Converts an angle in cw revolutions to cw degrees.

	This is mostly used when handing angles to OpenGL.
	"""
	return 360 * ang

def tupm(tuple, val):
	"""Given a 2-tuple, returns it with both parts multiplied by val."""
	
	return (tuple[0]*val, tuple[1]*val)

def tupa(a, b):
	"""Given a couple 2-tuples, returns (a[0]+b[0], a[1]+b[1])."""

	return (a[0]+b[0], a[1]+b[1])

def rotp(pt, cen, ang):
	"""Rotates a point around a center-point a given number of cw revolutions."""

	if abs(ang) < 0.000001:
		return pt
	a = rev2rad(ang) #Convert to ccw radians
	h = dist(cen, pt) #Radius of circle
	b = -math.atan2(pt[1]-cen[1], pt[0]-cen[0]) #Previous angle between the two (neg to make it ccw)
	return (h*math.cos(a+b)+cen[0], -1*h*math.sin(a+b)+cen[1])

def sphere_body(density, radius):
	"""Creates an ODE body which is a sphere of the given density and radius.
	
	It will be given radius and density data attributes, set to the given arguments.
	"""
	
	body = ode.Body(app.odeworld)
	omass = ode.Mass()
	omass.setSphere(density, radius)
	body.setMass(omass)
	body.radius = radius
	body.density = density
	return body

def box_geom(size):
	"""Creates an ODE geom which is a box of the given 2-tuple size.

	It will be given a size data attribute set to the given argument.
	"""

	geom = ode.GeomBox(app.odespace, (size[0], size[1], 1))
	geom.size = size
	return geom

def sphere_geom(radius):
	"""Creates an ODE geom which is a sphere of the given 2-tuple size.

	It will be given a radius data attribute set to the given argument.
	"""

	geom = ode.GeomSphere(app.odespace, radius)
	geom.radius = radius
	return geom

def dist(a, b):
	"""Returns the distance between two 2-tuple positions.
	"""
	return math.sqrt((a[0]-b[0])**2.0 + (a[1]-b[1])**2.0)

def inside_box(boxcen, size, ang, p):
	"""Returns true if p is with a box centered at boxcen of size size rotated by angle ang.
	"""
	#Rotate the point in the opposite direction around box center, check against unrotated box
	realp = rotp(p, boxcen, -ang);
	for axis in range(0, 2):
		if (realp[axis] > boxcen[axis] + size[axis]/2): return False
		if (realp[axis] < boxcen[axis] - size[axis]/2): return False
	return True

def nearest_on_line((a, b), p):
	"""Returns the nearest point on a line segment to an arbitrary point.
	
	The line is defined by the end-points a and b, and the point is p.
	"""
	u = (p[0]-a[0])*(b[0]-a[0]) + (p[1]-a[1])*(b[1]-a[1])
	u /= abs((a[0]-b[0])**2 + (a[1]-b[1])**2)
	u = min(max(0.0, u), 1.0)
	return (a[0] + u*(b[0]-a[0]), a[1] + u*(b[1]-a[1]))

def nearest_in_box(boxcen, size, ang, p):
	"""Returns the nearest point in a box to an arbitrary point.
	
	The box is centered at boxpos, and rotated by ang. Of course, if the point is inside the
	box, then the nearest point in the box to the point is itself.
	"""
	
	nearest = p
	if inside_box(boxcen, size, ang, p):
		return nearest
	
	halfwidth = size[0]/2.0
	halfheight = size[1]/2.0
	tl = rotp((boxcen[0]-halfwidth, boxcen[1]-halfheight), boxcen, ang)
	tr = rotp((boxcen[0]+halfwidth, boxcen[1]-halfheight), boxcen, ang)
	bl = rotp((boxcen[0]-halfwidth, boxcen[1]+halfheight), boxcen, ang)
	br = rotp((boxcen[0]+halfwidth, boxcen[1]+halfheight), boxcen, ang)

	curdist = dist(nearest, boxcen)
	for s in ((tl,tr), (bl,br), (tl,bl), (tr,br)):
		cand = nearest_on_line(s, p)
		cand_dist = dist(cand, p)
		if cand_dist < curdist:
			curdist = cand_dist
			nearest = cand
	
	return nearest


class TrackerList(list):
	"""Behaves exactly like a list, except that the 'in' operator, count, and __contains__ are
	more efficient, and compare by id(), rather than by equality."""
	
	def _decrid(self, i, n = 1):
		#Decrease the idcount for the given id by n
		if (self._idcounts[i] > n):
			self._idcounts[i] -= n
		else:
			del self._idcounts[i]

	def _incrid(self, i, n = 1):
		#Increase the idcount for the given id by n
		if self._idcounts.has_key(i):
			self._idcounts[i] += n
		else:
			self._idcounts[i] = n
	
	def __add__(self, y):
		r = self[:]
		list.__iadd__(r, y)
		r._idcounts = self._idcounts.copy()
		if isinstance(y, TrackerList):
			for k in y._idcounts.keys():
				r._incrid(k, y._idcounts[k])
		else:
			for v in y:
				r._incrid(id(v))
		return r

	def __contains__(self, y):
		return self._idcounts.has_key(id(y))
	
	def __delitem__(self, y):
		if not isinstance(y, slice):
			self._decrid(id(self[y]))
		else:
			for e in list.__getitem__(self, y):
				self._decrid(id(e))
		list.__delitem__(self, y)
	
	def __delslice__(self, i, j):
		self.__delitem__(slice(i, j))
	
	def __getitem__(self, i):
		if not isinstance(i, slice):
			return list.__getitem__(self, i)
		else:
			return TrackerList(list.__getitem__(self, i))

	def __getslice__(self, i, j):
		return self.__getitem__(slice(i, j))
		return TrackerList(list.__getslice__(self, i, j))
	
	def __iadd__(self, y):
		list.__iadd__(self, y)
		if (isinstance(y, TrackerList)):
			for k in y._idcounts.keys():
				self._incrid(k, y._idcounts[k])
		else:
			for v in y:
				self._incrid(id(v))
		return self
	
	def __imul__(self, y):
		list.__imul__(self, y)
		for k in self._idcounts.keys():
			self._idcounts[k] *= y
		return self
	
	def __mul__(self, y):
		r = self[:]
		list.__imul__(r, y)
		for k in self._idcounts.keys():
			r._idcounts[k] *= y
		return r
	
	def __setitem__(self, i, y):
		if not isinstance(i, slice):
			self._decrid(id(self[i]))
			list.__setitem__(self, i, y)
			self._incrid(id(self[i]))
		else:
			for e in list.__getitem__(self, i):
				self._decrid(id(e))
			list.__setitem__(self, i, y)
			for e in y:
				self._incrid(id(e))
	
	def __setslice__(self, i, j, v):
		self.__setitem__(slice(i, j), v)
	
	def __init__(self, seq = None):
		"""Creates a new TrackerList. If seq is provided, creates a new TrackerList with seq's items."""
		self._idcounts = {} #Key is some id, value is # of list elements in self with a value having that id
		if (seq == None):
			list.__init__(self)
		else:
			list.__init__(self, seq)
			if (isinstance(seq, TrackerList)):
				self._idcounts = seq._idcounts.copy()
			else:
				for v in seq:
					self._incrid(id(v))
	
	def append(self, o):
		list.append(self, o)
		self._incrid(id(o))
	
	def count(self, val):
		if self._idcounts.has_key(id(val)):
			return self._idcounts[id(val)]
		else:
			return 0
	
	def extend(self, iterable):
		list.extend(self, iterable)
		if (isinstance(iterable, TrackerList)):
			for k in iterable._idcounts.keys():
				self._incrid(k, iterable._idcounts[k])
		else:
			for v in iterable:
				self._incrid(id(v))

	def insert(self, idx, o):
		list.insert(self, idx, o)
		self._incrid(id(o))
	
	def pop(self, idx = None):
		if idx == None:
			self._decrid(id(self[-1]))
			return list.pop(self)
		else:
			self._decrid(id(self[idx]))
			return list.pop(self, idx)
	
	def remove(self, val):
		#This will throw an exception (before _decrid() is called) if val is not in list
		list.remove(self, val)
		self._decrid(id(val))
