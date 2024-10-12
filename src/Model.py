from datetime import datetime
import math
import numpy as np
import random
import time
from qtpy.QtCore import QTimer

from src.Agent import Agent
from src.AgentMode import AgentMode
from src.Boundary import Boundary
from src.Constants import Constants
from src.DObject import DObject
from src.Food import Food
from src.Params import Params
from src.Pheromone import Pheromone
from src.util import world_to_map


# TODO: optimise using bitmap mask for boundaries, and 2D numpy array for pheromones: type and activity level/duration


class Model:
    def __init__(self):
        self.observers = []
        self.hive = None
        self.agents = {}
        self.next_agent_id = 0
        self.pheromones = []
        self.pheromone_map = np.empty((Constants.map_size, Constants.map_size), dtype=Pheromone)
        self.foods = []
        self.boundaries = []
        self.params = Params()
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update)
        self.update_timers()
        self.update_count = 0
        self.update_time = 0
        self.running = False
        self.update_running = False
        self.rnd = random.Random(int(datetime.now().timestamp()))
        self.reset()

    def reset(self):
        self.agents.clear()
        self.pheromones.clear()
        self.foods.clear()
        self.boundaries.clear()
        self.create_maze_map()

    def start(self):
        self.running = True
        self.update_timer.start()

    def stop(self):
        self.running = False
        self.update_timer.stop()

    def update_params(self, params):
        self.params.copy_from(params)
        self.update_timers()

    def update_timers(self):
        self.update_timer.setInterval(int(Constants.update_time / self.params.time_speed * 1000))

    def create_simple_map(self):
        self.hive = DObject((0.5 * self.params.world_size[0], 0.25 * self.params.world_size[1]))
        self.hive.detect_range = 100.0 / 1000  # (10 cm -> m)
        self.foods.append(Food((0.5 * self.params.world_size[0], 0.75 * self.params.world_size[1]), 100))
        points = [
            (0.4, 0),
            (0.4, 1),
            (0.6, 1),
            (0.6, 0),
            (0.4, 0),
        ]
        self.add_boundary_path(points)

    def create_maze_map(self):
        self.hive = DObject((0.495 * self.params.world_size[0], 0.025 * self.params.world_size[1]))
        self.hive.detect_range = 100.0 / 1000  # (10 cm)
        self.foods.append(Food((0.495 * self.params.world_size[0], 0.975 * self.params.world_size[1]), 100))
        points = [
            (0.45 / 2 + 0.25, 0),
            (0.45 / 2 + 0.25, 0.15),
            (0.3 / 2 + 0.25, 0.22),
            (0.07 / 2 + 0.25, 0.26),
            (0.02 / 2 + 0.25, 0.3),
            (0.07 / 2 + 0.25, 0.34),
            (0.3 / 2 + 0.25, 0.37),
            (0.45 / 2 + 0.25, 0.44),
            (0.45 / 2 + 0.25, 0.56),
            (0.32 / 2 + 0.25, 0.7),
            (0.45 / 2 + 0.25, 0.85),
            (0.45 / 2 + 0.25, 1),
        ]
        self.add_boundary_path(points)
        points = [
            (0.53 / 2 + 0.25, 0),
            (0.53 / 2 + 0.25, 0.15),
            (0.65 / 2 + 0.25, 0.3),
            (0.53 / 2 + 0.25, 0.44),
            (0.53 / 2 + 0.25, 0.56),
            (0.66 / 2 + 0.25, 0.63),
            (0.9 / 2 + 0.25, 0.66),
            (0.96 / 2 + 0.25, 0.7),
            (0.9 / 2 + 0.25, 0.74),
            (0.67 / 2 + 0.25, 0.77),
            (0.53 / 2 + 0.25, 0.85),
            (0.53 / 2 + 0.25, 1),
        ]
        self.add_boundary_path(points)
        points = [
            (0.48 / 2 + 0.25, 0.19),
            (0.36 / 2 + 0.25, 0.26),
            (0.12 / 2 + 0.25, 0.3),
            (0.36 / 2 + 0.25, 0.33),
            (0.48 / 2 + 0.25, 0.39),
            (0.57 / 2 + 0.25, 0.3),
            (0.48 / 2 + 0.25, 0.19),
        ]
        self.add_boundary_path(points)
        points = [
            (0.5 / 2 + 0.25, 0.61),
            (0.63 / 2 + 0.25, 0.68),
            (0.86 / 2 + 0.25, 0.7),
            (0.63 / 2 + 0.25, 0.73),
            (0.5 / 2 + 0.25, 0.8),
            (0.42 / 2 + 0.25, 0.7),
            (0.5 / 2 + 0.25, 0.61),
        ]
        self.add_boundary_path(points)
        points = [
            (0.45 / 2 + 0.25, 0),
            (0.53 / 2 + 0.25, 0),
        ]
        self.add_boundary_path(points)
        points = [
            (0.45 / 2 + 0.25, 1),
            (0.53 / 2 + 0.25, 1),
        ]
        self.add_boundary_path(points)

    def add_boundary_path(self, points):
        last_point = None
        for point in np.array(points):
            if last_point is not None:
                point1 = last_point * self.params.world_size
                point2 = point * self.params.world_size
                self.boundaries.append(Boundary(point1, point2))
            last_point = point

    def spawn(self):
        if len(self.agents) < Constants.max_agents:
            position = self.hive.position
            agent = Agent(position)
            agent.set_mode(AgentMode.exploring)
            self.agents[self.next_agent_id] = agent
            self.next_agent_id += 1

    def update(self):
        if self.running and not self.update_running:
            self.update_running = True
            start_time = time.time()
            if self.update_count > Constants.spawn_time / Constants.update_time:
                self.spawn()
                self.update_count = 0
            for agent in self.agents.values():
                pheromone_direction = (0, 0)
                dest_found = False
                if agent.mode in [AgentMode.returning_food, AgentMode.returning_tired]:
                    # returning to hive
                    distance = self.hive.calc_distance(agent.position)
                    if distance < self.hive.detect_range:
                        if distance <= agent.get_move_distance():
                            self.agents.pop(agent)
                            continue
                        agent.angle = self.calc_angle(agent.position, self.hive.position)
                        agent.update_direction()
                        dest_found = True
                if agent.food_amount < 1:
                    # check if food source is nearby
                    for food in self.foods:
                        distance = food.calc_distance(agent.position)
                        if distance < food.detect_range:
                            if distance <= agent.get_move_distance():
                                agent.position = food.position
                                food.eat_amount(agent)
                            else:
                                agent.angle = self.calc_angle(agent.position, food.position)
                                agent.update_direction()
                            dest_found = True
                            break
                if not dest_found and not agent.is_ignoring_pheromones():
                    pheromone = self.find_pheromones(agent)
                    if pheromone is not None:
                        distance = pheromone.calc_distance(agent.position)
                        if distance > 0:
                            direction = (pheromone.position - agent.position) / distance
                            pheromone_direction = self.norm_direction(pheromone_direction + direction)
                destination = agent.calc_destination()
                for boundary in self.boundaries:
                    if boundary.intersects(agent.position):
                        if boundary.get_side(agent.position) != boundary.get_side(destination):
                            agent.ignore_pheromones()
                            angle1 = boundary.angle
                            angle2 = 2 * math.pi - angle1
                            dangle1 = self.smallest_angle_dif(agent.angle, angle1)
                            dangle2 = self.smallest_angle_dif(agent.angle, angle2)
                            if abs(dangle1) < abs(dangle2):
                                agent.angle = angle1
                            else:
                                agent.angle = angle2
                            agent.update_direction()
                            destination = agent.calc_destination()
                while not self.check_destination(agent.position, destination):
                    agent.ignore_pheromones()
                    agent.vary_direction(0.1)
                    destination = agent.calc_destination()
                new_pheromone = agent.update(pheromone_direction)
                if new_pheromone is not None:
                    self.add_pheromone(new_pheromone)

            for food in self.foods:
                if food.current_amount <= 0:
                    self.foods.remove(food)
            for pheromone in self.pheromones:
                pheromone.update(Constants.update_time)
                if not pheromone.active:
                    self.pheromones.remove(pheromone)

            self.update_count += 1
            self.update_time = time.time() - start_time
            self.update_running = False
            self.update_observers()

    def add_pheromone(self, pheromone):
        self.pheromones.append(pheromone)
        position0 = pheromone.position
        if pheromone.detect_range > 0:
            detect_range = int(round(pheromone.detect_range))
            for y in range(-detect_range, detect_range):
                for x in range(-detect_range, detect_range):
                    position = np.array(world_to_map(position0)) + [x, y]
                    if 0 <= position[0] < self.pheromone_map[0] and 0 <= position[1] < self.pheromone_map[1]:
                        self.pheromone_map[tuple(position)] = pheromone
        else:
            self.pheromone_map[world_to_map(position0)] = pheromone

    def find_pheromones(self, agent):
        pheromone = self.pheromone_map[world_to_map(agent.position)]
        return pheromone

    def check_destination(self, position, destination):
        for boundary in self.boundaries:
            # optimise
            if boundary.intersects(position):
                if boundary.get_side(position) != boundary.get_side(destination):
                    return False
        return True

    def calc_angle(self, origin, target):
        delta = target - origin
        return math.atan2(delta[1], delta[0])

    def smallest_angle_dif(self, angle1, angle2):
        difangle = abs(angle1 - angle2) % (2 * math.pi)
        if difangle > math.pi:
            difangle = 2 * math.pi - difangle
        return difangle

    def norm_angle(self, angle):
        if angle > math.pi:
            return angle - 2 * math.pi
        return angle

    def angle_to_detection(self, angle):
        return 1 - angle / math.pi

    def norm_direction(self, direction):
        length = np.linalg.norm(direction)
        if length != 1 and length != 0:
            direction /= length
        return direction

    def update_observers(self):
        for observer in self.observers:
            observer.update()

    def register_observer(self, observer):
        self.observers.append(observer)

    def unregister_observer(self, observer):
        self.observers.remove(observer)
