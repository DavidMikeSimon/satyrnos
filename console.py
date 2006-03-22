import code, pygame, sys, copy, sre
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *

import app
import colors
import consenv

helphelp = "Interactive Python help is not available in Satyrnose. You can still use help(object)."
quithelp = "To close the debugging console, hold down shift and type ~ (a tilde)."

class PseudoOut:
	"""A substitue stderr/stdout that appends to an OutputBox and also forwards to the real stderr."""
	
	def __init__(self, out):
		self.out = out

	def write(self, str):
		print >> sys.__stderr__, str,
		self.out.append(str)


class EditBox:
	"""Displays a string and a cursor, accepts events for moving the cursor and editing the string.

	Tabs are the same as just hitting space twice. Shift+Delete clears the box.
	Characters displayed in the EditBox are 9 pixels wide and 15 pixels tall (GLUT bitmap font).
	Since there's always one row of characters, there's not much point in having it be any height but 15.
	
	Data attributes:
	cursor -- Position of the input box cursor (0 means all the way at the left).
	cont -- Whatever is typed into the box right now.
	rect -- The rectangle defining the box's size and position in pixels (draw size is a 5px more on each side).
	prompt -- Uneditable text at the beginning of the box.
	"""
	
	#All the characters that we can accept when typed
	inpat = sre.compile(r"[-0-9A-Za-z!@#$%^&*\(\)_+=\\|{}\[\]:;'<,>.?/` \"']")

	def __init__(self, rect = None):
		"""Creates an EditBox."""
		self.rect = rect
		self.cursor = 0
		self.cont = ""
		self.prompt = ""

	def clear(self):
		"""Empties the EditBox and moves the cursor back to the starting position."""
		self.cont = ""
		self.cursor = 0
		
	def draw(self):
		"""Draws the EditBox."""
		
		#Draw a background box for the edit area
		glColor4f(0.0, 0.0, 0.0, 0.9)
		glBegin(GL_QUADS)
		glVertex2f(self.rect.left-5, self.rect.top-5)
		glVertex2f(self.rect.right+5, self.rect.top-5)
		glVertex2f(self.rect.right+5, self.rect.bottom+5)
		glVertex2f(self.rect.left-5, self.rect.bottom+5)
		glEnd()
		
		glColor4f(1.0, 1.0, 1.0, 1.0)
		
		#Draw the text and prompt
		glRasterPos2f(self.rect.left, self.rect.top+12) #11 is the magic number, 1 to make it look centered in EditBox
		for c in (self.prompt + self.cont):
			glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(c))
		
		#Draw the cursor
		cpos = self.rect.left + 9*(self.cursor + len(self.prompt))
		glBegin(GL_LINES)
		glVertex2f(cpos, self.rect.top)
		glVertex2f(cpos, self.rect.bottom)
		glEnd()
	
	def handle(self, event):
		"""Handles a keyboard event (either to change the contents of the input box, or move the cursor.)"""
		
		if event.key == K_LEFT:
			self.cursor = max(0, self.cursor-1)
		elif event.key == K_RIGHT:
			self.cursor = min(len(self.cont), self.cursor+1)
		elif event.key == K_DELETE:
			if pygame.key.get_mods() & KMOD_SHIFT:
				self.clear()
			elif self.cursor < len(self.cont):
				self.cont = self.cont[0:self.cursor] + self.cont[self.cursor+1:len(self.cont)]
		elif event.key == K_BACKSPACE:
			if self.cursor > 0:
				self.cont = self.cont[0:self.cursor-1] + self.cont[self.cursor:len(self.cont)]
				self.cursor -= 1
		elif event.key == K_HOME:
			self.cursor = 0
		elif event.key == K_END:
			self.cursor = len(self.cont)
		elif event.key == K_TAB:
			self.cont = self.cont[0:self.cursor] + "  " + self.cont[self.cursor:len(self.cont)]
			self.cursor += 2
		elif self.inpat.match(event.unicode):
			self.cont = self.cont[0:self.cursor] + event.unicode + self.cont[self.cursor:len(self.cont)]
			self.cursor += 1

