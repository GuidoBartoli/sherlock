from PySide2.QtCore import QUrl
from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtWidgets import QVBoxLayout

from .tools import ToolWidget


class EditorWidget(ToolWidget):
    def __init__(self, parent=None):
        super(EditorWidget, self).__init__(parent)
        web_view = QWebEngineView()
        web_view.load(QUrl('https://hexed.it/'))
        layout = QVBoxLayout()
        layout.addWidget(web_view)
        self.setLayout(layout)
