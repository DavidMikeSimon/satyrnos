from __future__ import division

import pygame, os, ode, math, sre

import app, collision
from geometry import *

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

def min_ang_diff(src, dest):
	"""Returns the shortest angular distance between two angles (in revolutions).

	By "shortest", I mean that this will return whichever is lesser out of
	clockwise or counter-clockwise."""
	dist = (dest - src) % 1
	if 1-dist < dist:
		dist = -(1-dist)
	return dist

def cap_ang_diff(ang, max):
	"""Reduces an angle offset to be less than a maximum, maintaining sign."""
	if abs(ang) > max:
		if ang > 0:
			return max
		else:
			return -max
	else:
		return ang

def anchored_joint(joint_type, obj1, anchor = None, obj2 = None):
	"""Creates a new joint of the given type between two GameObjs, calls setAnchor on it.

	Anchor is given as a point offset relative to the position of obj1.
	
	If obj2 is unspecified, then the joint is created between obj1 and the static environment.
	Either way, object(s) must be correctly positioned before this method is called.
	"""
	if anchor == None: anchor = Point(0, 0)
	joint = joint_type(app.odeworld)
	if (obj2 != None):
		joint.attach(obj1.body, obj2.body)
	else:
		joint.attach(obj1.body, ode.environment)
	joint.setAnchor((obj1.pos[0] + anchor[0], obj1.pos[1] + anchor[1], 0))
	return joint

def sphere_body(density, radius):
	"""Creates an ODE body which is a sphere of the given density and radius.
	
	It will be given a body_type data attribute set to "sphere".
	It will be given radius and density data attributes, set to the given arguments.
	"""
	
	body = ode.Body(app.odeworld)
	omass = ode.Mass()
	omass.setSphere(density, radius)
	body.setMass(omass)
	body.radius = radius
	body.density = density
	body.body_type = "sphere"
	return body


class TrackerList(list):
	"""A membership-checking optimized version of the regular list.
	
	Behaves exactly like a list, except that the 'in' operator, count, and __contains__ are
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

	def __str__(self):
		ret = ""
		x = 0
		for i in self:
			ret = ret + "%02i: %s\n" % (x, str(i))
			x += 1
		return ret
	
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


class LayeredList(list):
	"""A list that should contain only other lists, that propogates membership/count checking calls to them
	and iterates recursively through them. The sublists themselves are skipped for these operations; that
	is, to iterate over a LayeredList of lists of Thingy objects is to iterate over Thingy objects.
	
	Additionally, when append() is called with a non-list argument, then that argument is instead appended
	to the last sublist. 
	
	These features continue to work if you have LayeredLists that contain other LayeredLists, and so on.
	However, a LayeredList that contains a non-LayeredList will only descend to that first list, not
	to its sublists."""
	
	_tabberpat = sre.compile(r"^", sre.M)
	
	class _Iter:
		def __init__(self, tgtlist):
			self.pos = -1
			self.tgtlist = tgtlist
			self.subiter = None
		
		def __iter__(self):
			return self
		
		def next(self):
			if self.subiter == None:
				self.pos += 1
				if (self.pos < len(self.tgtlist)):
					self.subiter = iter(self.tgtlist[self.pos])
					return self.next()
				else:
					raise StopIteration
			else:
				try:
					return self.subiter.next()
				except StopIteration:
					self.subiter = None
					return self.next()
	
	def __iter__(self):
		return LayeredList._Iter(self)
	
	def __contains__(self, y):
		for sublist in self.plain_iter():
			if y in sublist: return True
		return False
	
	def __str__(self):
		ret = ""
		x = 0
		for i in self.plain_iter():
			ret = ret + ("%02i:\n%s\n" % (x, sre.sub(self._tabberpat, " ", str(i)))).strip() + "\n"
			x += 1
		return ret.strip()
	
	def append(self, o):
		if isinstance(o, list):
			super(LayeredList, self).append(o)
		else:
			self[len(self)-1].append(o)
	
	def plain_iter(self):
		"""Returns an iterator that behaves like a regular list iterator, doesnt skip over or descend into sublists."""
		return super(LayeredList, self).__iter__()
	
	def count(self, val):
		"""Sums the values of count() in all sublists of this LayeredList."""
		sum = 0
		for sublist in self:
			sum += sublist.count(val)
		return sum
