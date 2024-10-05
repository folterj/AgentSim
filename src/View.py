import cv2 as cv
import numpy as np
import time

from src.Constants import Constants
from src.ImageWindow import ImageWindow
from src.MainWindow import MainWindow


class View:
    def __init__(self, controller, model, params):
        self.controller = controller
        self.model = model
        self.params = params

        self.main_window = None
        self.control_window = None

        self.screen_size = np.array([0, 0])
        self.view_size = params.world_size
        self.view_offset = np.array([0, 0])
        self.scale = 1

        self.updating = False

        self.stopwatch = time.time()
        self.update_time = 0

        model.register_observer(self)

    def create(self):
        self.image_window = ImageWindow(self.controller)
        self.image_window.show()

        self.main_window = MainWindow(self.controller, self.params)
        self.main_window.show()

        self.reset()

    def reset(self):
        self.view_size = np.array(self.model.params.world_size)
        self.view_offset = np.array([0, 0])
        self.update()

    def zoom(self, zoom, offset):
        center = offset / self.scale + self.view_offset
        self.view_size *= zoom
        self.view_offset = center - self.view_size / 2
        self.update()

    def zoom_in(self):
        self.view_size = self.view_size / 2
        self.view_offset = 0.5 - self.view_size / 2
        self.update()

    def zoom_out(self):
        self.view_size = self.view_size * 2
        self.view_offset = 0.5 - self.view_size / 2
        self.update()

    def draw(self):
        if not self.updating:
            self.updating = True

            self.stopwatch = time.time()

            self.canvas = np.full(list(np.flip(self.screen_size)) + [3], fill_value=255, dtype=np.uint8)
            self.draw_boundaries()
            self.draw_pheromones()
            self.draw_hive()
            self.draw_foods()
            self.draw_agents()

            self.update_time = (time.time() - self.stopwatch) * 1000

            self.draw_text(f"model: {self.model.update_time:.3f} ms", (0, 25))
            self.draw_text(f"view: {self.update_time:.3f} ms", (0, 50))

            self.image_window.draw(self.canvas)

            self.updating = False

    def update_size(self, new_size):
        self.screen_size = new_size
        self.update()

    def update(self):
        viewsize = np.linalg.norm(self.view_size)
        screensize = np.linalg.norm(self.screen_size)
        self.scale = screensize / viewsize
        #self.canvas = np.full(list(np.flip(self.screen_size)) + [3], fill_value=255, dtype=np.uint8)
        self.draw()

    def draw_agents(self, color=(0, 0, 0)):
        rad = max(int(Constants.agent_size / 2 * self.scale), 1)
        for agent in self.model.agents:
            position = ((np.array(agent.position) - self.view_offset) * self.scale).astype(int)
            cv.circle(self.canvas, position, rad, color, cv.FILLED, cv.LINE_AA)

    def draw_pheromones(self, color=(1, 0, 0)):
        rad = max(int(0.0002 * self.scale), 1)
        for pheromone in self.model.pheromones:
            position = ((np.array(pheromone.position) - self.view_offset) * self.scale).astype(int)
            color1 = list(int(c * 255) for c in color) + [int(pheromone.activity * 255)]
            cv.circle(self.canvas, position, rad, color1, cv.FILLED, cv.LINE_AA)

    def draw_foods(self, color=(0, 1, 0)):
        rad = max(int(0.002 * self.scale), 1)
        for food in self.model.foods:
            position = ((np.array(food.position) - self.view_offset) * self.scale).astype(int)
            color1 = list(int(c * 255) for c in color) + [int(food.get_food_left() * 255)]
            cv.circle(self.canvas, position, rad, color1, cv.FILLED, cv.LINE_AA)

    def draw_hive(self, color=(1, 1, 0)):
        rad = max(int(0.002 * self.scale), 1)
        position = ((np.array(self.model.hive.position) - self.view_offset) * self.scale).astype(int)
        cv.circle(self.canvas, position, rad, color, cv.FILLED, cv.LINE_AA)

    def draw_boundaries(self, color=(0, 0, 0)):
        for obstacle in self.model.obstacles:
            start = ((np.array(obstacle.start) - self.view_offset) * self.scale).astype(int)
            end = ((np.array(obstacle.end) - self.view_offset) * self.scale).astype(int)
            cv.line(self.canvas, start, end, color, 1, cv.LINE_AA)

    def draw_text(self, text, position, color=(0, 0, 0)):
        font_scale = 1
        position = np.array(position).astype(int)
        fontface = cv.FONT_HERSHEY_SIMPLEX
        color = tuple(int(c * 255) for c in color)
        cv.putText(self.canvas, text, position, fontface, font_scale, color, 1, cv.LINE_AA)
