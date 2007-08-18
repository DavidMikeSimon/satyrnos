from __future__ import division
import math, copy
import util

def _coordlike_copy(obj):
	"""Given an object, if it's not already a derivative of _CoordLike,
	then it returns a new _CoordLike with that object in both fields. Otherwise,
	it makes a copy of the object and returns it."""
	if isinstance(obj, _CoordLike):
		return copy.copy(obj)
	else:
		return _CoordLike(obj)

def _coordlikeify(obj):
	"""Like _coordlike_copy, but if the object is already a derivative of _CoordLike,
	just returns the object itself (not a copy)."""
	if isinstance(obj, _CoordLike):
		return obj
	else:
		return _CoordLike(obj)

class _CoordLike(list):
	"""Used to implement the magic of both Point and Size.
	
	Basically, just a two element list that supports arithmetic, both
	between two _CoordLikes and between a _CoordLike and a number,
	which is just treated like a _CoordLike with both fields set
	to that number."""
	
	def __init__(self, a, b = None):
		"""
		Creates a _CoordLike.
		
		If only one argument is specified, it's copied into both fields."""
		
		self.append(a)
		if b == None:
			self.append(a)
		else:
			self.append(b)
	
	def __add__(self, y):
		ret = _coordlike_copy(self)
		ret += y
		return ret
	
	def __radd__(self, y):
		return self.__add__(y)
	
	def __iadd__(self, y):
		cy = _coordlikeify(y)
		self[0] += cy[0]
		self[1] += cy[1]
		return self
	
	def __sub__(self, y):
		return self + (-y)
	
	def __rsub__(self, y):
		return (-self) + y
	
	def __isub__(self, y):
		self += (-y)
		return self
	
	def __mul__(self, y):
		ret = _coordlike_copy(self)
		ret *= y
		return ret
	
	def __rmul__(self, y):
		return self.__mul__(y)
	
	def __imul__(self, y):
		cy = _coordlike_copy(y)
		self[0] *= cy[0]
		self[1] *= cy[1]
		return self
	
	def __div__(self, y):
		ret = _coordlike_copy(self)
		ret /= y
		return ret
	
	def __rdiv__(self, y):
		return _coordlikeify(y).__div__(self)
	
	def __idiv__(self, y):
		cy = _coordlikeify(y)
		self[0] /= cy[0]
		self[1] /= cy[1]
		return self
	
	def __truediv__(self, y):
		return self.__div__(y)
	
	def __rtruediv__(self, y):
		return _coordlikeify(y).__truediv__(self)
	
	def __itruediv__(self, y):
		return self.__idiv__(y)
	
	def __floordiv__(self, y):
		ret = _coordlike_copy(self)
		ret //= y
		return ret
	
	def __rfloordiv__(self, y):
		return _coordlikeify(y).__floordiv__(self)
	
	def __ifloordiv__(self, y):
		cy = _coordlikeify(y)
		self[0] //= cy[0]
		self[1] //= cy[1]
		return self
	
	def __neg__(self):
		c = copy.copy(self)
		c[0] = -c[0]
		c[1] = -c[1]
		return c
	
	def __abs__(self):
		c = copy.copy(self)
		c[0] = abs(c[0])
		c[1] = abs(c[1])
		return c
	
	def near_to(self, y):
		"""Returns true if this point and the other are close enough to be considered equal."""
		return (abs(self[0]-y[0])<0.0001 and abs(self[1]-y[1])<0.0001)


class Point(_CoordLike, object):
	"""Represents a point in two-dimensional space.
	
	Units are in game meters.
	
	This class could also be used to represent vectors or point offsets.
	
	Data attributes:
	x, y -- The coordinates (mean the same thing as pt[0] and pt[1] respectively).
	"""
			
	def __init__(self, x = 0, y = 0):
		super(Point, self).__init__(x, y)
	
	def __copy__(self):
		return Point(self[0], self[1])
	
	def __deepcopy__(self, memo):
		return self.__copy__()
	
	def mag(self):
		"""Returns the distsance between the origin and this point."""
		return math.sqrt(self[0]*self[0] + self[1]*self[1])
	
	def dist_to(self, other):
		"""Returns the distance between this point and another."""
		return math.sqrt((self[0]-other[0])**2.0 + (self[1]-other[1])**2.0)
	
	def ang(self):
		"""Returns the angle from the origin to this point."""
		return Point(0,0).ang_to(self)
	
	def ang_to(self, other):
		"""Returns the angle from this point to another in clockwise revolutions.
	
		If other is directly to the right of this point, then the angle is zero."""
		return math.atan2(other[1]-self[1], other[0]-self[0])/(2*math.pi)
	
	def to_length(self, len = 1.0):
		"""Returns a coord of a given length, but in the same direction from the origin."""
		if len == 0.0:
			return Point(0,0)
		oldlen = self.dist_to(Point(0,0))
		ret = Point(self[0], self[1])
		if oldlen != 0.0:
			ret[0] *= len/oldlen
			ret[1] *= len/oldlen
		return ret
	
	def rot(self, cen, ang):
		"""Returns this point rotated around a center a given number of cw revolutions."""
	
		if abs(ang) < 0.000001:
			return copy.copy(self)
		a = util.rev2rad(ang) #Convert to ccw radians
		h = cen.dist_to(self) #Radius of circle
		b = util.rev2rad(cen.ang_to(self))
		return Point(h*math.cos(a+b)+cen[0], -1*h*math.sin(a+b)+cen[1])
	
	def fake_3d_tuple(self):
		"""Returns a 3-tuple (point[0], point[1], 0)."""
		return (self[0], self[1], 0)
	
	def _get_x(self): return self[0]
	def _set_x(self, x): self[0] = x
	def _get_y(self): return self[1]
	def _set_y(self, y): self[1] = y
	x = property(_get_x, _set_x)
	y = property(_get_y, _set_y)
	

