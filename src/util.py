from qtpy.QtGui import QPixmap, QImage


def image_to_QPixmap(image):
    height, width = image.shape[:2]
    nchannels = image.shape[2] if image.ndim > 2 else 1
    bytes_per_line = nchannels * width
    if nchannels == 1:
        channel_format = QImage.Format_Grayscale8
    else:
        channel_format = QImage.Format_RGB888
    return QPixmap(QImage(image, width, height, bytes_per_line, channel_format))
