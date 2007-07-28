from __future__ import division
import ode, sys, math, pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import collision, util, console, resman, app
from geometry import *

#The ODE simulation
odeworld = None
static_space = None
dyn_space = None

#All the various game objects in a LayeredList (sim_init() prepares this to have objects shoved in it)
objects = None

#Input events (from PyGame) which occurred this step
events = []

#Keys which were pressed at the time 'events' was compiled
keys = []

winsize = Size(1024, 768) #Size of the display window in pixels; TODO: should be a user setting
winmeters = Size(4, 3) #Size of the display window in meters
maxfps = 60 #Max frames per second, and absolute sim-steps per second
pixm = winsize[0]/winmeters[0] #Number of screen pixels per game meter
camera = Point() #Where, in game meters, the view is centered
screen = None #The PyGame screen
clock = None #An instance of pygame.time.Clock() used for timing; use step count, not this for game-logic timing
msecs = 0 #TODO: Make sure everything uses step counters, not wall-clock time
draw_geoms = False #If True, then GameObjs and geom-related drives draw collision geom outlines
cons = None #An instances of console.Console used for in-game debugging
watchers = [] #A sequence of console.Watchers used for in-game debugging

class QuitException:
	"""Raised when something wants the main loop to end."""
	pass

def ui_init():
	global screen, clock, cons, watchers

	pygame.init()
	pygame.display.set_caption('Satyrnos')
	pygame.mouse.set_visible(0)
	screen = pygame.display.set_mode(winsize, DOUBLEBUF | OPENGL)
	clock = pygame.time.Clock()
	
	glutInit(sys.argv) # GLUT is only used for drawing text
	
	glViewport(0, 0, winsize[0], winsize[1])
	gluOrtho2D(0.0, winsize[0], winsize[1], 0.0) #This makes the y-axis go in the direction we want
	glClearColor(1.0, 1.0, 1.0, 0.0)
	glEnable(GL_BLEND)
	glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
	
	glEnable(GL_POINT_SMOOTH)
	glEnable(GL_LINE_SMOOTH)
	glEnable(GL_POLYGON_SMOOTH)
	
	glPointSize(4)
	glLineWidth(2)
	
	cons = console.Console()
	watchers = []
	sys.stderr = cons.pseudofile
	sys.stdout = cons.pseudofile
	watchers.append(console.Watcher(pygame.Rect(20, winsize[1]/3-30, winsize[0]/4, winsize[1]/3-20)))
	watchers.append(console.Watcher(pygame.Rect(20, 2*winsize[1]/3-30, winsize[0]/4, winsize[1]/3-20)))
	watchers.append(console.Watcher(pygame.Rect(3*winsize[0]/4 - 20, winsize[1]/3-30, winsize[0]/4, winsize[1]/3-20)))
	watchers.append(console.Watcher(pygame.Rect(3*winsize[0]/4 - 20, 2*winsize[1]/3-30, winsize[0]/4, winsize[1]/3-20)))

def ui_deinit():
	global screen, clock, cons, msec, watchers
	
	resman.unload_all()
	pygame.quit()
	
	screen = None
	clock = None
	cons = None
	msecs = 0
	watchers = []
	
	sys.stderr = sys.__stderr__
	sys.stdout = sys.__stdout__