class OutputBox:
	"""Caches a certain number of lines of information, draws screenfuls of it.
	
	Characters displayed in the OutputBox are 9 pixels wide and 15 pixels tall (GLUT bitmap font).
	
	Data attributes:
	scroll -- How far we have scrolled up (0 means we're at bottom, 10 means bottom ten lines aren't visible).
	buffer -- The output to the console. A list of strings, each of which is one line, without the newline.
	        If the last thing to go into buffer ended with a newline, then the last element of buffer will be an empty string.
	bufferlen -- No more than this many lines will be saved.
	rect -- The rectangle defining the box's size and position in pixels (draw size is a 5px more on each side).
	"""
	
	def __init__(self, rect = None):
		"""Creates an OutputBox."""
		self.rect = rect
		self.buffer = [""]
		self.bufferlen = 500
		self.scroll = 0

	def dispsize(self):
		"""Returns the possible number of lines that can be displayed by the OutputBox at once."""
		return self.rect.height/15

	def draw(self):
		"""Draws the OutputBox."""
		
		#Draw a background box for the display
		glColor4f(0.0, 0.0, 0.0, 0.9)
		glBegin(GL_QUADS)
		glVertex2f(self.rect.left-5, self.rect.top-5)
		glVertex2f(self.rect.right+5, self.rect.top-5)
		glVertex2f(self.rect.right+5, self.rect.bottom+5)
		glVertex2f(self.rect.left-5, self.rect.bottom+5)
		glEnd()
		
		#Cut off the last line if it's empty (which it almost always will be)
		buflen = len(self.buffer)
		if (self.buffer[-1] == "" and self.scroll == 0):
			buflen -= 1
		
		#Figure out how many lines of text we can fit, and how many we actually will draw
		drawinglines = min(buflen, self.dispsize())
		firstline = buflen-drawinglines-self.scroll
		
		#If there's extra blank space in the box, keep it at the top, not the bottom
		topoffset = self.rect.height - self.dispsize()*15
		
		#Draw each line (aligning to the bottom if there's fewer than dispsize() lines)
		glColor4f(1.0, 1.0, 1.0, 1.0)
		for x in range(drawinglines):
			#11 is the magic number for GLUT, for some reason
			glRasterPos2f(self.rect.left, self.rect.top + (self.dispsize()-drawinglines+x)*15 + topoffset + 11)
			for c in (self.buffer[firstline+x]):
				glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(c))
	
	def append(self, str):
		"""Adds new stuff to the OutputBox."""
		
		d = self.buffer
		origlen = len(d)
			
		#Add new lines to the list, without newline characters
		c = 0
		while True:
			next = str.find("\n", c)
			if next == -1:
				next = len(str)
			d[len(d)-1] += str[c:next]
			if next == len(str):
				break
			else:
				d.append("")
				c = next+1
		
		#Go back and wrap lines as needed (break anywhere, not just on spaces)
		x = origlen-1
		while x < len(d):
			if len(d[x])*9 > self.rect.width:
				for i in range(len(d[x])):
					if len(d[x][0:i])*9 > self.rect.width:
						d[x:(x+1)] = [d[x][0:(i-1)], d[x][(i-1):len(d[x])]]
			x += 1
		
		#Delete old lines past our maximum
		if len(d) > self.bufferlen+1:
			del d[0:(len(d)-(self.bufferlen+1))]
	
	def jump_top(self):
		"""Scrolls to the top of the OutputBox."""
		#Don't bother unless there's more than one screenful of information
		if (self.dispsize() >= len(self.buffer)):
			return
		self.scroll = len(self.buffer)-self.dispsize()
	
	def jump_bottom(self):
		"""Scrolls to the bottom of the OutputBox."""
		self.scroll = 0
	
	def scroll_up(self):
		"""Scrolls up one screenful."""
		#Don't bother unless there's more than one screenful of information
		if (self.dispsize() >= len(self.buffer)):
			return
		self.scroll = min(self.scroll+self.dispsize(), len(self.buffer)-self.dispsize())
	
	def scroll_down(self):
		"""Scrolls down one screenful."""
		self.scroll = max(self.scroll-self.dispsize(), 0)

