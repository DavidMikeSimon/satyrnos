import drive

class DEnvJoint(drive.Drive):
	"""Drive that manages a joint between the GameObj and the static environment.

	When this drive is created, the provided joint should already be correctly attached.

	This is officially the least exciting or interesting Drive.
	
	Data attributes:
	joint -- The ODE joint.
	"""
	
	def __init__(self, joint):
		super(DEnvJoint, self).__init__() #Nothing propogated
		self.joint = joint
