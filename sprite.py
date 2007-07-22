import app, drive, resman

class DSprite(drive.Drive):
	"""Drive that draws an animated image.
	
	You provide a DSprite with a library of frames (in the form of DImages), some
	animation patterns (in the form of DSprite.Anim objects), and then
	specify one of those animation patterns as the current one, by name.

	Data attributes:
	cur_anim -- The key of the currently selected animation in anims.
	library -- A dictionary of drives that have drawing capability.
	anims -- A dictionary of DSprite.Anim objects.
	playing -- A boolean value that determines if the DSprite is animating. If False, stays on the same frame forever.
		When an Anim has a 'next' attribute of STOP, then playing is set to False when the animation ends.
	frame_time -- How long ago the current frame began to be shown. Updated whenever cur_anim is set or the sprite is drawn.
	frame -- Index of the frame in the current anim that we're at.
	"""

	class Anim:
		"""Represents an animation made up of a DSprite's frames.

		Data attributes:
		frames -- A sequence containing tuples of (library frame key, time in msecs)
		next -- If "REPEAT", then animation repeats forever. If "STOP", animation stops last frame. Else, must be name of another Anim.
		"""
		
		def __init__(self, frames, next = "REPEAT"):
			self.frames = frames
			self.next = next
	
	def __init__(self, cur_anim, library = None, anims = None, playing = True):
		super(DSprite, self).__init__(drawing = True)
		self.cur_anim = cur_anim
		
		if library == None: self.library = {}
		else: self.library = library
		
		if anims == None: self.anims = {}
		else: self.anims = anims
		
		self.playing = playing
		self.frame = 0
	
	def __str__(self):
		if self.playing:
			return super(DSprite, self).__str__() + "(P:" + str(self.library[self.anims[self.cur_anim].frames[self.frame][0]]) + ")"
		else:
			return super(DSprite, self).__str__() + "(STOPPED)"
	
	def cur_frame_len(self):
		"""Returns the length in msecs of the current frame."""
		return (self.anims[self.cur_anim].frames[self.frame])[1]
	
	def _draw(self, obj):
		if self.playing:
			self.frame_time += app.msecs
			while (self.frame_time > self.cur_frame_len()):
				self.frame_time -= self.cur_frame_len()
				self.frame += 1
				if self.frame > (len(self.anims[self.cur_anim].frames) - 1):
					if self.anims[self.cur_anim].next == "REPEAT":
						self.frame = 0
					elif self.anims[self.cur_anim].next == "STOP":
						self.playing = False
						self.frame -= 1
						break
					else:
						self.cur_anim = self.anims[self.cur_anim].next
						self.frame = 0
			
		self.library[self.anims[self.cur_anim].frames[self.frame][0]].draw(obj)
		
	def _get_cur_anim(self): return self._cur_anim
	def _set_cur_anim(self, cur_anim):
		self._cur_anim = cur_anim
		self.frame_time = 0
	cur_anim = property(_get_cur_anim, _set_cur_anim)
