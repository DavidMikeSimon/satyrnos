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
import interface
from util import *

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
