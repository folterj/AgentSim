import math

from src.DObject import DObject


class Pheromone(DObject):
    def __init__(self, position=None):
        super().__init__(position)
        self.decay_time = 0
        self.max_detect_range = 0
        self.age = 0
        self.active = True
        self.activity = 1
        self.detect_range = self.max_detect_range

        if position is not None:
            self.set_values()
            self.detect_range = self.max_detect_range
            self.age = 0
            self.active = True
            self.activity = 1

    def set_values(self):
        self.decay_time = 0
        self.max_detect_range = 0

    def update(self, dage):
        self.age += dage
        self.activity = math.exp(-self.age / self.decay_time)
        self.detect_range = self.max_detect_range * self.activity
        self.active = self.age < 5 * self.decay_time  # 5 * Tau


class TrailPheromone(Pheromone):
    def __init__(self, position=None):
        super().__init__(position)

    def set_values(self):
        self.decay_time = 10 * 60 * 60  # (48 / 5 = 10 hours)
        self.max_detect_range = 10.0 / 1000  # (1 cm)


class RecruitPheromone(Pheromone):
    def __init__(self, position=None):
        super().__init__(position)

    def set_values(self):
        self.decay_time = 4 * 60  # (20 / 5 = 4 min)
        self.max_detect_range = 10.0 / 1000  # (1 cm)


class AlarmPheromone(Pheromone):
    def __init__(self, position=None):
        super().__init__(position)

    def set_values(self):
        self.decay_time = 1 * 60  # (1 min)
        self.max_detect_range = 100.0 / 1000  # (10 cm)
