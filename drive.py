from __future__ import division
from OpenGL.GL import *

import consenv, util, sre

class Drive(object):
	"""Base class for classes that control GameObj behavior/visuals.
	
	Derivatives should implement _step, _draw, and/or _predraw to
	implement the respective behaviors.
	
	Data attributes:
	offset -- If not None, then before a draw takes place, we translate by this Point.
	rot_offset -- If not near-zero, then before a draw takes place, rotates this amount of revolutions.
	drawing -- If false, then calls to draw() and predraw() do nothing.
	stepping -- If false, then calls to step() do nothing.
	"""

	def __init__(self, drawing = False, stepping = False, offset = None, rot_offset = 0):
		self.drawing = drawing
		self.stepping = stepping
		self.offset = offset
		self.rot_offset = rot_offset
	
	def __str__(self):
		return sre.match(r"<class '.+\.(.+)'>", str(type(self))).group(1)[1:] #Extract simple type name, remove first "D"
		
	def draw(self, obj):
		"""Puts the object on-screen somehow.
		
		This will be called by app in a state where GL is ready and
		GL units are meters."""
		if (self.drawing):
			need_pop = False
			
			if abs(self.rot_offset*obj.ang) > 0.00001:
				glPushMatrix()
				glRotate(util.rev2deg(obj.ang*self.rot_offset), 0, 0, 1)
				need_pop = True
			
			if self.offset != None:
				glTranslatef(self.offset[0], self.offset[1], 0)
				if not need_pop:
					glPushMatrix()
					need_pop = True
			
			self._draw(obj)
		
			if need_pop:
				glPopMatrix()
	
	def _draw(self, obj):
		pass
	
	def predraw(self, obj):
		"""Each frame, this is called on all drives before drawing phase begins on any.
		
		This will be called by app in a state where GL is ready and
		GL units are meters."""
		if (self.drawing):
			self._predraw(obj)
	
	def _predraw(self, obj):
		pass
	
	def step(self, obj):
		"""Performs any simulation-related stuff (for changing game state)."""
		if (self.stepping):
			self._step(obj)
	
	def _step(self, obj):
		pass


class DDebug(Drive):
	"""Drive that executes arbitrary expressions.

	Expressions will be executed within the debugging console's environment.
	When executed, 'obj' will be set to the relevant GameObj, then del'd after the expression is done.
	
	Data attributes:
	draw_expr, predraw_expr, step_expr -- If not None, these are eval()ed at the appropriate call.
	"""
	
	def __init__(self, draw_expr = None, predraw_expr = None, step_expr = None):
		"""Creates a DDebug with compiled versions of the given code.
		
		Since compile() is used, you can pass statements as well as expressions
		in the arguments to __init__."""
		
		super(DDebug, self).__init__(True, True)
		
		self.draw_expr = None
		self.predraw_expr = None
		self.step_expr = None
		
		if (draw_expr != None):
			self.draw_expr = compile(draw_expr, "draw_expr", "single")
		if (predraw_expr != None):
			self.predraw_expr = compile(predraw_expr, "predraw_expr", "single")
		if (step_expr != None):
			self.step_expr = compile(step_expr, "step_expr", "single")
	
	def _attempt(self, obj, expr):
		if expr != None:
			try:
				consenv.obj = obj
				eval(expr, consenv.__dict__)
				del consenv.obj
			except Exception, e:
				print "DDebug exception: " + repr(e) + " : " + e.__str__()
			except:
				print "DDebug unknown exception"
	
	def _draw(self, obj):
		self._attempt(obj, self.draw_expr)
	
	def _predraw(self, obj):
		self._attempt(obj, self.predraw_expr)
			
	def _step(self, obj):
		self._attempt(obj, self.step_expr)
