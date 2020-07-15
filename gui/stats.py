import cv2 as cv
import numpy as np
from PySide2.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QCheckBox,
    QLabel,
    QRadioButton)

from .tools import ToolWidget
from .viewer import ImageViewer


class StatsWidget(ToolWidget):
    def __init__(self, image, parent=None):
        super(StatsWidget, self).__init__(parent)

        self.min_radio = QRadioButton(self.tr('Minimum'))
        self.min_radio.setToolTip(self.tr('RGB channel with smallest value'))
        self.min_radio.setChecked(True)
        self.last_radio = self.min_radio
        self.avg_radio = QRadioButton(self.tr('Average'))
        self.avg_radio.setToolTip(self.tr('RGB channel with average value'))
        self.max_radio = QRadioButton(self.tr('Maximum'))
        self.max_radio.setToolTip(self.tr('RGB channel with largest value'))
        self.incl_check = QCheckBox(self.tr('Inclusive'))
        self.incl_check.setToolTip(self.tr('Use not strict inequalities'))

        self.image = image
        b, g, r = cv.split(self.image)
        blue = np.array([255, 0, 0])
        green = np.array([0, 255, 0])
        red = np.array([0, 0, 255])
        self.minimum = [[], []]
        self.minimum[0] = np.zeros_like(self.image)
        self.minimum[0][np.logical_and(b < g, b < r)] = blue
        self.minimum[0][np.logical_and(g < r, g < b)] = green
        self.minimum[0][np.logical_and(r < b, r < g)] = red
        self.minimum[1] = np.zeros_like(self.image)
        self.minimum[1][np.logical_and(b <= g, b <= r)] = blue
        self.minimum[1][np.logical_and(g <= r, g <= b)] = green
        self.minimum[1][np.logical_and(r <= b, r <= g)] = red
        self.maximum = [[], []]
        self.maximum[0] = np.zeros_like(self.image)
        self.maximum[0][np.logical_and(b > g, b > r)] = blue
        self.maximum[0][np.logical_and(g > r, g > b)] = green
        self.maximum[0][np.logical_and(r > b, r > g)] = red
        self.maximum[1] = np.zeros_like(self.image)
        self.maximum[1][np.logical_and(b >= g, b >= r)] = blue
        self.maximum[1][np.logical_and(g >= r, g >= b)] = green
        self.maximum[1][np.logical_and(r >= b, r >= g)] = red
        self.average = [[], []]
        self.average[0] = np.zeros_like(self.image)
        self.average[0][np.logical_or(np.logical_and(r < b, b < g), np.logical_and(g < b, b < r))] = blue
        self.average[0][np.logical_or(np.logical_and(r < g, g < b), np.logical_and(b < g, g < r))] = green
        self.average[0][np.logical_or(np.logical_and(b < r, r < g), np.logical_and(g < r, r < b))] = red
        self.average[1] = np.zeros_like(self.image)
        self.average[1][np.logical_or(np.logical_and(r <= b, b <= g), np.logical_and(g <= b, b <= r))] = blue
        self.average[1][np.logical_or(np.logical_and(r <= g, g <= b), np.logical_and(b <= g, g <= r))] = green
        self.average[1][np.logical_or(np.logical_and(b <= r, r <= g), np.logical_and(g <= r, r <= b))] = red
        self.viewer = ImageViewer(self.image, self.image)
        self.process()

        self.min_radio.clicked.connect(self.process)
        self.avg_radio.clicked.connect(self.process)
        self.max_radio.clicked.connect(self.process)
        self.incl_check.stateChanged.connect(self.process)

        params_layout = QHBoxLayout()
        params_layout.addWidget(QLabel(self.tr('Mode:')))
        params_layout.addWidget(self.min_radio)
        params_layout.addWidget(self.avg_radio)
        params_layout.addWidget(self.max_radio)
        params_layout.addWidget(self.incl_check)
        params_layout.addStretch()

        main_layout = QVBoxLayout()
        main_layout.addLayout(params_layout)
        main_layout.addWidget(self.viewer)
        self.setLayout(main_layout)

    def process(self):
        inclusive = self.incl_check.isChecked()
        if self.min_radio.isChecked():
            result = self.minimum[1 if inclusive else 0]
            self.last_radio = self.min_radio
        elif self.max_radio.isChecked():
            result = self.maximum[1 if inclusive else 0]
            self.last_radio = self.max_radio
        elif self.avg_radio.isChecked():
            result = self.average[1 if inclusive else 0]
            self.last_radio = self.avg_radio
        else:
            self.last_radio.setChecked(True)
            return
        self.viewer.update_processed(result)
