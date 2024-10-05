import math
import numpy as np
import random

from src.AgentMode import AgentMode
from src.Constants import Constants
from src.DObject import DObject
from src.Pheromone import RecruitPheromone, AlarmPheromone, TrailPheromone


class Agent(DObject):
    def __init__(self, position=(0, 0)):
        super().__init__(position)
        self.angle = 0
        self.direction = np.array([0, 0])
        self.speed = 0
        self.distance_last_pheromone = 0
        self.energy = 0
        self.food_amount = 0
        self.steps_from_nest = 0
        self.ignore_pheromone_steps = 0
        self.mode = AgentMode.idle
        self.position = np.array(position)
        self.rnd = random.Random()
        self.init()

    def init(self):
        self.detect_range = 10 / 1000
        self.mode = AgentMode.idle
        self.distance_last_pheromone = 0
        self.energy = Constants.total_energy
        self.food_amount = 0
        self.speed = Constants.norm_speed
        self.angle = 0
        self.steps_from_nest = 0

    def get_move_distance(self):
        return self.speed * Constants.update_time

    def calc_destination(self, new_direction=None):
        if new_direction is None:
            new_direction = np.array(self.direction)
        destination = [0, 0]

        if self.mode != AgentMode.idle and self.mode != AgentMode.dead:
            distance_moved = self.speed * Constants.update_time
            destination = self.position + (new_direction * distance_moved)
        return destination

    def set_mode(self, mode):
        self.mode = mode

        if mode in [AgentMode.idle, AgentMode.dead]:
            self.speed = 0
            self.angle = 0
            self.direction = np.array([0, 0])
        elif mode == AgentMode.eating:
            self.speed = 0
        elif mode == AgentMode.exploring:
            self.speed = Constants.norm_speed
            self.angle = self.rnd.random() * 2 * math.pi
            self.update_direction()
        elif mode in [AgentMode.distressed, AgentMode.following_alarm]:
            self.speed = Constants.alarm_speed
        elif mode == AgentMode.returning_food:
            self.speed = Constants.norm_speed

    def is_returning(self):
        return self.mode in [AgentMode.returning_food, AgentMode.returning_tired]

    def update(self, pheromone_direction):
        new_pheromone = None
        return_pheromone = False
        distance_moved = 0
        pheromone_detected = (pheromone_direction[0] != 0 or pheromone_direction[1] != 0)

        if self.mode not in [AgentMode.idle, AgentMode.dead, AgentMode.eating]:
            distance_moved = self.get_move_distance()
            self.position += self.direction * distance_moved
            self.energy -= distance_moved
            if self.energy <= 0:
                self.energy = 0
                self.mode = AgentMode.dead
                self.speed = 0
            if self.ignore_pheromone_steps > 0:
                self.ignore_pheromone_steps -= 1

        if self.mode == AgentMode.exploring:
            if self.energy < Constants.trail_energy:
                self.turn_around()
                self.mode = AgentMode.returning_tired
            else:
                self.steps_from_nest += 1
                self.distance_last_pheromone += distance_moved
                if self.distance_last_pheromone > Constants.trail_create_distance and not self.is_ignoring_pheromones():
                    if pheromone_detected:
                        pheromone_angle = math.atan2(pheromone_direction[1], pheromone_direction[0])
                        self.angle += (self.angle - pheromone_angle)
                        self.update_direction()
                    else:
                        self.vary_direction(1 / 6)
                    self.distance_last_pheromone = 0
                    new_pheromone = TrailPheromone(self.position)
                    return_pheromone = True

        elif self.mode == AgentMode.following_pheromone:
            if pheromone_detected:
                self.direction = np.array(pheromone_direction)
                self.update_angle()
            else:
                self.mode = AgentMode.exploring
            self.distance_last_pheromone += distance_moved
            if self.distance_last_pheromone > Constants.trail_create_distance and not self.is_ignoring_pheromones():
                self.distance_last_pheromone = 0
                new_pheromone = TrailPheromone(self.position)
                return_pheromone = True

        elif self.mode in [AgentMode.returning_food, AgentMode.returning_tired]:
            if pheromone_detected:
                self.direction = np.array(pheromone_direction)
                self.update_angle()
            else:
                self.vary_direction(1 / 3)
            if self.mode == AgentMode.returning_food:
                self.distance_last_pheromone += distance_moved
                if self.distance_last_pheromone > Constants.trail_create_distance:
                    self.distance_last_pheromone = 0
                    new_pheromone = RecruitPheromone(self.position)
                    return_pheromone = True
            self.steps_from_nest -= 1

        elif self.mode == AgentMode.distressed:
            self.distance_last_pheromone = 0
            new_pheromone = AlarmPheromone(self.position)
            return_pheromone = True

        if return_pheromone:
            return new_pheromone
        return None

    def ignore_pheromones(self):
        if self.mode == AgentMode.following_pheromone:
            self.mode = AgentMode.exploring
        self.ignore_pheromone_steps = 5

    def is_ignoring_pheromones(self):
        return self.ignore_pheromone_steps > 0

    def update_direction(self):
        self.check_angle()
        self.direction = np.array([math.cos(self.angle), math.sin(self.angle)])

    def update_angle(self):
        self.angle = math.atan2(self.direction[1], self.direction[0])

    def vary_direction(self, radvar):
        self.angle += (self.rnd.random() - 0.5) * math.pi * (radvar * 2)
        self.update_direction()

    def turn_around(self):
        self.direction = -self.direction
        self.angle += math.pi
        self.check_angle()

    def check_angle(self):
        while self.angle < -2 * math.pi:
            self.angle += 2 * math.pi
        while self.angle > 2 * math.pi:
            self.angle -= 2 * math.pi
