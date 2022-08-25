import os
import sys

from PySide6.QtWidgets import *
from PySide6.QtGui import QIcon, QAction, QKeySequence
from PySide6.QtCore import *

from baseapp import BaseApplication
from glwidget import GLWidget
from glcubewidget import GLCubeWidget
from glfractalwidget import GLFractalWidget
from about import AboutDialog


class MainDockWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.icons_path = os.path.abspath(
            os.path.dirname(__file__)) + '/images/'
        self.filters = "Any File (*)"
        self.gl_widget = GLWidget()
        self.cube_widget = GLCubeWidget()
        self.fractal_widget = GLFractalWidget()
        self.gl_demos = {"Cube": self.cube_widget, "Tessellation": self.gl_widget,
                         "Fractal": self.fractal_widget}
        self.create_ui()

    def create_ui(self) -> None:
        self.setWindowTitle("OpenGL Skeleton")
        self.setWindowIcon(QIcon(self.icons_path + 'app.png'))
        self.setGeometry(100, 100, 800, 600)

        # move main window to the center of the screen
        self.move(QApplication.primaryScreen(
        ).availableGeometry().center() - self.rect().center())
        self.create_action()
        self.create_menu_bar()
        self.create_toolbar()
        self.create_dockWidget()
        self.create_tabWidget()
        self.statusBar().showMessage('Ready', 10000)

    def create_tabWidget(self) -> None:
        self.tabs = QTabWidget(self)
        self.tabs.setTabsClosable(True)
        for key in self.gl_demos:
            self.tabs.addTab(self.gl_demos[key], key)
        self.setCentralWidget(self.tabs)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)

    def close_current_tab(self, index: int) -> None:
        # keep at least one tab
        if self.tabs.count() < 2:
            return
        self.tabs.removeTab(index)

    def create_dockWidget(self) -> None:
        self.dock_tree_Widget = QDockWidget("OpenGL Demos", self)
        self.dock_tree_Widget.setAllowedAreas(
            Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.dock_tree_Widget.setFeatures(
            QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        self.dock_tree_Widget.setMinimumWidth(200)
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderHidden(True)
        self.tree_widget.itemDoubleClicked.connect(self.doubleclick_tree_item)

        for demo in self.gl_demos:
            item = QTreeWidgetItem(self.tree_widget)
            item.setText(0, demo)
            self.tree_widget.addTopLevelItem(item)
        self.dock_tree_Widget.setWidget(self.tree_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock_tree_Widget)

    def doubleclick_tree_item(self, item: QTreeWidgetItem, column: int) -> None:
        title = item.text(0)
        exist = False
        for i in range(0, self.tabs.count()):
            text = self.tabs.tabText(i)
            if text == title:
                exist = True
                self.tabs.setCurrentIndex(i)
                break
        if not exist:
            index = self.tabs.addTab(self.gl_demos[title], title)
            self.tabs.setCurrentIndex(index)

    def create_menu_bar(self) -> None:
        self.file_menu = self.menuBar().addMenu("&File")
        self.file_menu.addAction(self.open_action)
        self.file_menu.addAction(self.save_action)
        self.file_menu.addAction(self.saveas_action)

        self.edit_menu = self.menuBar().addMenu("&Edit")
        self.edit_menu.addAction(self.undo_action)
        self.edit_menu.addAction(self.cut_action)

        self.help_menu = self.menuBar().addMenu("&Help")
        self.help_menu.addAction(self.about_action)

    def create_toolbar(self) -> None:
        self.top_toolbar = QToolBar()
        self.addToolBar(self.top_toolbar)
        self.top_toolbar.addAction(self.open_action)
        self.top_toolbar.addAction(self.save_action)
        self.top_toolbar.addAction(self.saveas_action)

        self.left_toolbar = QToolBar()
        self.addToolBar(Qt.LeftToolBarArea, self.left_toolbar)
        self.left_toolbar.addAction(self.undo_action)
        self.left_toolbar.addAction(self.cut_action)

    def create_action(self) -> None:
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
        self.about_action = QAction('About',
                                    self,
                                    statusTip="About",
                                    triggered=self.help_about)

    def open_file(self) -> None:
        self.file_name, self.filter_name = QFileDialog.getOpenFileName(self,
                                                                       caption="Open file",
                                                                       filter=self.filters)

    def save_file(self) -> None:
        pass

    def saveas_file(self) -> None:
        pass

    def edit_undo(self) -> None:
        pass

    def edit_cut(self) -> None:
        pass

    def help_about(self) -> None:
        dlg = AboutDialog(self.icons_path)
        dlg.exec()


def test() -> None:
    """Run MainWindow test"""
    app = BaseApplication(sys.argv)
    mainwindow = MainDockWindow()
    mainwindow.showMaximized()
    sys.exit(app.exec())


if __name__ == '__main__':
    test()
