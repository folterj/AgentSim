from src.Params import Params
from src.View import View


class Controller:
    def __init__(self, model):
        self.params = Params()
        self.model = model
        self.view = View(self, model, self.params)
        self.view.create()

    def start(self):
        self.model.start()

    def stop(self):
        self.model.stop()

    def update_params(self):
        self.model.update_params(self.params)

    def reset(self):
        self.model.reset()

    def view_zoom_in(self):
        self.view.zoom_in()

    def view_zoom_out(self):
        self.view.zoom_out()

    def view_reset(self):
        self.view.reset()

    def process_mouse_input(self, delta, position):
        delta //= 120
        if delta < 0:
            delta = -delta
            self.view.zoom(2 * delta, position)
        elif delta > 0:
            self.view.zoom(0.5 / delta, position)

    def update_view_size(self, new_size):
        self.view.update_size(new_size)
