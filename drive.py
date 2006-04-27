class Drive(object):
	"""Base class for classes that control GameObj behavior/visuals.
	
	Derivatives should implement _step, _draw, and/or _predraw to
	implement the respective behaviors.
	
	Data attributes:
	drawing -- If false, then calls to draw() and predraw() do nothing.
	stepping -- If false, then calls to step() do nothing.
	"""
	
	def __init__(self, drawing = True, stepping = True):
		self.drawing = drawing
		self.stepping = stepping
		
	def draw(self, obj):
		"""Puts the object on-screen somehow.
		
		This will be called by app in a state where GL is ready and
		GL units are meters."""
		if (self.drawing):
			self._draw(obj)
	
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