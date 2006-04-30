import app, util, drive

class DCameraFollow(drive.Drive):
	"""Drive that changes app.camera to keep the object centered, without going outside bounds.
	
	Don't have more than one camera drive active at once.
	
	Data attributes:
	boundlist -- A list of rectangles that the camera's center will be restricted to. If there any boxes
		then the camera will refuse to go anywhere where it isn't in at least one of the boxes.
		If the list is empty, then the camera can go anywhere. The rectangles are specified
		as ((pos), (size)).
	"""
	
	def __init__(self, boundlist = []):
		super(DCameraFollow, self).__init__(True, False)
		self.boundlist = boundlist
	
	def _predraw(self, obj):
		app.ui.camera = obj.pos