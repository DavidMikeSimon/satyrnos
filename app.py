import pygame, ode, sys
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

import colors, console, resman, util

#The size of the display window in pixels
winwidth = None
winheight = None

#The PyGame screen (set in app.init())
screen = None

#Never draw at a faster rate than this (simulation runs at 100hz regardless)
#There's no point in setting this higher than 100, since nothing changes faster than that
maxfps = None

#The ODE simulation
odeworld = None
odespace = None

#Used in the main frame loop
clock = None

#All the various game objects (init() prepares this to have objects shoved in it)
objects = None

#The in-game debugging console
cons = None

#Location in meters where the display is centered
camera = None

#Number of pixels per game meter
#We always go for a 4x3 meter display, which works perfectly for 640x480, 800x600, and 1024x768
pixm = None

class QuitException:
	"""Raised when something wants the main loop to end."""
	pass
	

def disp_init():
	"""Initializes the backend of the game, creates a display window.

	You must call this before calling run() if you want anything to appear on-screen.
	"""
	
	global screen, clock, cons, winwidth, winheight, pixm, maxfps
	
	maxfps = 100
	winwidth = 1024
	winheight = 768
	pixm = winwidth/4
	
	pygame.init()
	pygame.display.set_caption('Satyrnose')
	pygame.mouse.set_visible(0)
	screen = pygame.display.set_mode((winwidth, winheight), DOUBLEBUF | OPENGL)
	
	clock = pygame.time.Clock()
	
	glViewport(0, 0, winwidth, winheight)
	gluOrtho2D(0.0, winwidth, winheight, 0.0)
	glClearColor(1.0, 1.0, 1.0, 0.0)
	glEnable(GL_BLEND)
	glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
	
	cons = console.Console()
	sys.stderr = cons.pseudofile
	sys.stdout = cons.pseudofile


def sim_init():
	"""Initializes the camera and simulation, including ODE.
	
	You must call this before calling run().
	"""
	
	global odeworld, odespace, objects, camera
	odeworld = ode.World()
	odeworld.setQuickStepNumIterations(10)
	odeworld.setERP(0.0) #Setting this to zero stops annoying shaking, can still set joint ERPs
	odespace = ode.HashSpace()
	objects = util.TrackerList()
	camera = (2, 1.5)


def disp_deinit():
	"""Deinitializes the backend, turns off the display window.

	You don't have to call this, it's enough to just let the program end.
	It might be handy if you want to close the window and open it again later, though.
	"""

	resman.unload_all()
	
	global screen, clock, cons, winwidth, winheight, pixm
	pygame.quit()
	screen = None
	clock = None
	cons = None
	winwidth = None
	winheight = None
	pixm = None
	sys.stderr = sys.__stderr__
	sys.stdin = sys.__stdin__


def sim_deinit():
	"""Deinitializes the camera and simulation, including ODE.

	You can call this and then call sim_init() again to forcibly clear the game state.
	Other than that, you don't need to call this.
	"""

	global odeworld, odespace, objects, camera
	odeworld = None
	odespace = None
	objects = None
	ode.CloseODE()
	camera = None


def _collision(contactgroup, geom1, geom2):
	"""Callback function to the collide method."""
	
	body1 = geom1.getBody()
	body2 = geom2.getBody()
	if (body1 == None and body2 == None):
		return
	
	contacts = ode.collide(geom1, geom2)
	
	for c in contacts:
		c.setMode(ode.ContactApprox1 | ode.ContactBounce)
		c.setBounce(0.2)
		c.setMu(5000)
		j = ode.ContactJoint(odeworld, contactgroup, c)
		j.attach(body1, body2)


def _sim_step():
	"""Runs one step of the simulation. This is 1/100th of a simulated second."""

	#Calculate collisions, run ODE
	contactgroup = ode.JointGroup() #A group for collision contact joints
	odespace.collide(contactgroup, _collision)
	odeworld.quickStep(0.01)
	contactgroup.empty()
		
	#Cancel non-2d activity, and load each GameObj's state with the new information ODE calculated
	for o in objects:
		if o.body != None:
			o.sync_ode()

	#Have each object do any simulation stuff it needs (this includes calling do() on controllers)
	for o in objects:
		o.sim()

