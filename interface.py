from __future__ import division
import sys, pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import console, resman, app
from geometry import *

class Interface:
	"""Represents the window used to draw the game, including A/V and user input.
	
	If you want anything interactive to happen, be sure to call 'app.ui.open()'
	before calling 'app.run()'. With the Interface opened, the game runs
	normally and interactively. With the interface closed, Satyrnose tries
	to arrive at a final state (after a specified number of steps) as quickly
	as possible.
	
	Data attributes:
	opened -- If True, then everything else in the class is ready for use.
	winsize -- The size of the display window in pixels.
	winmeters -- The size of the display window in meters.
	screen -- The PyGame screen.
	maxfps -- The maximum frames-per-second that we will draw at.
	   This is also the maximum number of steps per second we
		run at, so changing this value will change the simulation
		as well as the display.
	clock -- An instance of pygame.time.Clock() used for timing.
		Do not call get_time() on this, use the 'msecs' variable instead.
	msecs -- The reuslt of the last call to clock.get_time(). Use this
		instead of calling clock.get_time() from a drive's draw() or
		predraw(), since that way time spent drawing or predrawing
		doesn't screw up calculations.
	pixm -- Number of screen pixels per game meter.
		We always try and go for a 4x3 meter display.
	draw_hulls -- If set to True, then GameObj's draw method also calls draw() on geom Hulls.
	cons -- An instance of console.Console used for in-game debugging.
	watchers -- A sequence of console.Watchers used for in-game debugging.
	camera -- Where, in game meters, the view is centered.
	"""
	
	def __init__(self):
		"""Sets all the data attributes to default values.
		
		After creating a Display, you'll have to call open() on it to
		have it make a window where you can actually display things.
		Before you do that, the 'screen', 'clock', 'cons', and 'watchers'
		data attributes shouldn't be accessed."""
		
		self.opened = False
		self.winsize = Size(1024, 768)
		self.winmeters = Size(4, 3) #Shouldn't ever be changed
		self.maxfps = 60
		self.pixm = self.winsize[0]/4
		self.camera = Point()
		self.screen = None
		self.clock = None
		self.draw_hulls = False
		self.cons = None
		self.msecs = 0
		self.watchers = []
	
	def open(self):
		"""Initializes PyGame and GL, creates a display window.
		
		Additionally, this creates a console.Console and directs
		standard out and standard error to it, and also
		creates some console.Watchers in the watchers sequence."""
		
		if not self.opened:
			self.opened = True
			
			pygame.init()
			pygame.display.set_caption('Satyrnose')
			pygame.mouse.set_visible(0)
			self.screen = pygame.display.set_mode(self.winsize, DOUBLEBUF | OPENGL)
			self.clock = pygame.time.Clock()
			
			glutInit(sys.argv) #Since we don't use GLUT for anything but drawing text, cmd line arguments are ignored anyways
			
			glViewport(0, 0, self.winsize[0], self.winsize[1])
			gluOrtho2D(0.0, self.winsize[0], self.winsize[1], 0.0) #This way makes the y-axis go in the direction we want
			glClearColor(1.0, 1.0, 1.0, 0.0)
			glEnable(GL_BLEND)
			glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
			
			# Enable antialiasing
			#glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)
			#glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
			#glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)
			glEnable(GL_POINT_SMOOTH)
			glEnable(GL_LINE_SMOOTH)
			glEnable(GL_POLYGON_SMOOTH)
			
