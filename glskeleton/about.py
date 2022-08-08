from PySide6.QtWidgets import QDialog, QDialogButtonBox, QPlainTextEdit, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtGui import QPixmap
from utils import OpenGLTools

# show OpenGL information
class AboutDialog(QDialog):
    def __init__(self, parent):
        super().__init__()
        self.setWindowTitle("About OpenGL")
        pixmap = QPixmap(parent.icons_path + "OpenGL-Logo.png")
        self.setWindowIcon(pixmap)
        qbtn = QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(qbtn)
        self.buttonBox.accepted.connect(self.accept)
        
        # use QPlainTextEdit to show current OpenGL information

        self.vlayout = QVBoxLayout()

        self.hlayout = QHBoxLayout()

        self.gl_image = QLabel()
        self.gl_image.setPixmap(pixmap)
        self.gl_image.resize(pixmap.width(), pixmap.height())

        self.gl_text_edit = QPlainTextEdit()
        self.gl_text_edit.setMinimumWidth(400)
        self.gl_text_edit.setReadOnly(True)
        self.gl_text_edit.setPlainText(OpenGLTools().gl_information)
        self.hlayout.addWidget(self.gl_image)
        self.hlayout.addWidget(self.gl_text_edit)

        self.vlayout.addLayout(self.hlayout)
        self.vlayout.addWidget(self.buttonBox)
        self.setLayout(self.vlayout)
        