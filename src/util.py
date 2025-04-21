import math
import numpy as np
from qtpy.QtGui import QPixmap, QImage

from src.Constants import Constants


def calc_angle(origin, target):
    delta = target - origin
    return math.degrees(math.atan2(delta[1], delta[0]))


def smallest_angle_dif(angle1, angle2):
    difangle = abs(angle1 - angle2) % 360
    if difangle > 180:
        difangle = 360 - difangle
    return difangle


def norm_angle(angle):
    if angle > 180:
        return angle - 360
    return angle


def norm_direction(direction):
    length = np.linalg.norm(direction)
    if length != 1 and length != 0:
        direction /= length
    return direction


def world_to_map(position, map_size=Constants.map_size):
    return tuple(np.round(position * map_size).astype(int).tolist())


def map_to_world(map_position, map_size=Constants.map_size):
    return np.asarray(map_position) / map_size


def image_to_QPixmap(image):
    height, width = image.shape[:2]
    nchannels = image.shape[2] if image.ndim > 2 else 1
    bytes_per_line = nchannels * width
    if nchannels == 1:
        channel_format = QImage.Format_Grayscale8
    else:
        channel_format = QImage.Format_RGB888
    return QPixmap(QImage(image, width, height, bytes_per_line, channel_format))
