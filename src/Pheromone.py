import math
import numpy as np

from src.Constants import Constants
from src.DObject import DObject
from src.util import world_to_map


class Pheromone(DObject):
    def __init__(self, label, position):
        super().__init__(position)
        self.label = label
        self.decay_time = 0
        self.max_detect_range = 0
        self.age = 0
        self.active = True
        self.activity = 1
        self.detect_range = self.max_detect_range

        self.set_values()
        self.detect_range = self.max_detect_range
        self.age = 0
        self.active = True
        self.activity = 1

    def set_values(self):
        values = Constants.pheromones[self.label]
        self.decay_time = values['decay_time']
        self.max_detect_range = values['max_detect_range']
        self.action = values['action']

    def add_to_map(self, map):
        position0 = self.position
        if self.detect_range > 0:
            detect_range = int(round(self.detect_range))
            for y in range(-detect_range, detect_range):
                for x in range(-detect_range, detect_range):
                    position = np.flip(np.array(world_to_map(position0)) + [x, y])
                    if 0 <= position[0] < map[0] and 0 <= position[1] < map[1]:
                        map[tuple(position)] = self.activity
        else:
            map[world_to_map(position0)] = self.activity

    def update(self, dage, map):
        self.age += dage
        self.activity = math.exp(-self.age / self.decay_time)
        self.detect_range = self.max_detect_range * self.activity
        self.active = self.age < 5 * self.decay_time  # 5 * Tau
