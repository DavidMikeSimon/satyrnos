#This is where the debugging console runs 

import sys
import math
import os

import ode
import pygame
import pydoc
from pygame.locals import *

import app
import colors
import console
import gameobj
import resman
import camera
import drive
import image
import background
import magnet
from util import *

class Watcher(console.OutputBox):
	"""Displays continually-updated information to an on-screen debugging window.
	
	Caller is expected to make sure that expr is non-Null before calling update().
	
	Data attributes:
	expr -- Runs this expression on each call to update(), sets buffer to the result.
	"""
	def __init__(self, rect = None, expr = None):
		console.OutputBox.__init__(self, rect)
		self.expr = expr
		self.bufferlen = self.dispsize()
	
	def update(self):
		self.clear()
		try:
			self.append(self.expr + ":\n\n" + repr(eval(self.expr)))
		except:
			self.append("EXCEPTION")
			
#These Watchers will be set up in app.disp_init() and drawn from app.run()
wa = None
wb = None
wc = None
wd = None

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
