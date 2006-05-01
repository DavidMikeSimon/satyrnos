#This is where the debugging console runs 

import sys
import math
import os

import ode
import pygame
import pydoc
from pygame.locals import *

import app
import background
import camera
import colors
import console
import drive
import gameobj
import image
import interface
import magnet
import resman
from util import *

def wset(num, expr):
	"""Shortcut for 'app.ui.watchers[num].expr = expr'."""
	app.ui.watchers[num].expr = expr
	
def wclear(num = -1):
	"""Clears all Watchers in app.ui.watchers, or just the specified one."""
	if num == -1:
		for w in app.ui.watchers:
			w.expr = None
	else:
		app.ui.watchers[num].expr = None

def wfps(num = 0):
	"""Sets a given watcher (#0 by default) to show the FPS."""
	app.ui.watchers[num].expr = "app.ui.clock"

class ConsDoc(pydoc.TextDoc):
	#The regular bolder tries to replace X with X<BKSP>X
	#That doesn't work very well for the debugging console output
	def bold(self, text):
		return text

def help(tgt = None):
	if tgt == None:
		print console.helphelp
	else:
		print ConsDoc().document(tgt).strip()

def quit():
	print console.quithelp

def exit():
	print console.quithelp

def close():
	print console.quithelp
