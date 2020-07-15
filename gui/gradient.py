from time import time

import cv2 as cv
import numpy as np
from PySide2.QtWidgets import (
    QSpinBox,
    QComboBox,
    QCheckBox,
    QHBoxLayout,
    QVBoxLayout,
    QLabel)

from .tools import ToolWidget
from .utility import create_lut, norm_mat, equalize_img, elapsed_time
from .viewer import ImageViewer


class GradientWidget(ToolWidget):
    def __init__(self, image, parent=None):
        super(GradientWidget, self).__init__(parent)
        self.intensity_spin = QSpinBox()
        self.intensity_spin.setRange(0, 100)
        self.intensity_spin.setValue(95)
        self.intensity_spin.setSuffix(self.tr(' %'))
        self.intensity_spin.setToolTip(self.tr('Tonality compression amount'))
        self.blue_combo = QComboBox()
        self.blue_combo.addItems([self.tr('None'), self.tr('Flat'), self.tr('Abs'), self.tr('Norm')])
        self.blue_combo.setCurrentIndex(2)
        self.blue_combo.setToolTip(self.tr('Blue component inclusion mode'))
        self.invert_check = QCheckBox(self.tr('Invert'))
        self.invert_check.setToolTip(self.tr('Reverse lighting direction'))
        self.equalize_check = QCheckBox(self.tr('Equalize'))
        self.equalize_check.setToolTip(self.tr('Apply histogram equalization'))

        self.image = image
        self.viewer = ImageViewer(self.image, self.image)
        self.dx, self.dy = cv.spatialGradient(cv.cvtColor(self.image, cv.COLOR_BGR2GRAY))
        self.process()

        self.intensity_spin.valueChanged.connect(self.process)
        self.blue_combo.currentIndexChanged.connect(self.process)
        self.invert_check.stateChanged.connect(self.process)
        self.equalize_check.stateChanged.connect(self.process)

        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel(self.tr('Intensity:')))
        top_layout.addWidget(self.intensity_spin)
        top_layout.addWidget(QLabel(self.tr('Blue channel:')))
        top_layout.addWidget(self.blue_combo)
        top_layout.addWidget(self.invert_check)
        top_layout.addWidget(self.equalize_check)
        top_layout.addStretch()

        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.viewer)

        self.setLayout(main_layout)

    def process(self):
        start = time()
        intensity = int(self.intensity_spin.value() / 100 * 127)
        invert = self.invert_check.isChecked()
        equalize = self.equalize_check.isChecked()
        self.intensity_spin.setEnabled(not equalize)
        blue_mode = self.blue_combo.currentIndex()
        if invert:
            dx = (-self.dx).astype(np.float32)
            dy = (-self.dy).astype(np.float32)
        else:
            dx = (+self.dx).astype(np.float32)
            dy = (+self.dy).astype(np.float32)
        dx_abs = np.abs(dx)
        dy_abs = np.abs(dy)
        red = ((dx / np.max(dx_abs) * 127) + 127).astype(np.uint8)
        green = ((dy / np.max(dy_abs) * 127) + 127).astype(np.uint8)
        if blue_mode == 0:
            blue = np.zeros_like(red)
        elif blue_mode == 1:
            blue = np.full_like(red, 255)
        elif blue_mode == 2:
            blue = norm_mat(dx_abs + dy_abs)
        elif blue_mode == 3:
            blue = norm_mat(np.linalg.norm(cv.merge((red, green)), axis=2))
        else:
            blue = None
        gradient = cv.merge([blue, green, red])
        if equalize:
            gradient = equalize_img(gradient)
        elif intensity > 0:
            gradient = cv.LUT(gradient, create_lut(intensity, intensity))
        self.viewer.update_processed(gradient)
        self.info_message.emit(self.tr('Luminance Gradient = {}'.format(elapsed_time(start))))
