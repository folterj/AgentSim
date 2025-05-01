from datetime import datetime
import numpy as np
import random
import time
from qtpy.QtCore import QTimer

from src.Agent import Agent
from src.AgentMode import AgentMode
from src.Constants import Constants
from src.DObject import DObject
from src.Food import Food
from src.Params import Params
from src.util import *


# TODO: optimise using bitmap mask for boundaries, and 2D numpy array for pheromones: type and activity level/duration


class Model:
    def __init__(self):
        self.observers = []
        self.hive = None
        self.agents = {}
        self.next_agent_id = 0
        self.map = []
        self.pheromones = []
        self.pheromone_maps = {}
        self.foods = []
        self.params = Params()
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update)
        self.update_count = 0
        self.update_time = 0
        self.running = False
        self.update_running = False
        self.rnd = random.Random(int(datetime.now().timestamp()))

    def init(self):
        self.reset()
        self.update_timers()

    def reset(self):
        self.agents.clear()
        self.pheromones.clear()
        self.foods.clear()
        self.map_image = self.create_map()
        self.map_image_float = self.map_image / np.float32(255)
        for label, values in Constants.pheromones.items():
            self.pheromone_maps[label] = np.zeros(np.flip(self.params.map_size), dtype=np.float32)

    def start(self):
        self.running = True
        self.update_timer.start()

    def stop(self):
        self.running = False
        self.update_timer.stop()

    def update_timers(self):
        self.update_timer.setInterval(int(Constants.update_time / self.params.time_speed * 1000))

    def create_map(self):
        image = load_image(Constants.map_filename)
        self.params.set_map_size(np.flip(image.shape[:2]))
        if image.ndim < 3:
            # gray source
            map_image = cv.cvtColor(image, cv.COLOR_GRAY2BGRA)
            self.map = (map_image > 0)
        else:
            # rgb source
            map_image = cv.cvtColor(image, cv.COLOR_BGR2BGRA)
            self.map = (cv.cvtColor(image, cv.COLOR_BGR2GRAY) > 0)
        self.hive = DObject((0.5 * self.params.world_size[0], 0.025 * self.params.world_size[1]))
        self.hive.detect_range = 100.0 / 1000  # (10 cm)
        self.foods.append(Food((0.5 * self.params.world_size[0], 0.975 * self.params.world_size[1]), 100))
        return map_image

    def spawn(self):
        if len(self.agents) < Constants.max_agents:
            position = self.hive.position
            agent = Agent(position, self.params)
            agent.set_mode(AgentMode.Scout)
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
                new_direction = (0, 0)
                dest_found = False
                if agent.mode in [AgentMode.Return, AgentMode.Recruit]:
                    # returning to hive
                    distance = self.hive.calc_distance(agent.position)
                    if distance < self.hive.detect_range:
                        if distance <= agent.get_move_distance():
                            self.agents.pop(agent)
                            continue
                        agent.angle = calc_angle(agent.position, self.hive.position)
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
                                agent.angle = calc_angle(agent.position, food.position)
                                agent.update_direction()
                            dest_found = True
                            break
                if not dest_found and not agent.is_ignoring_pheromones():
                    pheromones = self.find_pheromones_pos(agent)
                    if pheromones:
                        pheromone = agent.choose_pheromone(pheromones)
                        if pheromone:
                            distance = pheromone.calc_distance(agent.position)
                            if distance > 0:
                                direction = (pheromone.position - agent.position) / distance
                                new_direction = norm_direction(new_direction + direction)
                destination = agent.calc_destination()
                if not self.map[self.params.world_to_map(destination, reverse=True)]:
                    # check if destination is valid
                    agent.update_direction()
                    destination = agent.calc_destination()
                # vary angle to find a valid destination
                vary_angle = 0
                while not self.check_destination(destination):
                    if vary_angle < 0:
                        vary_angle -= 5
                    else:
                        vary_angle += 5
                    vary_angle = -vary_angle
                    agent.angle += vary_angle
                    agent.update_direction()
                    destination = agent.calc_destination()
                new_pheromone = agent.update(new_direction)
                if new_pheromone is not None:
                    self.add_pheromone(new_pheromone)

            for food in self.foods:
                if food.current_amount <= 0:
                    self.foods.remove(food)
            for pheromone in self.pheromones.copy():
                pheromone.update(Constants.update_time, self.pheromone_maps[pheromone.label])
                if not pheromone.active:
                    self.pheromones.remove(pheromone)

            self.update_count += 1
            self.update_time = time.time() - start_time
            self.update_running = False
            self.update_observers()

    def add_pheromone(self, pheromone):
        # TODO: strategy:
        #    1. add pheromones to map, recreating map every n time
        #  * 2. add pheromones to map w/o recreating, only subtract change (delta activity)
        self.pheromones.append(pheromone)
        pheromone.update_map(self.pheromone_maps[pheromone.label], pheromone.activity)

    def find_pheromones_pos(self, agent):
        pheromones = []
        for pheromone in self.pheromones:
            if pheromone.calc_distance(agent.position) < pheromone.max_detect_range + 1:
                pheromones.append(pheromone)
        return pheromones

    def find_pheromones_map(self, agent):
        pheromones = []
        position = self.params.world_to_map(agent.position)
        for label, map in self.pheromone_maps.items():
            if map[tuple(np.flip(position))]:
                pheromones.append(label)
        return pheromones

    def check_destination(self, destination):
        return self.map[self.params.world_to_map(destination, reverse=True)]

    def update_observers(self):
        for observer in self.observers:
            observer.update()

    def register_observer(self, observer):
        self.observers.append(observer)

    def unregister_observer(self, observer):
        self.observers.remove(observer)
