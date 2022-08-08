import sys

from PySide6.QtGui import QScreen
from PySide6.QtWidgets import QApplication

from baseapp import BaseApplication
from mainwindow import MainWindow
from utils import OpenGLTools


def main():
    app = BaseApplication(sys.argv, major=2, minor=0)
    window = MainWindow()
    window.show()

    screenCenter = QScreen.availableGeometry(
        QApplication.primaryScreen()).center()
    position = window.frameGeometry()
    position.moveCenter(screenCenter)
    window.move(position.topLeft())

    """ for debugging """
    # print(OpenGLTools().gl_information)
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