class Console:
	"""An in-game debugging console.

	Activate and de-activate by providing ~ key (tilde key) events.

	PgUp and PgDn scroll through history. Shift+PgUp and Shift+PgDn jump to top and bottom of history.
	
	Data attributes:
	edit -- An EditBox used for inputting commands.
	out -- An OutputBox used to display command feedback and information.
	active -- If this is false, then the console never draws or accepts input.
	pseudofile -- The stdout/stderr redirection target (also sends to the real stderr).
	hist -- The command history (more recent commands have higher indices).
	histpos -- User's current index in the command history. If not in history, then is len(hist).
	intercons -- The InteractiveConsole.
	"""
	
	def __init__(self):
		"""Creates a Console. By default, the active flag is off."""
		self.active = 0
		self.hist = []
		self.histpos = 0
		self.intercons = code.InteractiveConsole(consenv.__dict__)
		self.out = OutputBox()
		self.pseudofile = PseudoOut(self.out)
		self.edit = EditBox()
		self.edit.prompt = ">>> "
		self.update_size() #Get OutputBox and EditBox sized to match the screen's resolution
	
	def update_size(self):
		"""Sets the EditBox and OutputBox rectangles to match the current window size."""
		self.edit.rect = pygame.Rect(20, app.winheight-30, app.winwidth-40, 15)
		self.out.rect = pygame.Rect(20, 20, app.winwidth-40, app.winheight-70)
	
	def draw(self):
		"""Draws the console. Nothing happens if the active flag is off."""
		if not self.active:
			return
		
		self.out.draw()
		self.edit.draw()
		
	def handle(self, event):
		"""Handles an event, if possible. Commands aren't accepted if the active flag is off."""
		if event.type != KEYDOWN:
			return
		
		if event.unicode == "~":
			if self.active == 1:
				self.active = 0
				pygame.key.set_repeat()
			else:
				self.active = 1
				pygame.key.set_repeat(400, 30)
				return
		
		if not self.active:
			return
		
		self.edit.handle(event)

		if event.key == K_UP:
			#Browse backwards in history
			if self.histpos > 0 and len(self.hist) > 0:
				self.histpos -= 1
				self.edit.cont = self.hist[self.histpos]
				self.edit.cursor = len(self.edit.cont)
		elif event.key == K_DOWN:
			#Browse forwards in history, clear box at end
			if self.histpos < len(self.hist)-1:
				self.histpos += 1
				self.edit.cont = self.hist[self.histpos]
				self.edit.cursor = len(self.edit.cont)
			elif self.histpos == len(self.hist)-1:
				self.histpos += 1
				self.edit.clear()
		elif event.key == K_PAGEUP:
			if pygame.key.get_mods() & KMOD_SHIFT:
				self.out.jump_top()
			else:
				self.out.scroll_up()
		elif event.key == K_PAGEDOWN:
			if pygame.key.get_mods() & KMOD_SHIFT:
				self.out.jump_bottom()
			else:
				self.out.scroll_down()
		elif event.key == K_KP_ENTER or event.key == K_RETURN:
			#Clear the edit box
			cmd = self.edit.cont
			self.edit.clear()
			
			#Put the line that was just input into the output area (and thru stderr as well)
			print self.edit.prompt + cmd
			
			#Only put lines in the history that start commands and were different from the last command
			if self.edit.prompt == ">>> " and cmd != "" and (len(self.hist) == 0 or self.hist[-1] != cmd):
				self.hist.append(cmd)
			
			#Jump to the end of the history after every command
			self.histpos = len(self.hist)
			
			#If it's just a confused player, help them out a little
			cleaned = cmd.lower().strip()
			if cleaned == "help":
				print helphelp
				print quithelp
				return
			elif cleaned == "quit" or cleaned == "exit" or cleaned == "close":
				print quithelp
				return
			
			#Try and run the command, change prompt to request more input if needed
			res = self.intercons.push(cmd)
			if res == 1:
				self.edit.prompt = "... "
			else:
				self.edit.prompt = ">>> "
