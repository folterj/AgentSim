import math
import numpy as np
import random

from src.AgentMode import AgentMode
from src.Constants import Constants
from src.DObject import DObject
from src.Pheromone import Pheromone
from src.util import calc_angle, smallest_angle_dif


class Agent(DObject):
    def __init__(self, position, params):
        super().__init__(position)
        self.params = params
        self.angle = 0
        self.direction = np.array([0, 0])
        self.trajectory = np.array([0, 0])
        self.trajectory_update_weight = 0.1
        self.speed = 0
        self.distance_last_pheromone = 0
        self.energy = 0
        self.food_amount = 0
        self.steps_from_nest = 0
        self.ignore_pheromone_steps = 0
        self.mode = AgentMode.Idle
        self.position = np.array(position)
        self.init()

    def init(self):
        self.detect_range = 0
        self.mode = AgentMode.Idle
        self.distance_last_pheromone = 0
        self.energy = Constants.total_energy
        self.food_amount = 0
        self.speed = Constants.norm_speed
        self.angle = 0
        self.steps_from_nest = 0

    def get_move_distance(self):
        return self.speed * Constants.update_time

    def calc_destination(self, new_direction=None):
        destination = None
        if new_direction is None:
            new_direction = np.array(self.direction)
        if self.mode not in [AgentMode.Idle, AgentMode.Eat, AgentMode.Dead]:
            distance_moved = self.speed * Constants.update_time
            destination = self.position + (new_direction * distance_moved)
        return destination

    def set_mode(self, mode):
        if mode == self.mode:
            return
        if mode in [AgentMode.Idle, AgentMode.Eat, AgentMode.Dead]:
            self.speed = 0
            self.angle = 0
        elif mode == AgentMode.Scout:
            self.speed = Constants.norm_speed
            self.angle = random.random() * 360
            self.update_direction()
        elif mode == AgentMode.Recruit:
            self.speed = Constants.norm_speed
            if self.mode == AgentMode.Eat:
                self.turn_around()
        elif mode in [AgentMode.Distress]:
            self.speed = Constants.alarm_speed
        self.mode = mode

    def choose_pheromone(self, pheromones):
        candidates = []
        trajectory_angle = calc_angle(self.trajectory)
        for pheromone in pheromones:
            # interest in pheromone depends on the mode
            if not self.mode == AgentMode.Scout or not pheromone.label == 'trail':
                distance = self.calc_distance(pheromone.position)
                if distance > 0:
                    angle = smallest_angle_dif(calc_angle(self.position, pheromone.position), trajectory_angle)
                    if abs(angle) <= 60:
                        candidates.append((distance, pheromone))
        if candidates:
            if len(candidates) == 1:
                best_candidate = candidates[0]
            else:
                best_candidate = min(candidates, key=lambda candidate: candidate[0])
            return best_candidate[1]
        return None

    def update(self, target_direction):
        new_pheromone = None
        distance_moved = 0
        has_target = (target_direction[0] != 0 or target_direction[1] != 0)

        if self.mode not in [AgentMode.Idle, AgentMode.Dead, AgentMode.Eat]:
            distance_moved = self.get_move_distance()
            self.position += self.direction * distance_moved
            self.energy -= distance_moved
            if self.energy <= 0:
                self.energy = 0
                self.mode = AgentMode.Dead
                self.speed = 0
            if self.ignore_pheromone_steps > 0:
                self.ignore_pheromone_steps -= 1

        if self.mode == AgentMode.Scout:
            if self.energy < Constants.trail_energy:
                self.turn_around()
                self.mode = AgentMode.Return
            else:
                self.steps_from_nest += 1
                if has_target:
                    self.angle = calc_angle(target_direction)
                    self.update_direction()
                else:
                    self.vary_direction(1)
                self.distance_last_pheromone = 0
                new_pheromone = Pheromone('trail', self.position, self.params)

        elif self.mode == AgentMode.Distress:
            new_pheromone = Pheromone('alarm', self.position, self.params)

        elif self.mode == AgentMode.Recruit:
            new_pheromone = Pheromone('recruit', self.position, self.params)

        else:
            if has_target:
                self.direction = np.array(target_direction)
                self.update_angle()
            if self.distance_last_pheromone > Constants.trail_create_distance and not self.is_ignoring_pheromones():
                new_pheromone = Pheromone('trail', self.position, self.params)

        if new_pheromone is not None:
            if self.distance_last_pheromone > new_pheromone.detect_range and not self.is_ignoring_pheromones():
                self.distance_last_pheromone = 0
            else:
                self.distance_last_pheromone += distance_moved
        return new_pheromone

    def ignore_pheromones(self):
        self.ignore_pheromone_steps = 5

    def is_ignoring_pheromones(self):
        return self.ignore_pheromone_steps > 0

    def update_direction(self):
        self.check_angle()
        self.direction = np.array([math.cos(math.radians(self.angle)), math.sin(math.radians(self.angle))])
        self.trajectory = (self.trajectory_update_weight * self.direction
                        + (1 - self.trajectory_update_weight) * self.trajectory)

    def update_angle(self):
        self.angle = calc_angle(self.direction)

    def vary_direction(self, angle_variation):
        self.angle += (random.random() - 0.5) * 2 * angle_variation
        self.update_direction()

    def turn_around(self):
        new_trajectory = -self.trajectory
        self.trajectory = new_trajectory
        self.direction = new_trajectory
        self.angle = calc_angle(new_trajectory)

    def check_angle(self):
        while self.angle < -360:
            self.angle += 360
        while self.angle > 360:
            self.angle -= 360
