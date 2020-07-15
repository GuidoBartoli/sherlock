from PySide2.QtCore import QUrl
from PySide2.QtGui import QIcon
from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QRadioButton,
    QHBoxLayout)

from .tools import ToolWidget


class ReverseWidget(ToolWidget):
    def __init__(self, parent=None):
        super(ReverseWidget, self).__init__(parent)

        self.tineye_radio = QRadioButton(self.tr('TinEye'))
        self.tineye_radio.setIcon(QIcon('gui/icons/tineye.png'))
        self.google_radio = QRadioButton(self.tr('Google'))
        self.google_radio.setIcon(QIcon('gui/icons/google.svg'))
        self.bing_radio = QRadioButton(self.tr('Bing'))
        self.bing_radio.setIcon(QIcon('gui/icons/bing.svg'))
        self.root_radio = QRadioButton(self.tr('RootAbout'))
        self.root_radio.setIcon(QIcon('gui/icons/rootabout.png'))
        self.karma_radio = QRadioButton(self.tr('KarmaDecay'))
        self.karma_radio.setIcon(QIcon('gui/icons/karmadecay.jpg'))
        self.tineye_radio.setChecked(True)
        self.last_radio = self.tineye_radio
        self.web_view = QWebEngineView()
        self.choose()

        self.tineye_radio.clicked.connect(self.choose)
        self.google_radio.clicked.connect(self.choose)
        self.bing_radio.clicked.connect(self.choose)
        self.root_radio.clicked.connect(self.choose)
        self.karma_radio.clicked.connect(self.choose)

        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel(self.tr('Search engine:')))
        top_layout.addWidget(self.tineye_radio)
        top_layout.addWidget(self.google_radio)
        top_layout.addWidget(self.bing_radio)
        top_layout.addWidget(self.root_radio)
        top_layout.addWidget(self.karma_radio)
        top_layout.addStretch()
        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.web_view)
        self.setLayout(main_layout)

    def choose(self):
        if self.tineye_radio.isChecked():
            self.web_view.load(QUrl('https://tineye.com/'))
            self.last_radio = self.tineye_radio
        elif self.google_radio.isChecked():
            self.web_view.load(QUrl('https://www.google.com/imghp'))
            self.last_radio = self.google_radio
        elif self.bing_radio.isChecked():
            self.web_view.load(QUrl('https://www.bing.com/?scope=images&nr=1&FORM=NOFORM'))
            self.last_radio = self.bing_radio
        elif self.root_radio.isChecked():
            self.web_view.load(QUrl('http://rootabout.com/'))
            self.last_radio = self.root_radio
        elif self.karma_radio.isChecked():
            self.web_view.load(QUrl('http://karmadecay.com/'))
            self.last_radio = self.karma_radio
        else:
            self.last_radio.setChecked(True)
