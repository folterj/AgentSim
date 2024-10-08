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
from src.Pheromone import AlarmPheromone, RecruitPheromone


class Model:
    def __init__(self):
        self.observers = []
        self.hive = None
        self.agents = []
        self.pheromones = []
        self.foods = []
        self.obstacles = []
        self.params = Params()
        self.spawn_timer = QTimer()
        self.spawn_timer.timeout.connect(self.spawn)
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update)
        self.update_timers()
        self.update_time = 0
        self.running = False
        self.update_running = False
        self.rnd = random.Random(int(datetime.now().timestamp()))
        self.reset()
        self.update_timers()

    def stop_timers(self):
        self.spawn_timer.stop()
        self.update_timer.stop()

    def reset(self):
        self.agents.clear()
        self.pheromones.clear()
        self.foods.clear()
        self.obstacles.clear()
        self.create_maze_map()
        self.slow_interval = 0

    def start(self):
        self.running = True
        self.spawn_timer.start()
        self.update_timer.start()

    def stop(self):
        self.running = False
        self.stop_timers()

    def update_params(self, params):
        self.params.copy_from(params)
        self.update_timers()

    def update_timers(self):
        self.spawn_timer.setInterval(int(Constants.spawn_time / self.params.time_speed * 1000))
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
                self.obstacles.append(Boundary(point1, point2))
            last_point = point

    def spawn(self):
        if len(self.agents) < Constants.max_agents:
            position = self.hive.position
            pheromone_direction = (0, 0)
            total_weight = 0
            agent = Agent(position)
            match_pheromone_types = self.find_pheromones(agent)
            for pheromone in self.pheromones:
                if type(pheromone) in match_pheromone_types:
                    distance = pheromone.calc_distance(position)
                    if distance < pheromone.max_detect_range:
                        detection = pheromone.calc_detection(position)
                        if distance != 0 and detection > 0:
                            direction = (pheromone.position - agent.position) / distance
                            weight = detection
                            pheromone_direction += direction * weight
                            total_weight += weight
            if total_weight > 0:
                pheromone_direction /= total_weight
                agent.direction = self.norm_direction(pheromone_direction)
                agent.update_angle()
            else:
                agent.set_mode(AgentMode.exploring)
            self.agents.append(agent)

    def update(self):
        if self.running and not self.update_running:
            self.update_running = True
            start_time = time.time()
            for agent in self.agents:
                position = agent.position
                pheromone_direction = (0, 0)
                total_weight = 0
                dest_found = False
                if agent.is_returning():
                    distance = self.hive.calc_distance(agent.position)
                    if distance < self.hive.detect_range:
                        if distance <= agent.get_move_distance():
                            self.agents.remove(agent)
                            continue
                        agent.angle = self.calc_angle(agent.position, self.hive.position)
                        agent.update_direction()
                        dest_found = True
                if agent.food_amount < 1:
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
                    match_pheromone_types = self.find_pheromones(agent)
                    for pheromone in self.pheromones[:]:
                        if not match_pheromone_types or type(pheromone) in match_pheromone_types:
                            distance = pheromone.calc_distance(position)
                            if distance < pheromone.max_detect_range:
                                detection = pheromone.calc_detection(position)
                                angle = self.calc_angle(agent.position, pheromone.position)
                                dangle = self.smallest_angle_dif(agent.angle, angle)
                                if distance != 0 and detection > 0 and abs(dangle) < math.pi / 4:
                                    direction = (pheromone.position - agent.position) / distance
                                    weight = detection
                                    pheromone_direction += direction * weight
                                    total_weight += weight
                    if total_weight > 0:
                        pheromone_direction /= total_weight
                        pheromone_direction = self.norm_direction(pheromone_direction)
                destination = agent.calc_destination()
                for obstacle in self.obstacles:
                    if obstacle.intersects(agent.position):
                        if obstacle.get_side(agent.position) != obstacle.get_side(destination):
                            agent.ignore_pheromones()
                            angle1 = obstacle.angle
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
                    agent.vary_direction(1)
                    destination = agent.calc_destination()
                new_pheromone = agent.update(pheromone_direction)
                if new_pheromone:
                    self.pheromones.append(new_pheromone)
            if self.slow_interval >= Constants.slow_update_interval:
                self.slow_update()
                self.slow_interval = 0
            self.slow_interval += 1
            self.update_time = time.time() - start_time
            self.update_running = False
            self.update_observers()

    def slow_update(self):
        if self.running:
            for food in self.foods[:]:
                if food.current_amount <= 0:
                    self.foods.remove(food)
            for pheromone in self.pheromones[:]:
                pheromone.update(self.params.time_speed)
                if not pheromone.active:
                    self.pheromones.remove(pheromone)

    def find_pheromones(self, ant):
        match_pheromone_types = []
        for pheromone in self.pheromones:
            distance = pheromone.calc_distance(ant.position)
            if distance < pheromone.max_detect_range:
                if isinstance(pheromone, AlarmPheromone) and AlarmPheromone not in match_pheromone_types:
                    match_pheromone_types.clear()
                    match_pheromone_types.append(AlarmPheromone)
                    ant.set_mode(AgentMode.following_alarm)
                elif isinstance(pheromone, RecruitPheromone) and not match_pheromone_types and not ant.is_returning():
                    match_pheromone_types.append(RecruitPheromone)
                    ant.set_mode(AgentMode.following_pheromone)
        return match_pheromone_types

    def check_destination(self, position, destination):
        for obstacle in self.obstacles:
            if obstacle.intersects(position):
                if obstacle.get_side(position) != obstacle.get_side(destination):
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
