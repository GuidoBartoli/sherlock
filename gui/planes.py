import cv2 as cv
import numpy as np
from PySide2.QtWidgets import (
    QHBoxLayout,
    QComboBox,
    QLabel,
    QVBoxLayout,
    QSpinBox)

from .tools import ToolWidget
from .utility import norm_mat
from .viewer import ImageViewer


class PlanesWidget(ToolWidget):
    def __init__(self, image, parent=None):
        super(PlanesWidget, self).__init__(parent)

        self.chan_combo = QComboBox()
        self.chan_combo.addItems(
            [self.tr('Luminance'), self.tr('Red'), self.tr('Green'), self.tr('Blue'), self.tr('RGB Norm')])
        self.plane_spin = QSpinBox()
        self.plane_spin.setPrefix(self.tr('Bit '))
        self.plane_spin.setRange(0, 7)
        self.filter_combo = QComboBox()
        self.filter_combo.addItems([self.tr('Disabled'), self.tr('Median'), self.tr('Gaussian')])

        self.image = image
        self.viewer = ImageViewer(self.image, self.image)
        self.planes = None
        self.preprocess()

        self.chan_combo.currentIndexChanged.connect(self.preprocess)
        self.plane_spin.valueChanged.connect(self.process)
        self.filter_combo.currentIndexChanged.connect(self.process)

        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel(self.tr('Channel:')))
        top_layout.addWidget(self.chan_combo)
        top_layout.addWidget(QLabel(self.tr('Plane:')))
        top_layout.addWidget(self.plane_spin)
        top_layout.addWidget(QLabel(self.tr('Filter:')))
        top_layout.addWidget(self.filter_combo)
        top_layout.addStretch()

        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.viewer)
        self.setLayout(main_layout)

    def preprocess(self):
        channel = self.chan_combo.currentIndex()
        if channel == 0:
            img = cv.cvtColor(self.image, cv.COLOR_BGR2GRAY)
        elif channel == 4:
            b, g, r = cv.split(self.image.astype(np.float64))
            img = cv.sqrt(cv.pow(b, 2) + cv.pow(g, 2) + cv.pow(r, 2)).astype(np.uint8)
        else:
            img = self.image[:, :, 3 - channel]

        self.planes = [norm_mat(cv.bitwise_and(np.full_like(img, 2 ** b), img), to_bgr=True) for b in range(8)]

        # rows, cols = img.shape
        # bits = 8
        # data = [np.binary_repr(img[i][j], width=bits) for i in range(rows) for j in range(cols)]
        # self.planes = [
        #     (np.array([int(i[b]) for i in data], dtype=np.uint8) * 2 ** (bits - b - 1)).reshape(
        #         (rows, cols)) for b in range(bits)]

        self.process()

    def process(self):
        plane = self.planes[self.plane_spin.value()]
        if self.filter_combo.currentIndex() == 1:
            plane = cv.medianBlur(plane, 3)
        elif self.filter_combo.currentIndex() == 2:
            plane = cv.GaussianBlur(plane, (3, 3), 0)
        self.viewer.update_processed(plane)
