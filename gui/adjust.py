import cv2 as cv
import numpy as np
from PySide2.QtWidgets import (
    QVBoxLayout,
    QLabel,
    QGridLayout,
    QCheckBox,
    QPushButton,
    QComboBox)

from .tools import ToolWidget
from .utility import create_lut, ParamSlider
from .viewer import ImageViewer


class AdjustWidget(ToolWidget):
    def __init__(self, image, parent=None):
        super(AdjustWidget, self).__init__(parent)

        self.bright_slider = ParamSlider([-255, +255], 16, 0)
        self.sat_slider = ParamSlider([-255, +255], 16, 0)
        self.hue_slider = ParamSlider([0, 180], 10, 0, '°')
        self.gamma_slider = ParamSlider([1, 50], 10, 10)
        self.shadow_slider = ParamSlider([-100, +100], 10, 0, '%')
        self.high_slider = ParamSlider([-100, +100], 10, 0, '%')
        self.sweep_slider = ParamSlider([0, 255], 8, 127)
        self.width_slider = ParamSlider([0, 255], 8, 255)
        self.sharpen_slider = ParamSlider([0, 100], 10, 0, '%')
        self.thr_slider = ParamSlider([0, 255], 16, 255, special=self.tr('Auto'))
        self.equalize_combo = QComboBox()
        self.equalize_combo.addItems(
            [self.tr('No EQ'), self.tr('Hist EQ'), self.tr('CLAHE L1'),
             self.tr('CLAHE L2'), self.tr('CLAHE L3'), self.tr('CLAHE L4')])
        self.equalize_combo.setToolTip(self.tr('Histogram equalization mode'))
        self.invert_check = QCheckBox(self.tr('Invert values'))
        self.invert_check.setToolTip(self.tr('Apply bitwise complement'))
        self.reset_button = QPushButton(self.tr('Reset'))

        self.image = image
        self.viewer = ImageViewer(self.image, self.image)
        self.reset()

        self.bright_slider.valueChanged.connect(self.process)
        self.sat_slider.valueChanged.connect(self.process)
        self.hue_slider.valueChanged.connect(self.process)
        self.gamma_slider.valueChanged.connect(self.process)
        self.shadow_slider.valueChanged.connect(self.process)
        self.high_slider.valueChanged.connect(self.process)
        self.sweep_slider.valueChanged.connect(self.process)
        self.width_slider.valueChanged.connect(self.process)
        self.thr_slider.valueChanged.connect(self.process)
        self.sharpen_slider.valueChanged.connect(self.process)
        self.equalize_combo.currentIndexChanged.connect(self.process)
        self.invert_check.stateChanged.connect(self.process)
        self.reset_button.clicked.connect(self.reset)

        params_layout = QGridLayout()
        params_layout.addWidget(QLabel(self.tr('Brightness')), 0, 0)
        params_layout.addWidget(QLabel(self.tr('Saturation')), 1, 0)
        params_layout.addWidget(QLabel(self.tr('Hue')), 2, 0)
        params_layout.addWidget(QLabel(self.tr('Gamma')), 3, 0)
        params_layout.addWidget(self.bright_slider, 0, 1)
        params_layout.addWidget(self.sat_slider, 1, 1)
        params_layout.addWidget(self.hue_slider, 2, 1)
        params_layout.addWidget(self.gamma_slider, 3, 1)
        params_layout.addWidget(QLabel(self.tr('Shadows')), 0, 2)
        params_layout.addWidget(QLabel(self.tr('Highlights')), 1, 2)
        params_layout.addWidget(QLabel(self.tr('Sweep')), 2, 2)
        params_layout.addWidget(QLabel(self.tr('Width')), 3, 2)
        params_layout.addWidget(self.shadow_slider, 0, 3)
        params_layout.addWidget(self.high_slider, 1, 3)
        params_layout.addWidget(self.sweep_slider, 2, 3)
        params_layout.addWidget(self.width_slider, 3, 3)
        params_layout.addWidget(QLabel(self.tr('Sharpen')), 0, 4)
        params_layout.addWidget(self.sharpen_slider, 0, 5)
        params_layout.addWidget(QLabel(self.tr('Threshold')), 1, 4)
        params_layout.addWidget(self.thr_slider, 1, 5)
        params_layout.addWidget(self.equalize_combo, 2, 4)
        params_layout.addWidget(self.invert_check, 2, 5)
        params_layout.addWidget(self.reset_button, 3, 4, 1, 2)

        main_layout = QVBoxLayout()
        main_layout.addLayout(params_layout)
        main_layout.addWidget(self.viewer)
        self.setLayout(main_layout)

    def process(self):
        brightness = self.bright_slider.value()
        saturation = self.sat_slider.value()
        hue = self.hue_slider.value()
        gamma = self.gamma_slider.value() / 10
        shadows = self.shadow_slider.value()
        highlights = self.high_slider.value()
        equalize = self.equalize_combo.currentIndex()
        invert = self.invert_check.isChecked()
        sweep = self.sweep_slider.value()
        width = self.width_slider.value()
        threshold = self.thr_slider.value()
        sharpen = self.sharpen_slider.value() // 4

        result = np.copy(self.image)
        if sharpen > 0:
            kernel = 2 * sharpen + 1
            gaussian = cv.GaussianBlur(result, (kernel, kernel), 0)
            result = cv.addWeighted(result, 1.5, gaussian, -0.5, 0)
        if brightness != 0 or saturation != 0 or hue != 0:
            h, s, v = cv.split(cv.cvtColor(result, cv.COLOR_BGR2HSV))
            if hue != 0:
                h = h.astype(np.float64) + hue
                h[h < 0] += 180
                h[h > 180] -= 180
                h = h.astype(np.uint8)
            if saturation != 0:
                s = cv.add(s, saturation)
            if brightness != 0:
                v = cv.add(v, brightness)
            result = cv.cvtColor(cv.merge([h, s, v]), cv.COLOR_HSV2BGR)
        if gamma != 0:
            inverse = 1 / gamma
            lut = np.array([((i / 255) ** inverse) * 255 for i in np.arange(0, 256)]).astype(np.uint8)
            result = cv.LUT(result, lut)
        if shadows != 0:
            result = cv.LUT(result, create_lut(int(shadows / 100 * 255), 0))
        if highlights != 0:
            result = cv.LUT(result, create_lut(0, int(highlights / 100 * 255)))
        if width < 255:
            radius = width // 2
            low = max(sweep - radius, 0)
            high = 255 - min(sweep + radius, 255)
            result = cv.LUT(result, create_lut(low, high))
        if equalize > 0:
            h, s, v = cv.split(cv.cvtColor(result, cv.COLOR_BGR2HSV))
            if equalize == 1:
                v = cv.equalizeHist(v)
            elif equalize > 1:
                clip = 0
                if equalize == 2:
                    clip = 2
                elif equalize == 3:
                    clip = 5
                elif equalize == 4:
                    clip = 10
                elif equalize == 5:
                    clip = 20
                v = cv.createCLAHE(clip).apply(v)
            result = cv.cvtColor(cv.merge([h, s, v]), cv.COLOR_HSV2BGR)
        if threshold < 255:
            if threshold == 0:
                gray = cv.cvtColor(result, cv.COLOR_BGR2GRAY)
                threshold, _ = cv.threshold(gray, 0, 255, cv.THRESH_OTSU)
            _, result = cv.threshold(result, threshold, 255, cv.THRESH_BINARY)
        if invert:
            result = cv.bitwise_not(result)
        self.viewer.update_processed(result)

    def reset(self):
        self.blockSignals(True)
        self.bright_slider.reset_value()
        self.sat_slider.reset_value()
        self.hue_slider.reset_value()
        self.gamma_slider.reset_value()
        self.shadow_slider.reset_value()
        self.high_slider.reset_value()
        self.sweep_slider.reset_value()
        self.width_slider.reset_value()
        self.sharpen_slider.reset_value()
        self.thr_slider.reset_value()
        self.equalize_combo.setCurrentIndex(0)
        self.invert_check.setChecked(False)
        self.blockSignals(False)
        self.process()
