from time import time

import cv2 as cv
import numpy as np
from PySide2.QtWidgets import (
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QCheckBox,
    QSpinBox,
    QLabel)

from .jpeg import compress_img
from .tools import ToolWidget
from .utility import elapsed_time, equalize_img, desaturate, create_lut
from .viewer import ImageViewer


class ElaWidget(ToolWidget):
    def __init__(self, image, parent=None):
        super(ElaWidget, self).__init__(parent)

        self.quality_spin = QSpinBox()
        self.quality_spin.setRange(0, 100)
        self.quality_spin.setSuffix(self.tr(' %'))
        self.quality_spin.setToolTip(self.tr('JPEG reference quality level'))
        self.scale_spin = QSpinBox()
        self.scale_spin.setRange(1, 100)
        self.scale_spin.setSuffix(' %')
        self.scale_spin.setToolTip(self.tr('Output multiplicative gain'))
        self.contrast_spin = QSpinBox()
        self.contrast_spin.setRange(0, 100)
        self.contrast_spin.setSuffix(' %')
        self.contrast_spin.setToolTip(self.tr('Output tonality compression'))
        self.equalize_check = QCheckBox(self.tr('Equalized'))
        self.equalize_check.setToolTip(self.tr('Apply histogram equalization'))
        self.gray_check = QCheckBox(self.tr('Grayscale'))
        self.gray_check.setToolTip(self.tr('Desaturated output'))
        default_button = QPushButton(self.tr('Default'))
        default_button.setToolTip(self.tr('Revert to default parameters'))

        params_layout = QHBoxLayout()
        params_layout.addWidget(QLabel(self.tr('Quality:')))
        params_layout.addWidget(self.quality_spin)
        params_layout.addWidget(QLabel(self.tr('Scale:')))
        params_layout.addWidget(self.scale_spin)
        params_layout.addWidget(QLabel(self.tr('Contrast:')))
        params_layout.addWidget(self.contrast_spin)
        params_layout.addWidget(self.equalize_check)
        params_layout.addWidget(self.gray_check)
        params_layout.addWidget(default_button)
        params_layout.addStretch()

        self.image = image
        self.original = image.astype(np.float32) / 255
        self.viewer = ImageViewer(self.image, self.image)
        self.default()

        self.quality_spin.valueChanged.connect(self.process)
        self.scale_spin.valueChanged.connect(self.process)
        self.contrast_spin.valueChanged.connect(self.process)
        self.equalize_check.stateChanged.connect(self.process)
        self.gray_check.stateChanged.connect(self.process)
        default_button.clicked.connect(self.default)

        main_layout = QVBoxLayout()
        main_layout.addLayout(params_layout)
        main_layout.addWidget(self.viewer)
        self.setLayout(main_layout)

    def process(self):
        start = time()
        quality = self.quality_spin.value()
        scale = self.scale_spin.value() / 20
        contrast = int(self.contrast_spin.value() / 100 * 128)
        equalize = self.equalize_check.isChecked()
        grayscale = self.gray_check.isChecked()
        self.scale_spin.setEnabled(not equalize)
        self.contrast_spin.setEnabled(not equalize)
        compressed = compress_img(self.image, quality).astype(np.float32) / 255
        difference = cv.absdiff(self.original, compressed)
        if equalize:
            ela = equalize_img((difference * 255).astype(np.uint8))
        else:
            ela = cv.convertScaleAbs(cv.sqrt(difference) * 255, None, scale)
            ela = cv.LUT(ela, create_lut(contrast, contrast))
        if grayscale:
            ela = desaturate(ela)
        self.viewer.update_processed(ela)
        self.info_message.emit(self.tr('Error Level Analysis = {}'.format(elapsed_time(start))))

    def default(self):
        self.blockSignals(True)
        self.equalize_check.setChecked(False)
        self.gray_check.setChecked(False)
        self.quality_spin.setValue(75)
        self.scale_spin.setValue(50)
        self.contrast_spin.setValue(20)
        self.process()
        self.blockSignals(False)
