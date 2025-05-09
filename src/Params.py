import numpy as np

from src.Constants import Constants


class Params:
	def __init__(self):
		self.map_factor = 1 / Constants.agent_size
		self.time_speed = 1

	def world_to_map(self, position, reverse=False):
		position = np.array(position)
		map_position = np.round(position * self.map_factor).astype(int)
		if reverse:
			map_position = np.flip(map_position)
		if position.ndim >= 1:
			return tuple(map_position.tolist())
		else:
			return map_position

	def map_to_world(self, map_position, reverse=False):
		if reverse:
			map_position = np.flip(map_position)
		return np.asarray(map_position) / self.map_factor