def _proc_input():
	"""Looks for input from the keyboard/joystick/etc, does the appropriate thing.
	
	Throws a QuitException if user has requested that the game quit.
	"""
		
	#Collect keyboard events
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			raise QuitException
		
		if event.type == KEYDOWN:
			cons.handle(event)
			if cons.active == 0:
				if event.key == K_w:
					objects[1].body.addForce((0, -10, 0))
				elif event.key == K_a:
					objects[1].body.addForce((-10, 0, 0))
				elif event.key == K_s:
					objects[1].body.addForce((0, 10, 0))
				elif event.key == K_d:
					objects[1].body.addForce((10, 0, 0))
				elif event.key == K_c:
					objects[1].body.addForce((100, 0, 0))
				elif event.key == K_q:
					objects[1].body.addTorque((0, 0, -2))
				elif event.key == K_e:
					objects[1].body.addTorque((0, 0, 2))
				elif event.key == K_r:
					objects[1].ang -= 0.1
				elif event.key == K_f:
					objects[1].ang += 0.1
				elif event.key == K_z:
					objects[6].body.addTorque((0, 0, -50))
				elif event.key == K_x:
					objects[6].body.addTorque((0, 0, 50))

def run(maxsteps = 0):
	"""Runs the game. Returns the number of steps ran.
	
	If given a non-zero argument, only runs for the given number of
	simulation steps. To make it run for 5 seconds, pass a value of 500.
	
	Before running this function, you have to have called app.sim_init().
	You also can call app.disp_init() first if you want anything to appear
	on-screen; otherwise, the simulation runs as quickly as possible. If
	you have not called app.disp_init(), then the maxsteps argument is
	required.
	"""
	
	#Weird case: The display is down, so we're running as an invisible simulation, quick as possible
	if not maxfps:
		if maxsteps == 0:
			raise NotImplementedError, "If display isn't initialized via app.disp_init(), then you must pass a maximum number of steps to app.run()"
		for i in range(maxsteps):
			_sim_step()
		return maxsteps

	#Normal case: The display is up, and we're running the game as a game
	totalsteps = 0L    #Number of simulation steps we've ran
	totalms = 0L       #Total number of milliseconds passed
	willquit = 0       #Becomes 1 when we're ready to quit
	while not willquit:
		elapsedms = clock.tick(maxfps)
		totalms += elapsedms
		
		#Figure out how many simulation steps we're doing this frame.
		#It should be one for every 100th of a second that has passed.
		#We do it this way, instead of dividing elapsedms by 10, because
		#if we did it that way, 4 frames in a row each 5ms long would
		#cause no sim_steps to be ran, instead of 2.
		steps = (totalms - totalsteps*10)/10
		
		#If we have a maximum number of steps, only go up to that amount
		if maxsteps != 0 and steps + totalsteps > maxsteps:
			steps = maxsteps - totalsteps
		
		#Run the simulation the desired number of steps
		totalsteps += steps
		for i in range(steps):
			_sim_step()
		
		#Deal with input from the player, quit if requested
		try:
			_proc_input()
		except QuitException:
			willquit = 1
		
		#Draw everything, if the display is enabled
		if (maxfps):
			glClear(GL_COLOR_BUFFER_BIT)
			glPushMatrix()
			glTranslatef(winwidth/2 - camera[0]*pixm, winheight/2 - camera[1]*pixm, 0)
			glScalef(pixm, pixm, 0) #OpenGL units are now game meters, not pixels
			for o in objects:
				o.draw()
			glPopMatrix()
			cons.draw()
			glFlush()
			pygame.display.flip()
		
		#If a limited-time simulation was requested, and we're done, then we're done
		if maxsteps != 0 and totalsteps == maxsteps:
			break
			
	return totalsteps
