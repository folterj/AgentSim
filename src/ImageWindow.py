from qtpy import uic
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QGraphicsScene, QGraphicsPixmapItem

from src.util import image_to_QPixmap


class ImageWindow(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        uic.loadUi('ui/ImageWindow.ui', self)
        self.pixmap = QGraphicsPixmapItem()
        scene = QGraphicsScene()
        self.graphicsView.setScene(scene)
        scene.addItem(self.pixmap)

    def resizeEvent(self, event):
        self.controller.update_view_size((self.graphicsView.width(), self.graphicsView.height()))

    def wheelEvent(self, event):
        self.controller.process_mouse_input(event.angleDelta().y(), (event.x(), event.y()))

    def draw(self, image):
        self.pixmap.setPixmap(image_to_QPixmap(image))
        self.pixmap.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
        self.graphicsView.repaint()
