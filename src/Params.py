from src.Constants import Constants


class Params:
	def __init__(self):
		self.world_size = (Constants.world_size, Constants.world_size)  # [m]
		self.time_speed = 1

	def copy_from(self, params):
		self.world_size = params.world_size
		self.time_speed = params.time_speed
