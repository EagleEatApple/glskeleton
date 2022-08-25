import sys

from baseapp import BaseApplication
from mainwindow import MainWindow
from maindockwindow import MainDockWindow
from utils import OpenGLTools


def main() -> None:
    app = BaseApplication(sys.argv)
    # window = MainWindow()
    window = MainDockWindow()
    window.show()

    """ for debugging """
    # print(OpenGLTools().gl_information)
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
