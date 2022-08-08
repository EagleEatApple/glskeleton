# Ensure PySide6 had been installed
try:
    from PySide6.QtWidgets import QApplication
except ImportError:
    print("PySide6 must be installed to run this application!")
    print("Please run:\npip install PySide6")
from PySide6.QtGui import QSurfaceFormat


class BaseApplication(QApplication):
    def __init__(self, argv, bufferSize=24, samples=4, major=4, minor=0):
        super().__init__(argv)
        # initialize OpenGL profile, support OpenGL 4.0 by default
        self.format = QSurfaceFormat()
        self.format.setDepthBufferSize(bufferSize)
        self.format.setSamples(samples)
        self.format.setVersion(major, minor)
        self.format.setProfile(QSurfaceFormat.CoreProfile)
        QSurfaceFormat.setDefaultFormat(self.format)
