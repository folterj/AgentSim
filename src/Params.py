from src.Constants import Constants


class Params:
	def __init__(self):
		self.world_size = (Constants.world_size, Constants.world_size)  # [m]
		self.time_acceleration = 1

	def copy_from(self, ant_params):
		self.world_size = ant_params.world_size
		self.time_acceleration = ant_params.time_acceleration
