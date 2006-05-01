from __future__ import division
import app, util, drive

class DCameraFollow(drive.Drive):
	"""Drive that changes app.camera to keep the object centered, without going outside bounds.
	
	Don't have more than one camera drive active at once.
	
	Data attributes:
	boundlist -- A list of rectangles that the camera's center will be restricted to. If boundlist
		is not empty,  then the camera won't go anywhere where it isn't centered in at least one of them.
		If the list is empty, then the camera can go anywhere. The rectangles are specified
		as ((pos), (size)).
	rate -- How much (0.0-1.0) to move the camera's real position to its destination.
		If negative, camera moves instantly
	"""
	
	def __init__(self, boundlist = [], rate = -1):
		super(DCameraFollow, self).__init__(True, False)
		self.boundlist = boundlist
		self.rate = rate
	
	def _predraw(self, obj):
		dest = (0, 0)
		if len(self.boundlist) == 0:
			dest = obj.pos
		else:
			ndist = -1
			nearest = None
			for box in self.boundlist:	
				cand = util.nearest_in_box(box[0], box[1], 0, obj.pos)
				cdist = util.dist(cand, obj.pos)
				if ndist == -1 or cdist < ndist:
					nearest = cand
					ndist = cdist
			dest = nearest
		
		if self.rate < 0:
			app.ui.camera = dest
		else:
			newcam = [0, 0]
			for axis in range(0, 2):
				newcam[axis] = app.ui.camera[axis] + (dest[axis] - app.ui.camera[axis])*self.rate*(app.ui.clock.get_time()/1000)
				#print "AXIS " + repr(newcam[axis])
			#print "NEWCAM IS " + repr(newcam)
			#print "--"
			app.ui.camera = (newcam[0], newcam[1])
		