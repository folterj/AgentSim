from qtpy import uic
from qtpy.QtWidgets import QMainWindow


class MainWindow(QMainWindow):
    def __init__(self, controller, params):
        super().__init__()
        self.controller = controller
        self.params = params
        uic.loadUi('ui/MainWindow.ui', self)
        self.pushButton_start.clicked.connect(self.controller_start)
        self.pushButton_stop.clicked.connect(self.controller.stop)
        self.pushButton_reset.clicked.connect(self.controller.reset)
        self.pushButton_zoom_in.clicked.connect(self.controller.view_zoom_in)
        self.pushButton_zoom_out.clicked.connect(self.controller.view_zoom_out)
        self.pushButton_view_reset.clicked.connect(self.controller.view_reset)

    def controller_start(self):
        self.controller.update_params()
        self.controller.start()
