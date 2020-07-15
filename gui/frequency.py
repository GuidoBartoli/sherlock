from time import time

import cv2 as cv
import numpy as np
from PySide2.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QGridLayout,
    QSpinBox)

from .tools import ToolWidget
from .utility import norm_mat, elapsed_time, modify_font
from .viewer import ImageViewer


class FrequencyWidget(ToolWidget):
    def __init__(self, image, parent=None):
        super(FrequencyWidget, self).__init__(parent)

        self.split_spin = QSpinBox()
        self.split_spin.setRange(0, 100)
        self.split_spin.setValue(15)
        self.split_spin.setSuffix(self.tr(' %'))

        self.smooth_spin = QSpinBox()
        self.smooth_spin.setRange(0, 100)
        self.smooth_spin.setValue(25)
        self.smooth_spin.setSuffix(self.tr(' %'))
        self.smooth_spin.setSpecialValueText(self.tr('Off'))

        self.thr_spin = QSpinBox()
        self.thr_spin.setRange(0, 100)
        self.thr_spin.setValue(0)
        self.thr_spin.setSuffix(self.tr(' %'))
        self.thr_spin.setSpecialValueText(self.tr('Off'))

        self.zero_label = QLabel()
        modify_font(self.zero_label, italic=True)

        self.filter_spin = QSpinBox()
        self.filter_spin.setRange(0, 15)
        self.filter_spin.setValue(0)
        self.filter_spin.setSuffix(self.tr(' px'))
        self.filter_spin.setSpecialValueText(self.tr('Off'))

        self.split_spin.valueChanged.connect(self.process)
        self.smooth_spin.valueChanged.connect(self.process)
        self.thr_spin.valueChanged.connect(self.process)
        self.filter_spin.valueChanged.connect(self.process)

        self.image = image
        gray = cv.cvtColor(self.image, cv.COLOR_BGR2GRAY)
        rows, cols = gray.shape
        height = cv.getOptimalDFTSize(rows)
        width = cv.getOptimalDFTSize(cols)
        padded = cv.copyMakeBorder(gray, 0, height - rows, 0, width - cols, cv.BORDER_CONSTANT)
        self.dft = np.fft.fftshift(cv.dft(padded.astype(np.float32), flags=cv.DFT_COMPLEX_OUTPUT))
        self.magnitude, self.phase = cv.cartToPolar(self.dft[:, :, 0], self.dft[:, :, 1])
        self.magnitude = cv.normalize(cv.log(self.magnitude), None, 0, 255, cv.NORM_MINMAX)
        self.phase = cv.normalize(self.phase, None, 0, 255, cv.NORM_MINMAX)

        self.low_viewer = ImageViewer(self.image, self.image, self.tr('Low frequency'), export=True)
        self.high_viewer = ImageViewer(self.image, self.image, self.tr('High frequency'), export=True)
        self.mag_viewer = ImageViewer(self.image, None, self.tr('DFT Magnitude'), export=True)
        self.phase_viewer = ImageViewer(self.image, None, self.tr('DFT Phase'), export=True)
        self.process()

        self.low_viewer.viewChanged.connect(self.high_viewer.changeView)
        self.high_viewer.viewChanged.connect(self.low_viewer.changeView)
        self.mag_viewer.viewChanged.connect(self.phase_viewer.changeView)
        self.phase_viewer.viewChanged.connect(self.mag_viewer.changeView)

        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel(self.tr('Separation:')))
        top_layout.addWidget(self.split_spin)
        top_layout.addWidget(QLabel(self.tr('Smooth:')))
        top_layout.addWidget(self.smooth_spin)
        top_layout.addWidget(QLabel(self.tr('Threshold:')))
        top_layout.addWidget(self.thr_spin)
        top_layout.addWidget(QLabel(self.tr('Filter:')))
        top_layout.addWidget(self.filter_spin)
        top_layout.addWidget(self.zero_label)
        top_layout.addStretch()

        center_layout = QGridLayout()
        center_layout.addWidget(self.low_viewer, 0, 0)
        center_layout.addWidget(self.high_viewer, 0, 1)
        center_layout.addWidget(self.mag_viewer, 1, 0)
        center_layout.addWidget(self.phase_viewer, 1, 1)

        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addLayout(center_layout)
        self.setLayout(main_layout)

    def process(self):
        start = time()
        rows, cols, _ = self.dft.shape
        mask = np.zeros((rows, cols), np.float32)
        half = np.sqrt(rows**2 + cols**2) / 2
        radius = int(half * self.split_spin.value() / 100)
        mask = cv.circle(mask, (cols // 2, rows // 2), radius, 1, cv.FILLED)
        kernel = 2 * int(half * self.smooth_spin.value() / 100) + 1
        mask = cv.GaussianBlur(mask, (kernel, kernel), 0)
        mask /= np.max(mask)
        threshold = int(self.thr_spin.value() / 100 * 255)
        if threshold > 0:
            mask[self.magnitude < threshold] = 0
            zeros = (mask.size - np.count_nonzero(mask)) / mask.size * 100
        else:
            zeros = 0
        self.zero_label.setText(self.tr('(zeroed coefficients = {:.2f}%)').format(zeros))
        mask2 = np.repeat(mask[:, :, np.newaxis], 2, axis=2)

        rows0, cols0, _ = self.image.shape
        low = cv.idft(np.fft.ifftshift(self.dft * mask2), flags=cv.DFT_SCALE)
        low = norm_mat(cv.magnitude(low[:, :, 0], low[:, :, 1])[:rows0, :cols0], to_bgr=True)
        self.low_viewer.update_processed(low)
        high = cv.idft(np.fft.ifftshift(self.dft * (1 - mask2)), flags=cv.DFT_SCALE)
        high = norm_mat(cv.magnitude(high[:, :, 0], high[:, :, 1]), to_bgr=True)
        self.high_viewer.update_processed(np.copy(high[:self.image.shape[0], :self.image.shape[1]]))

        magnitude = (self.magnitude * mask).astype(np.uint8)
        phase = (self.phase * mask).astype(np.uint8)
        kernel = 2*self.filter_spin.value() + 1
        if kernel >= 3:
            magnitude = cv.GaussianBlur(magnitude, (kernel, kernel), 0)
            phase = cv.GaussianBlur(phase, (kernel, kernel), 0)
            # phase = cv.medianBlur(phase, kernel)
        self.mag_viewer.update_original(cv.cvtColor(magnitude, cv.COLOR_GRAY2BGR))
        self.phase_viewer.update_original(cv.cvtColor(phase, cv.COLOR_GRAY2BGR))
        self.info_message.emit(self.tr('Frequency Split = {}'.format(elapsed_time(start))))