def sim_init():
	"""Initializes the simulation, including ODE.
	
	You must call this before calling run().

	After calling this, app.objects will be a util.LayeredList(). Within,
	create 6 lists, all of which are either TrackerLists or LayeredLists.
	LayeredLists should always contain either more LayeredLists and/or TrackerLists,
	and TrackerLists should contain only GameObjs. This way, you can make everything
	as deep or shallow as you like, but the recursive behavior of LayeredList.append()
	will make sure that GameObjs that are created and stuffed into some top list will
	eventually arrive at the right place.
	
	The top-level layers of objects should be as follows:
	0 - Non-colliding background imagery, and general non-colliding GameObjs, without geoms
	1 - Static objects (walls, buttons affixed to the floor, etc) in space "static_space"
	2 - Non-player objects w/ physics (pushable blocks, enemies, etc) in space "dyn_space"
	3 - Player objects (there should really only be one of these) in space "dyn_space"
	4 - Foreground objects (dust particles, etc) in space "dyn_space" or without geoms
	5 - Non-colliding foreground imagery (close-up tree leaves, fog, etc), without geoms
	This way, drives can make reasonable guesses about where to append() newly created GameObjs.
	
	Objects in static_space do not collide with one another. Objects in dyn_space collide
	with those in static_space, as well as with each other.
	"""
	
	global odeworld, static_space, dyn_space, objects
	odeworld = ode.World()
	odeworld.setQuickStepNumIterations(10)
	static_space = ode.HashSpace()
	dyn_space = ode.HashSpace()
	objects = util.LayeredList()

def sim_deinit():
	"""Deinitializes the camera and simulation, including ODE.
	
	You can call this and then call sim_init() again to forcibly clear the game state.
	Other than that, you don't need to call this.
	"""

	global odeworld, static_space, dyn_space, objects
	odeworld = None
	static_space = None
	dyn_space = None
	objects = None
	ode.CloseODE()

def _sim_step():
	"""Runs one step of the simulation. This is (1/maxfps)th of a simulated second."""

	#Calculate collisions, run ODE simulation
	contactgroup = ode.JointGroup() #A group for collision contact joints
	dyn_space.collide(contactgroup, collision.collision_cb) #Collisions among dyn_space objects
	ode.collide2(dyn_space, static_space, contactgroup, collision.collision_cb) #Colls between dyn_space objects and static_space objs
	odeworld.quickStep(1/maxfps)
	contactgroup.empty()
		
	#Cancel non-2d activity, and load each GameObj's state with the new information ODE calculated
	for o in objects:
		if o.body != None:
			o.sync_ode()

	#Have each object do any simulation stuff it needs
	for o in objects:
		o.step()

def _draw_frame():
	global msecs
	msecs = clock.get_time()
	
	glClear(GL_COLOR_BUFFER_BIT)
	
	glPushMatrix()
	glScalef(pixm, pixm, 0) #OpenGL units are now game meters, not pixels
	
	#Mostly, this is used for setting the camera's position
	for o in objects:
		o.predraw()
	
	#Translate so that camera position is centered
	glTranslatef(winsize[0]/(2*pixm) - camera[0], winsize[1]/(2*pixm) - camera[1], 0)

	#This actually draws the objects
	for o in objects:
		o.draw()
	
	glPopMatrix()
	
	for w in watchers:
		if (w.expr != None):
			w.update()
			w.draw()
	
	cons.draw()
	
	glFlush()
	pygame.display.flip()

def _proc_input():
	global events, keys
	events = []
	for event in pygame.event.get():
		cons.handle(event)
		if event.type == pygame.QUIT:
			raise QuitException
		else:
			events.append(event)
	keys = pygame.key.get_pressed()

def run():
	"""Runs the game.
	
	You have to call ui_init() and sim_init() before running this.
	"""
	try:
		totalsteps = 0L    #Number of simulation steps we've ran
		totalms = 0L       #Total number of milliseconds passed
		while True:
			elapsedms = clock.tick(maxfps)
			
			if not cons.active:
				totalms += elapsedms
				
				#Figure out how many simulation steps we're doing this frame.
				#In theory, shouldn't be zero, since frames per second is the same as steps per second
				#However, it's alright to be occasionally zero, since clock.tick is sometimes slightly off
				steps = int(math.floor((totalms*maxfps/1000)))-totalsteps
				
				#Run the simulation the desired number of steps
				for i in range(steps):
					_proc_input()
					_sim_step()
				
				totalsteps += steps
			else:
				_proc_input()
			
			#Draw everything
			_draw_frame()
	except QuitException:
		pass