#			glShadeModel(GL_SMOOTH)
#			glLightfv(GL_LIGHT0, GL_POSITION, (1.0, 1.0, 1.0, 0.0))
#			glLightfv(GL_LIGHT0, GL_DIFFUSE, (1.0, 1.0, 0.3, 1.0))
#			glLightfv(GL_LIGHT0, GL_SPECULAR, (1.0, 1.0, 0.3, 1.0))
#			glLightfv(GL_LIGHT0, GL_QUADRATIC_ATTENUATION, 0.5)
#			glLightModelfv(GL_LIGHT_MODEL_LOCAL_VIEWER, (0.1, 0.1, 0.1, 1.0))
#			
#			glEnable(GL_LIGHTING)
#			glEnable(GL_LIGHT0)
#			glEnable(GL_COLOR_MATERIAL)
#			glColorMaterial(GL_FRONT, GL_DIFFUSE)

			glPointSize(4)
			glLineWidth(2)
			
			self.cons = console.Console()
			self.watchers = []
			sys.stderr = self.cons.pseudofile
			sys.stdout = self.cons.pseudofile
			self.watchers.append(console.Watcher(pygame.Rect(20, self.winsize[1]/3-30, self.winsize[0]/4, self.winsize[1]/3-20)))
			self.watchers.append(console.Watcher(pygame.Rect(20, 2*self.winsize[1]/3-30, self.winsize[0]/4, self.winsize[1]/3-20)))
			self.watchers.append(console.Watcher(pygame.Rect(3*self.winsize[0]/4 - 20, self.winsize[1]/3-30, self.winsize[0]/4, self.winsize[1]/3-20)))
			self.watchers.append(console.Watcher(pygame.Rect(3*self.winsize[0]/4 - 20, 2*self.winsize[1]/3-30, self.winsize[0]/4, self.winsize[1]/3-20)))
		
	def draw_frame(self, objects):
		"""Draws one frame based on the list of objects passed.
		
		This also resets the msecs data attribute."""
		
		self.msecs = self.clock.get_time()
		
		glClear(GL_COLOR_BUFFER_BIT)
		
		glPushMatrix()
		glScalef(self.pixm, self.pixm, 0) #OpenGL units are now game meters, not pixels
		
		#Mostly, this is used for setting the camera's position
		for o in objects:
			o.predraw()
		
		#Translate so that camera position is centered
		glTranslatef(self.winsize[0]/(2*self.pixm) - self.camera[0], self.winsize[1]/(2*self.pixm) - self.camera[1], 0)

		#This actually draws the objects
		for o in objects:
			o.draw()
		
		glPopMatrix()
		
		for w in self.watchers:
			if (w.expr != None):
				w.update()
				w.draw()
		
		self.cons.draw()
		
		glFlush()
		pygame.display.flip()
	
	def proc_input(self):
		"""Looks for input from the keyboard/joystick/etc, does the appropriate thing.
	
		Throws an app.QuitException if user has requested that the game quit.
		"""
		#Collect keyboard events
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				raise app.QuitException
			
			if event.type == KEYDOWN:
				self.cons.handle(event)
				if self.cons.active == 0:
					if event.key == K_w:
						app.objects[3][0].body.addForce((0, -20, 0))
					elif event.key == K_a:
						app.objects[3][0].body.addForce((-20, 0, 0))
					elif event.key == K_s:
						app.objects[3][0].body.addForce((0, 20, 0))
					elif event.key == K_d:
						app.objects[3][0].body.addForce((20, 0, 0))
					elif event.key == K_c:
						app.objects[3][0].body.addForce((200, 0, 0))
					elif event.key == K_q:
						app.objects[3][0].body.addTorque((0, 0, -4))
					elif event.key == K_e:
						app.objects[3][0].body.addTorque((0, 0, 4))
					elif event.key == K_r:
						app.objects[2][0].body.addTorque((0, 0, 40))
					elif event.key == K_f:
						app.objects[2][0].freeze()
						app.objects[3][0].freeze()
					elif event.key == K_t:
						app.objects[3][0].pos = Point(2.5, 1)
					elif event.key == K_p:
						app.objects[2][2].drives[0].playing = not app.objects[2][2].drives[0].playing
	
	def close(self):
		"""If display window is open, destroys all data attributes and closes the display window.
		
		This will be automatically called by the destructor if the object is GC collected
		while the display window is still open. If you want any control over when the display
		is closed, though, you'd better call this method yourself.
		
		This method also destroys the Console and Watchers, and
		redirects stdout and stderr back to their default settings.
		"""
		
		if self.opened:
			self.opened = False
			resman.unload_all()
			pygame.quit()
			
			self.screen = None
			self.clock = None
			self.cons = None
			self.msecs = 0
			self.watchers = []
			
			sys.stderr = sys.__stderr__
			sys.stdout = sys.__stdout__
	
	def __del__(self):
		try:
			self.close()
		except:
			print "Exited with error."

	
