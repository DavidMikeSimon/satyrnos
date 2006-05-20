import ode, sys

import util, interface

#The ODE simulation
odeworld = None
odespace = None

#All the various game objects in a LayeredList (init() prepares this to have objects shoved in it)
objects = None

#Call this thing's open() method to actually show anything onscreen
ui = interface.Interface()

class QuitException:
	"""Raised when something wants the main loop to end."""
	pass

def sim_init():
	"""Initializes the simulation, including ODE.
	
	You must call this before calling run().

	After calling this, app.objects will be a util.LayeredList(). Within,
	create a bunch of TrackerLists, one for each drawing layer. Within those, put
	GameObjs. You can create multiple levels of LayeredLists if you wish, but
	the "leaf" lists should always be TrackerLists of GameObjs.
	"""
	
	global odeworld, odespace, objects
	odeworld = ode.World()
	odeworld.setQuickStepNumIterations(10)
	odeworld.setERP(0.1)
	odespace = ode.HashSpace()
	objects = util.LayeredList()

def sim_deinit():
	"""Deinitializes the camera and simulation, including ODE.

	You can call this and then call sim_init() again to forcibly clear the game state.
	Other than that, you don't need to call this.
	"""

	global odeworld, odespace, objects
	odeworld = None
	odespace = None
	objects = None
	ode.CloseODE()

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

	#Have each object do any simulation stuff it needs (this includes calling do() on drives)
	for o in objects:
		o.step()


def run(maxsteps = 0):
	"""Runs the game. Returns the number of steps ran.
	
	If given a non-zero argument, only runs for the given number of
	simulation steps. To make it run for 5 seconds, pass a value of 500.
	
	Before running this function, you have to have called app.sim_init().
	You also can call app.ui.open()() first if you want anything to appear
	on-screen; otherwise, the simulation runs as quickly as possible. If
	you have not called app.ui.open(), then the maxsteps argument is
	required.
	"""
	
	#Weird case: The display is down, so we're running as an invisible simulation, quick as possible
	if not ui.opened:
		if maxsteps == 0:
			raise NotImplementedError, "If display isn't initialized via app.ui.open(), then you must pass a maximum number of steps to app.run()"
		for i in range(maxsteps):
			_sim_step()
		return maxsteps

	#Normal case: The display is up, and we're running the game as a game
	totalsteps = 0L    #Number of simulation steps we've ran
	totalms = 0L       #Total number of milliseconds passed
	willquit = 0       #Becomes 1 when we're ready to quit
	while not willquit:
		elapsedms = ui.clock.tick(ui.maxfps)
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
			ui.proc_input(objects)
		except QuitException:
			willquit = 1
		
		#Draw everything, if the display is enabled
		if (ui.opened):
			ui.draw_frame(objects)
		
		#If a limited-time simulation was requested, and we're done, then we're done
		if maxsteps != 0 and totalsteps == maxsteps:
			break
			
	return totalsteps
