import sys

from baseapp import BaseApplication
from maindockwindow import MainDockWindow


def main() -> None:
    app = BaseApplication(sys.argv)
    window = MainDockWindow(app)
    window.resize(1200,800)
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
