import cv2 as cv
import math
import numpy as np

from src.Constants import Constants
from src.DObject import DObject


class Pheromone(DObject):
    def __init__(self, label, position, params):
        super().__init__(position)
        self.label = label
        self.params = params
        self.decay_time = 0
        self.max_detect_range = 0
        self.age = 0
        self.active = True
        self.activity = 1

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
        # increment map value
        if self.detect_range > 0:
            position = self.params.world_to_map(self.position)
            rad = self.params.world_to_map(self.detect_range)
            value = self.activity
            # TODO: increment instead of set (using addWeighted?):
            cv.circle(map, position, rad, value, cv.FILLED)
        else:
            position = self.params.world_to_map(self.position, reverse=True)
            map[position] += self.activity

    def update(self, dage, map):
        self.age += dage
        self.activity = math.exp(-self.age / self.decay_time)
        self.detect_range = self.max_detect_range * self.activity
        self.active = self.age < 5 * self.decay_time  # 5 * Tau
