import math

from src.DObject import DObject


class Pheromone(DObject):
    def __init__(self, position, values):
        super().__init__(position)
        self.decay_time = 0
        self.max_detect_range = 0
        self.age = 0
        self.active = True
        self.activity = 1
        self.detect_range = self.max_detect_range

        self.set_values(values)
        self.detect_range = self.max_detect_range
        self.age = 0
        self.active = True
        self.activity = 1

    def set_values(self, values):
        self.decay_time = values['decay_time']
        self.max_detect_range = values['max_detect_range']
        self.action = values['action']

    def update(self, dage):
        self.age += dage
        self.activity = math.exp(-self.age / self.decay_time)
        self.detect_range = self.max_detect_range * self.activity
        self.active = self.age < 5 * self.decay_time  # 5 * Tau
