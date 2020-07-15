from time import time

import cv2 as cv
import numpy as np
from PySide2.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QCheckBox,
    QSpinBox,
    QLabel)

from .tools import ToolWidget
from .utility import elapsed_time, create_lut, bgr_to_gray3
from .viewer import ImageViewer


class EchoWidget(ToolWidget):
    def __init__(self, image, parent=None):
        super(EchoWidget, self).__init__(parent)

        self.radius_spin = QSpinBox()
        self.radius_spin.setRange(1, 15)
        self.radius_spin.setSuffix(self.tr(' px'))
        self.radius_spin.setValue(2)
        self.radius_spin.setToolTip(self.tr('Laplacian filter radius'))

        self.contrast_spin = QSpinBox()
        self.contrast_spin.setRange(0, 100)
        self.contrast_spin.setSuffix(self.tr(' %'))
        self.contrast_spin.setValue(85)
        self.contrast_spin.setToolTip(self.tr('Output tonality compression'))

        self.gray_check = QCheckBox(self.tr('Grayscale'))
        self.gray_check.setToolTip(self.tr('Desaturated output mode'))

        self.image = image
        self.viewer = ImageViewer(self.image, self.image, None)
        self.process()

        self.radius_spin.valueChanged.connect(self.process)
        self.contrast_spin.valueChanged.connect(self.process)
        self.gray_check.stateChanged.connect(self.process)

        params_layout = QHBoxLayout()
        params_layout.addWidget(QLabel(self.tr('Radius:')))
        params_layout.addWidget(self.radius_spin)
        params_layout.addWidget(QLabel(self.tr('Contrast:')))
        params_layout.addWidget(self.contrast_spin)
        params_layout.addWidget(self.gray_check)
        params_layout.addStretch()

        main_layout = QVBoxLayout()
        main_layout.addLayout(params_layout)
        main_layout.addWidget(self.viewer)
        self.setLayout(main_layout)

    def process(self):
        start = time()
        kernel = 2*self.radius_spin.value() + 1
        contrast = int(self.contrast_spin.value() / 100 * 255)
        lut = create_lut(0, contrast)
        laplace = []
        for channel in cv.split(self.image):
            deriv = np.fabs(cv.Laplacian(channel, cv.CV_64F, None, kernel))
            deriv = cv.normalize(deriv, None, 0, 255, cv.NORM_MINMAX, cv.CV_8UC1)
            laplace.append(cv.LUT(deriv, lut))
        result = cv.merge(laplace)
        if self.gray_check.isChecked():
            result = bgr_to_gray3(result)
        self.viewer.update_processed(result)
        self.info_message.emit('Echo Edge Filter = {}'.format(elapsed_time(start)))
