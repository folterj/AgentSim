import cv2 as cv
import numpy as np
import time
from qtpy.QtCore import QThread

from src.Constants import Constants
from src.ImageWindow import ImageWindow
from src.MainWindow import MainWindow


# remove QTimer in view/controller, and handle calling Qt function from here?

class View(QThread):
    def __init__(self, controller, model):
        super().__init__()
        self.controller = controller
        self.model = model
        self.params = model.params

        self.main_window = None
        self.control_window = None

        self.updating = False

        self.update_time = 0

        model.register_observer(self)

    def update(self):
        self.draw()

    def run(self):
        self.draw()

    def create(self):
        self.image_window = ImageWindow(self.controller)
        self.image_window.show()

        self.main_window = MainWindow(self.controller, self.params)
        self.main_window.show()

        self.reset()

    def reset(self):
        self.update()

    def zoom(self, zoom, offset):
        #center = offset / self.scale + self.view_offset
        #self.view_size *= zoom
        #self.view_offset = center - self.view_size / 2
        self.update()

    def zoom_in(self):
        #self.view_size = self.view_size / 2
        #self.view_offset = 0.5 - self.view_size / 2
        self.update()

    def zoom_out(self):
        #self.view_size = self.view_size * 2
        #self.view_offset = 0.5 - self.view_size / 2
        self.update()

    def draw(self):
        if not self.updating:
            self.updating = True

            self.stopwatch = time.time()

            # TODO: improve performance - maybe use opencv? no alpha channel?
            map_image = self.model.map_image_float.copy()
            weight = 1 / len(self.model.pheromone_maps)
            for pheromone_map in self.model.pheromone_maps.values():
                color = np.array([1, 0, 0, 1])
                map_image[self.model.map] -= np.clip(np.atleast_3d(pheromone_map)[self.model.map], 0, 1) * (weight * (1 - color))
            self.canvas = (map_image * 255).astype(np.uint8)
            #self.draw_pheromones()
            self.draw_hive()
            self.draw_foods()
            self.draw_agents()

            self.update_time = time.time() - self.stopwatch

            self.draw_text(f"model: {self.model.update_time * 1000:.0f} ms", (0, 25))
            self.draw_text(f"view: {self.update_time * 1000:.0f} ms", (0, 50))

            self.image_window.draw(self.canvas)

            self.updating = False

    def update_size(self, new_size):
        self.screen_size = new_size
        self.update()

    def draw_agents(self, color=(0, 0, 0)):
        rad = max(self.params.world_to_map(Constants.agent_size) // 2, 1)
        for agent_id, agent in self.model.agents.copy().items():
            position = self.params.world_to_map(agent.position)
            color1 = list(int(c * 255) for c in list(color) + [1])
            cv.circle(self.canvas, position, rad, color1, cv.FILLED, cv.LINE_AA)

    def draw_pheromones(self, color=(1, 0, 0)):
        rad = max(self.params.world_to_map(Constants.pheromone_size) // 2, 1)
        for pheromone in self.model.pheromones.copy():
            position = self.params.world_to_map(pheromone.position)
            color1 = list(int(c * 255) for c in color) + [int(pheromone.activity * 255)]
            cv.circle(self.canvas, position, rad, color1, cv.FILLED, cv.LINE_AA)

    def draw_foods(self, color=(0, 1, 0)):
        rad = max(self.params.world_to_map(Constants.food_size) // 2, 1)
        for food in self.model.foods.copy():
            position = self.params.world_to_map(food.position)
            color1 = list(int(c * 255) for c in color) + [int(food.get_food_left() * 255)]
            cv.circle(self.canvas, position, rad, color1, cv.FILLED, cv.LINE_AA)

    def draw_hive(self, color=(1, 1, 0)):
        rad = max(self.params.world_to_map(Constants.hive_size) // 2, 1)
        position = self.params.world_to_map(self.model.hive.position)
        color1 = list(int(c * 255) for c in list(color) + [1])
        cv.circle(self.canvas, position, rad, color1, cv.FILLED, cv.LINE_AA)

    def draw_text(self, text, position, color=(0.5, 0.5, 0.5)):
        font_scale = 1
        position = np.array(position).astype(int)
        fontface = cv.FONT_HERSHEY_SIMPLEX
        color1 = tuple(int(c * 255) for c in list(color) + [1])
        cv.putText(self.canvas, text, position, fontface, font_scale, color1, 1, cv.LINE_AA)