class Size(_CoordLike, object):
	"""Represents the width and height of some object in two-dimensional space.
	
	Units are in game meters.
	
	The corner methods (tl, tr, bl, br) return the corner positions of a rectangle
	with this size centered at the origin.
	
	Data attributes:
	w, h -- The width and height (mean the same as x[0] and x[1] respectively).
	"""
	
	def __init__(self, w = 0, h = 0):
		super(Size, self).__init__(w, h)
	
	def __copy__(self):
		return Size(self[0], self[1])
	
	def __deepcopy__(self, memo):
		return self.__copy__()
	
	def area(self):
		return self[0]*self[1]
	
	def tl(self): return Point(-(self.w/2), -(self.h/2))
	def tr(self): return Point( (self.w/2), -(self.h/2))
	def bl(self): return Point(-(self.w/2),  (self.h/2))
	def br(self): return Point( (self.w/2),  (self.h/2))

	def _get_w(self): return self[0]
	def _set_w(self, w): self[0] = w
	def _get_h(self): return self[1]
	def _set_h(self, h): self[1] = h
	w = property(_get_w, _set_w)
	h = property(_get_h, _set_h)


class Line:
	"""Represents a line segment from one point to another.
	
	Units are in game meters.
	
	Data attributes:
	a, b -- Two Points defining the ends of the line.
	"""
	
	def __init__(self, a, b):
		self.a = a
		self.b = b
	
	def __copy__(self):
		return Line(self.a, self.b)
	
	def __deepcopy__(self, memo):
		return Line(self.a.__copy__(), self.b.__copy__())
		
	def nearest_pt_to(self, p):
		"""Returns the nearest point on the line segment to an arbitrary point."""
		u = (p.x-self.a.x)*(self.b.x-self.a.x) + (p.y-self.a.y)*(self.b.y-self.a.y)
		u /= abs((self.a.x-self.b.x)**2 + (self.a.y-self.b.y)**2)
		u = min(max(0.0, u), 1.0)
		return Point(self.a.x + u*(self.b.x-self.a.x), self.a.y + u*(self.b.y-self.a.y))


class Rect:
	"""Represents a rectangle, possibly rotated.
	
	Units are in game meters.
	
	Data attributes:
	cen -- A Point which is the center of the rect.
	size -- A Size which is the width and height of the rect.
	ang -- An angle for the rectangle in clockwise revolutions.
	"""
	
	def __init__(self, cen, size, ang = 0):
		self.cen = cen
		self.size = size
		self.ang = ang
	
	def __copy__(self):
		return Rect(self.cen, self.size, self.ang)
	
	def __deepcopy__(self, memo):
		return Line(self.cen.__copy__(), self.size.__copy__(), self.ang)
	
	def tl(self): return Point(self.cen.x-(self.size.w/2), self.cen.y-(self.size.h/2)).rot(self.cen, self.ang)
	def tr(self): return Point(self.cen.x+(self.size.w/2), self.cen.y-(self.size.h/2)).rot(self.cen, self.ang)
	def bl(self): return Point(self.cen.x-(self.size.w/2), self.cen.y+(self.size.h/2)).rot(self.cen, self.ang)
	def br(self): return Point(self.cen.x+(self.size.w/2), self.cen.y+(self.size.h/2)).rot(self.cen, self.ang)
	
	def corners(self):
		"""Returns a tuple of the corners of the box in clockwise order, starting with the top left."""
		return (self.tl(), self.tr(), self.br(), self.bl())
	
	def sides(self):
		"""Returns a tuple of the box's sides as Lines in clockwise order, starting with the top."""
		c = self.corners()
		return (Line(c[0], c[1]), Line(c[1], c[2]), Line(c[2], c[3]), Line(c[3], c[0]))
		
	def contains(self, p):
		"""Returns true if the given point is inside the box."""
		
		#Rotate the point in the opposite direction around box center, check against unrotated box
		realp = p.rot(self.cen, -self.ang);
		for axis in range(0, 2):
			if (realp[axis] > self.cen[axis] + self.size[axis]/2): return False
			if (realp[axis] < self.cen[axis] - self.size[axis]/2): return False
		return True
	
	def nearest_pt_to(self, p):
		"""Returns the nearest point in the box to an arbitrary point.
		
		Of course, if the point is inside the box, then the nearest point
		in the box to the point is itself.
		"""
		
		nearest = p
		if self.contains(p):
			return nearest
	
		curdist = nearest.dist_to(self.cen)
		for s in self.sides():
			cand = s.nearest_pt_to(p)
			cand_dist = cand.dist_to(p)
			if cand_dist < curdist:
				curdist = cand_dist
				nearest = cand
		
		return nearest
