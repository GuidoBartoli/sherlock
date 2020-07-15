from PySide2.QtWidgets import QVBoxLayout

from .tools import ToolWidget
from .viewer import ImageViewer


class OriginalWidget(ToolWidget):
    def __init__(self, image, parent=None):
        super(OriginalWidget, self).__init__(parent)
        viewer = ImageViewer(image, None, None)
        layout = QVBoxLayout()
        layout.addWidget(viewer)
        self.setLayout(layout)
