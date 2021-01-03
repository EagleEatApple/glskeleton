import os
from PySide6.QtWidgets import *
from PySide6.QtGui import QIcon, QAction, QKeySequence
from PySide6.QtCore import *
import glwidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.icons_path = os.path.abspath(os.path.dirname(__file__)) + '/icons/'
        self.filters = "Any File (*)"
        self.frame = QFrame()
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setLineWidth(1)
        self.setCentralWidget(self.frame)
        self.vlayout = QVBoxLayout()
        self.glwidget = glwidget.GLWidget()
        self.vlayout.addWidget(self.glwidget)
        self.frame.setLayout(self.vlayout)

        self.status_bar = None
        self.menu_bar = None
        self.top_toolbar = None
        self.left_toolbar = None
        self.create_ui()

    def create_ui(self):
        self.setWindowTitle("OpenGL Skeleton")
        self.setWindowIcon(QIcon(self.icons_path + 'app.png'))
        self.setGeometry(100, 100, 400, 400)
        self.create_action()
        self.create_status_bar()
        self.create_menu_bar()
        self.create_toolbar()

    def create_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage('Ready', 10000)

    def create_menu_bar(self):
        self.menu_bar = QMenuBar()
        self.setMenuBar(self.menu_bar)
        self.file_menu = self.menu_bar.addMenu("&File")
        self.file_menu.addAction(self.open_action)
        self.file_menu.addAction(self.save_action)
        self.file_menu.addAction(self.saveas_action)

        self.edit_menu = self.menu_bar.addMenu("&Edit")
        self.edit_menu.addAction(self.undo_action)
        self.edit_menu.addAction(self.cut_action)

        self.help_menu = self.menu_bar.addMenu("&Help")

    def create_toolbar(self):
        self.top_toolbar = QToolBar()
        self.addToolBar(self.top_toolbar)
        self.top_toolbar.addAction(self.open_action)
        self.top_toolbar.addAction(self.save_action)
        self.top_toolbar.addAction(self.saveas_action)

        self.left_toolbar = QToolBar()
        self.addToolBar(Qt.LeftToolBarArea, self.left_toolbar)
        self.left_toolbar.addAction(self.undo_action)
        self.left_toolbar.addAction(self.cut_action)

    def create_action(self):
        self.open_action = QAction(QIcon(self.icons_path + 'open.png'), 'O&pen',
                                   self, shortcut=QKeySequence.Open,
                                   statusTip="Open an existing file",
                                   triggered=self.open_file)
        self.save_action = QAction(QIcon(self.icons_path + 'save.png'), 'Save',
                                   self, shortcut=QKeySequence.Save,
                                   statusTip="Save to a file",
                                   triggered=self.save_file)
        self.saveas_action = QAction(QIcon(self.icons_path + 'saveas.png'), 'Save As',
                                     self, shortcut=QKeySequence.SaveAs,
                                     statusTip="Save to a file",
                                     triggered=self.saveas_file)
        self.undo_action = QAction(QIcon(self.icons_path + 'undo.png'), 'Undo',
                                   self, shortcut=QKeySequence.Undo,
                                   statusTip="Undo",
                                   triggered=self.edit_undo)
        self.cut_action = QAction(QIcon(self.icons_path + 'cut.png'), 'Cut',
                                  self, shortcut=QKeySequence.Cut,
                                  statusTip="Cut",
                                  triggered=self.edit_cut)

    def open_file(self):
        self.file_name, self.filter_name = QFileDialog.getOpenFileName(self,
                                                                       caption="Open file",
                                                                       filter=self.filters)

    def save_file(self):
        pass

    def saveas_file(self):
        pass

    def edit_undo(self):
        pass

    def edit_cut(self):
        pass
