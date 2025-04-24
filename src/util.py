import cv2 as cv
import math
import numpy as np
from qtpy.QtGui import QPixmap, QImage

from src.Constants import Constants


def load_image(filename):
    image = cv.imread(filename)
    return image


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


def image_to_QPixmap(image):
    height, width = image.shape[:2]
    nchannels = image.shape[2] if image.ndim > 2 else 1
    bytes_per_line = nchannels * width
    if nchannels == 1:
        channel_format = QImage.Format_Grayscale8
    elif nchannels == 4:
        channel_format = QImage.Format_RGBA8888
    else:
        channel_format = QImage.Format_RGB888
    return QPixmap(QImage(image, width, height, bytes_per_line, channel_format))
