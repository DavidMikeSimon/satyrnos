from __future__ import division
import ode, sys, math

import collision, util, interface

#The ODE simulation
odeworld = None
static_space = None
dyn_space = None

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
	6 - Light (a single GameObj with a single DLightField drive)
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
	"""Runs one step of the simulation. This is 1/60th of a simulated second."""

	#Calculate collisions, run ODE simulation
	contactgroup = ode.JointGroup() #A group for collision contact joints
	dyn_space.collide(contactgroup, collision.collision_cb) #Collisions among dyn_space objects
	ode.collide2(dyn_space, static_space, contactgroup, collision.collision_cb) #Colls between dyn_space objects and static_space objs
	odeworld.quickStep(0.01)
	contactgroup.empty()
		
	#Cancel non-2d activity, and load each GameObj's state with the new information ODE calculated
	for o in objects:
		if o.body != None:
			o.sync_ode()

	#Have each object do any simulation stuff it needs
	for o in objects:
		o.step()


def run(maxsteps = 0):
	"""Runs the game. Returns the number of steps ran.
	
	If given a non-zero argument, only runs for the given number of
	simulation steps. To make it run for 5 seconds, pass a value of 500.
	
	Before running this function, you have to have called app.sim_init().
	You also can call app.ui.open() first if you want anything to appear
	on-screen; otherwise, the simulation runs as quickly as possible. If
	you have not called app.ui.open(), then the maxsteps argument is
	required.
	"""
	
	#Weird case: The display is down, so we're running as an invisible simulation, quick as possible
	if not ui.opened:
		if maxsteps == 0:
			raise NotImplementedError, "If display isn't initialized via app.ui.open(), you must pass a maximum number of steps to app.run()"
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
		#Shouldn't be zero, since frames per second is the same as steps per second
		#However, it's alright to be occasionally zero, since clock.tick is sometimes slightly off
		steps = int(math.floor((totalms*ui.maxfps/1000)))-totalsteps
		
		#If we have a maximum number of steps, only go up to that amount
		if maxsteps != 0 and steps + totalsteps > maxsteps:
			steps = maxsteps - totalsteps
		
		#Run the simulation the desired number of steps
		for i in range(steps):
			_sim_step()
		totalsteps += steps
		
		#Deal with input from the player, quit if requested
		try:
			ui.proc_input()
		except QuitException:
			willquit = 1
		
		#Draw everything, if the display is enabled
		if (ui.opened):
			ui.draw_frame(objects)
		
		#If a limited-time simulation was requested, and we're done, then we're done
		if maxsteps != 0 and totalsteps == maxsteps:
			break
			
	return totalsteps
