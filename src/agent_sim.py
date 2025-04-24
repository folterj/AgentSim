import sys
from qtpy import QtWidgets

from src.Controler import Controller
from src.Model import Model


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    controller = Controller()
    sys.exit(app.exec_())
