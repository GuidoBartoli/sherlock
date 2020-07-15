from time import time

import cv2 as cv
from PySide2.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QCheckBox,
    QLabel,
    QVBoxLayout,
    QSpinBox)

from .tools import ToolWidget
from .utility import create_lut, elapsed_time, equalize_img
from .viewer import ImageViewer


class NoiseWidget(ToolWidget):
    def __init__(self, image, parent=None):
        super(NoiseWidget, self).__init__(parent)

        self.mode_combo = QComboBox()
        self.mode_combo.addItems([
            self.tr('Median'), self.tr('Gaussian'), self.tr('BoxBlur'),
            self.tr('Bilateral'), self.tr('NonLocal')])

        self.radius_spin = QSpinBox()
        self.radius_spin.setRange(1, 10)
        self.radius_spin.setSuffix(self.tr(' px'))
        self.radius_spin.setValue(1)

        self.sigma_spin = QSpinBox()
        self.sigma_spin.setRange(1, 200)
        self.sigma_spin.setValue(3)

        self.levels_spin = QSpinBox()
        self.levels_spin.setRange(0, 255)
        self.levels_spin.setSpecialValueText(self.tr('Equalized'))
        self.levels_spin.setValue(32)

        self.gray_check = QCheckBox(self.tr('Grayscale'))
        self.denoised_check = QCheckBox(self.tr('Denoised'))

        self.image = image
        self.viewer = ImageViewer(self.image, self.image)
        self.process()

        params_layout = QHBoxLayout()
        params_layout.addWidget(QLabel(self.tr('Mode:')))
        params_layout.addWidget(self.mode_combo)
        params_layout.addWidget(QLabel(self.tr('Radius:')))
        params_layout.addWidget(self.radius_spin)
        params_layout.addWidget(QLabel(self.tr('Sigma:')))
        params_layout.addWidget(self.sigma_spin)
        params_layout.addWidget(QLabel(self.tr('Levels:')))
        params_layout.addWidget(self.levels_spin)
        params_layout.addWidget(self.gray_check)
        params_layout.addWidget(self.denoised_check)
        params_layout.addStretch()

        main_layout = QVBoxLayout()
        main_layout.addLayout(params_layout)
        main_layout.addWidget(self.viewer)
        self.setLayout(main_layout)

        self.mode_combo.currentTextChanged.connect(self.process)
        self.radius_spin.valueChanged.connect(self.process)
        self.sigma_spin.valueChanged.connect(self.process)
        self.levels_spin.valueChanged.connect(self.process)
        self.gray_check.stateChanged.connect(self.process)
        self.denoised_check.stateChanged.connect(self.process)

    def process(self):
        start = time()
        grayscale = self.gray_check.isChecked()
        if grayscale:
            original = cv.cvtColor(self.image, cv.COLOR_BGR2GRAY)
        else:
            original = self.image
        radius = self.radius_spin.value()
        kernel = radius*2 + 1
        sigma = self.sigma_spin.value()
        choice = self.mode_combo.currentText()
        if choice == self.tr('Median'):
            self.sigma_spin.setEnabled(False)
            denoised = cv.medianBlur(original, kernel)
        elif choice == self.tr('Gaussian'):
            self.sigma_spin.setEnabled(False)
            denoised = cv.GaussianBlur(original, (kernel, kernel), 0)
        elif choice == self.tr('BoxBlur'):
            self.sigma_spin.setEnabled(False)
            denoised = cv.blur(original, (kernel, kernel))
        elif choice == self.tr('Bilateral'):
            self.sigma_spin.setEnabled(True)
            denoised = cv.bilateralFilter(original, kernel, sigma, sigma)
        elif choice == self.tr('NonLocal'):
            if grayscale:
                denoised = cv.fastNlMeansDenoising(original, None, kernel)
            else:
                denoised = cv.fastNlMeansDenoisingColored(original, None, kernel, kernel)
        else:
            denoised = None

        if self.denoised_check.isChecked():
            self.levels_spin.setEnabled(False)
            result = denoised
        else:
            self.levels_spin.setEnabled(True)
            noise = cv.absdiff(original, denoised)
            levels = self.levels_spin.value()
            if levels == 0:
                if grayscale:
                    result = cv.equalizeHist(noise)
                else:
                    result = equalize_img(noise)
            else:
                result = cv.LUT(noise, create_lut(0, 255 - levels))
        if grayscale:
            result = cv.cvtColor(result, cv.COLOR_GRAY2BGR)
        self.viewer.update_processed(result)
        self.info_message.emit(self.tr('Noise estimation = {}'.format(elapsed_time(start))))
