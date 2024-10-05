import math
import numpy as np


class DObject:
	def __init__(self, position=None):
		if position is None:
			self.position = np.array([0, 0])
		else:
			self.position = np.array(position)
		self.detect_range = 0

	def calc_distance(self, position):
		return math.dist(self.position, position)

	def calc_detection(self, position):
		# 1 : 100% detection
		# -x ... 0 : 0% detection
		return (self.detect_range - self.calc_distance(position)) / self.detect_range
