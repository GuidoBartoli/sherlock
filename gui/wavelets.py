from copy import deepcopy

import cv2 as cv
import numpy as np
import pywt
from PySide2.QtWidgets import (
    QSpinBox,
    QComboBox,
    QHBoxLayout,
    QVBoxLayout,
    QLabel)

from .tools import ToolWidget
from .viewer import ImageViewer


class WaveletWidget(ToolWidget):
    def __init__(self, image, parent=None):
        super(WaveletWidget, self).__init__(parent)

        self.family_combo = QComboBox()
        self.family_combo.addItems(
            [self.tr('Daubechies'), self.tr('Symlets'), self.tr('Coiflets'), self.tr('Biorthogonal')])
        self.wavelet_combo = QComboBox()
        self.wavelet_combo.setMinimumWidth(70)
        self.threshold_spin = QSpinBox()
        self.threshold_spin.setRange(0, 100)
        self.threshold_spin.setSuffix('%')
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(
            [self.tr('Soft'), self.tr('Hard'), self.tr('Garrote'), self.tr('Greater'), self.tr('Less')])
        self.level_spin = QSpinBox()

        self.image = image
        self.coeffs = None
        self.viewer = ImageViewer(self.image, self.image)
        self.update_wavelet()

        self.family_combo.activated.connect(self.update_wavelet)
        self.wavelet_combo.activated.connect(self.update_level)
        self.threshold_spin.valueChanged.connect(self.compute_idwt)
        self.mode_combo.activated.connect(self.compute_idwt)
        self.level_spin.valueChanged.connect(self.compute_idwt)

        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel(self.tr('Family:')))
        top_layout.addWidget(self.family_combo)
        top_layout.addWidget(QLabel(self.tr('Wavelet:')))
        top_layout.addWidget(self.wavelet_combo)
        top_layout.addWidget(QLabel(self.tr('Threshold:')))
        top_layout.addWidget(self.threshold_spin)
        top_layout.addWidget(QLabel(self.tr('Mode:')))
        top_layout.addWidget(self.mode_combo)
        top_layout.addWidget(QLabel(self.tr('Level:')))
        top_layout.addWidget(self.level_spin)
        top_layout.addStretch()

        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.viewer)
        self.setLayout(main_layout)

    def update_wavelet(self):
        self.wavelet_combo.clear()
        family = self.family_combo.currentIndex()
        if family == 0:
            self.wavelet_combo.addItems(['db{}'.format(i) for i in range(1, 21)])
        elif family == 1:
            self.wavelet_combo.addItems(['sym{}'.format(i) for i in range(2, 21)])
        elif family == 2:
            self.wavelet_combo.addItems(['coif{}'.format(i) for i in range(1, 6)])
        else:
            types = ['1.1', '1.3', '1.5', '2.2', '2.4', '2.6', '2.8',
                     '3.1', '3.3', '3.5', '3.7', '3.9', '4.4', '5.5', '6.8']
            self.wavelet_combo.addItems(['bior{}'.format(t) for t in types])
        self.update_level()

    def update_level(self):
        wavelet = self.wavelet_combo.currentText()
        max_level = pywt.dwtn_max_level(self.image.shape[:-1], wavelet)
        self.level_spin.blockSignals(True)
        self.level_spin.setRange(1, max_level)
        self.level_spin.setValue(max_level // 2)
        self.level_spin.blockSignals(False)
        self.compute_dwt()

    def compute_dwt(self):
        wavelet = self.wavelet_combo.currentText()
        self.coeffs = pywt.wavedec2(self.image[:, :, 0], wavelet)
        self.compute_idwt()

    def compute_idwt(self):
        thr = self.threshold_spin.value()
        if thr > 0:
            level = self.level_spin.value()
            coeffs = deepcopy(self.coeffs)
            threshold = self.threshold_spin.value() / 100
            mode = self.mode_combo.currentText().lower()
            for i in range(1, level + 1):
                octave = [None]*3
                for j in range(3):
                    plane = coeffs[-i][j]
                    t = threshold * np.max(np.abs(plane))
                    octave[j] = pywt.threshold(plane, t, mode)
                coeffs[-i] = tuple(octave)
        else:
            coeffs = self.coeffs
        wavelet = self.wavelet_combo.currentText()
        image = cv.cvtColor(pywt.waverec2(coeffs, wavelet).astype(np.uint8), cv.COLOR_GRAY2BGR)
        self.viewer.update_processed(image)
