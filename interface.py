	def draw_frame(self, objects):
		"""Draws one frame based on the list of objects passed.
		
		This also resets the msecs data attribute."""
		
	
	def proc_input(self):
		"""Empties the event queue, does the appropriate thing on general app-related input.
		
		Throws an app.QuitException if user has requested that the game quit (i.e. by closing the window)
		"""
