import numpy as np

from src.Constants import Constants


class Params:
	def __init__(self, map_size):
		self.map_size = map_size
		self.world_size = np.array(Constants.world_size) * map_size / (max(map_size), max(map_size))
		self.time_speed = 1

	def world_to_map(self, position, reverse=False):
		position = np.array(position)
		map_position = np.round(position / self.world_size * self.map_size).astype(int)
		if reverse:
			map_position = np.flip(map_position)
		if position.ndim < 1:
			return map_position[0]
		else:
			return tuple(map_position.tolist())

	def map_to_world(self, map_position, reverse=False):
		if reverse:
			map_position = np.flip(map_position)
		return np.asarray(map_position) / self.map_size * self.world_size
