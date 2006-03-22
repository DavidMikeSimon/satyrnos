import pygame, os, ode

import app, math


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

def rotp(pt, cen, ang):
	"""Rotates a point around a center-point a given number of cw revolutions.

	This is for rotating for purposes of display; it's y-flipped compared to mathematical standards.
	"""

	a = rev2rad(ang)
	h = dist(cen, pt) #Radius of circle
	b = math.atan2(pt[1]-cen[1], pt[0]-cen[0]) #Previous angle between the two
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
	return math.sqrt(abs((a[0]-b[0])**2.0 + (a[1]-b[1])**2.0))

def nearest_on_line(a, b, p):
	"""Returns the nearest point on a line segment to an arbitrary point.
	
	The line is defined by a and b, and the point is p.
	"""
	u = (p[0]-a[0])*(b[0]-a[0]) + (p[1]-a[1])*(b[1]-a[1])
	u /= abs((a[0]-b[0])**2 + (a[1]-b[1])**2)
	u = min(max(0.0, u), 1.0)
	return (a[0] + u*(b[0]-a[0]), a[1] + u*(b[1]-a[1]))

def mag_force(source, target, tgtmass, pow, loss = 0, grav = False):
	"""Returns a 3-tuple, appropriate for passing to body.addForce(), for a magnetic/gravitational force.
	
	Force is emanating from source, affecting target. Both are passed as 2-tuples.
	Pow is the amount of force applied. Negative for pulling, positive for pushing.
	Loss is the amount of force lost per meter distance from the object (brings pow closer to zero).
	If grav is true, then mass of object is ignored; it acts as though objects have a mass of 1.
	"""
	
	#If we have loss, determine the actual amount of force applied
	force = pow
	d = dist(source, target)
	if loss != 0:
		diff = d*loss
		if pow > 0:
			diff = -diff
		force += diff
		#If the loss is so powerful that we change from pushing to pulling or vice versa, then cancel
		if (force > 0) != (pow > 0):
			return ((0, 0, 0))
	
	#If we're a gravity-like force (mass of object disregarded), adjust applied force to compensate
	if grav:
		force *= tgtmass
			
	#Calculate and return the force
	ang = math.atan2(target[1]-source[1], target[0]-source[0])
	return ((force*math.cos(ang), force*math.sin(ang), 0))
