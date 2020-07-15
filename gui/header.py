import os
from subprocess import run, PIPE

from PySide2.QtCore import QUrl, QTemporaryDir
from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtWidgets import QVBoxLayout

from .tools import ToolWidget
from .utility import exiftool_exe


class HeaderWidget(ToolWidget):
    def __init__(self, filename, parent=None):
        super(HeaderWidget, self).__init__(parent)
        self.temp_dir = QTemporaryDir()
        if self.temp_dir.isValid():
            temp_file = os.path.join(self.temp_dir.path(), 'structure.html')
            p = run([exiftool_exe(), '-htmldump0', filename], stdout=PIPE)
            with open(temp_file, 'w') as file:
                file.write(p.stdout.decode('utf-8'))
            web_view = QWebEngineView()
            web_view.load(QUrl('file://' + temp_file))
            layout = QVBoxLayout()
            layout.addWidget(web_view)
            self.setLayout(layout)
            self.setMinimumWidth(900)
