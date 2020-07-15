import cv2 as cv
import numpy as np
from PySide2.QtWidgets import (
    QVBoxLayout,
    QGridLayout,
    QRadioButton,
    QComboBox,
    QHBoxLayout)

from .tools import ToolWidget
from .utility import modify_font
from .viewer import ImageViewer


class SpaceWidget(ToolWidget):
    def __init__(self, image, parent=None):
        super(SpaceWidget, self).__init__(parent)
        rows, cols, chans = image.shape
        scaled = image.astype(np.float32) / 255

        self.rgb = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        self.ycrcb = cv.cvtColor(image, cv.COLOR_BGR2YCrCb)
        self.xyz = cv.cvtColor(image, cv.COLOR_BGR2XYZ)
        self.lab = cv.cvtColor(image, cv.COLOR_BGR2Lab)
        self.luv = cv.cvtColor(image, cv.COLOR_BGR2Luv)

        self.gray = np.zeros((rows, cols, 4))
        self.gray[:, :, 0] = (np.amax(scaled, axis=2) + np.amin(scaled, axis=2)) / 2
        self.gray[:, :, 1] = 0.21*scaled[:, :, 2] + 0.72*scaled[:, :, 1] + 0.07*scaled[:, :, 0]
        self.gray[:, :, 2] = np.mean(scaled, axis=2)
        self.gray[:, :, 3] = cv.cvtColor(scaled, cv.COLOR_BGR2GRAY)
        self.gray = (self.gray * 255).astype(np.uint8)

        self.hsv = cv.cvtColor(scaled, cv.COLOR_BGR2HSV) * 255
        self.hsv[:, :, 0] /= 360
        self.hsv = self.hsv.astype(np.uint8)
        self.hls = cv.cvtColor(scaled, cv.COLOR_BGR2HLS) * 255
        self.hls[:, :, 0] /= 360
        self.hls = self.hls.astype(np.uint8)

        self.cmyk = np.zeros((rows, cols, 4))
        k = np.repeat(np.amin(1 - scaled, axis=2)[:, :, np.newaxis], repeats=3, axis=2)
        k[k == 1] = 1 - np.finfo(np.float32).eps
        self.cmyk[:, :, :-1] = (1 - scaled - k) / (1 - k) * 255
        self.cmyk[:, :, -1] = k[:, :, 0] * 255
        self.cmyk[:, :, [0, 1, 2, 3]] = self.cmyk[:, :, [2, 1, 0, 3]]
        self.cmyk = self.cmyk.astype(np.uint8)

        self.rgb_radio = QRadioButton(self.tr('RGB'))
        self.rgb_radio.setChecked(True)
        self.rgb_combo = QComboBox()
        self.rgb_combo.addItem(self.tr('Red'))
        self.rgb_combo.addItem(self.tr('Green'))
        self.rgb_combo.addItem(self.tr('Blue'))
        self.last_radio = self.rgb_radio

        self.cmyk_radio = QRadioButton(self.tr('CMYK'))
        self.cmyk_combo = QComboBox()
        self.cmyk_combo.addItem(self.tr('Cyan'))
        self.cmyk_combo.addItem(self.tr('Magenta'))
        self.cmyk_combo.addItem(self.tr('Yellow'))
        self.cmyk_combo.addItem(self.tr('Black'))

        self.gray_radio = QRadioButton(self.tr('Grayscale'))
        self.gray_combo = QComboBox()
        self.gray_combo.addItem(self.tr('Lightness'))
        self.gray_combo.addItem(self.tr('Luminance'))
        self.gray_combo.addItem(self.tr('Average'))
        self.gray_combo.addItem(self.tr('Perceptual'))

        self.hsv_radio = QRadioButton(self.tr('HSV'))
        self.hsv_combo = QComboBox()
        self.hsv_combo.addItem(self.tr('Hue'))
        self.hsv_combo.addItem(self.tr('Saturation'))
        self.hsv_combo.addItem(self.tr('Value'))

        self.hls_radio = QRadioButton(self.tr('HLS'))
        self.hls_combo = QComboBox()
        self.hls_combo.addItem(self.tr('Hue'))
        self.hls_combo.addItem(self.tr('Luminance'))
        self.hls_combo.addItem(self.tr('Saturation'))

        self.ycrcb_radio = QRadioButton(self.tr('YCrCb'))
        self.ycrcb_combo = QComboBox()
        self.ycrcb_combo.addItem(self.tr('Luminance'))
        self.ycrcb_combo.addItem(self.tr('Chroma Red'))
        self.ycrcb_combo.addItem(self.tr('Chroma Blue'))

        self.xyz_radio = QRadioButton(self.tr('CIE XYZ'))
        self.xyz_combo = QComboBox()
        self.xyz_combo.addItem(self.tr('X'))
        self.xyz_combo.addItem(self.tr('Y'))
        self.xyz_combo.addItem(self.tr('Z'))

        self.lab_radio = QRadioButton(self.tr('CIE Lab'))
        self.lab_combo = QComboBox()
        self.lab_combo.addItem(self.tr('Luminosity'))
        self.lab_combo.addItem(self.tr('Green-Red'))
        self.lab_combo.addItem(self.tr('Blue-Yellow'))

        self.luv_radio = QRadioButton(self.tr('CIE Luv'))
        self.luv_combo = QComboBox()
        self.luv_combo.addItem(self.tr('Luminosity'))
        self.luv_combo.addItem(self.tr('Chroma U'))
        self.luv_combo.addItem(self.tr('Chroma V'))

        self.rgb_radio.clicked.connect(self.process)
        self.rgb_combo.currentIndexChanged.connect(self.process)
        self.cmyk_radio.clicked.connect(self.process)
        self.cmyk_combo.currentIndexChanged.connect(self.process)
        self.gray_radio.clicked.connect(self.process)
        self.gray_combo.currentIndexChanged.connect(self.process)
        self.hsv_radio.clicked.connect(self.process)
        self.hsv_combo.currentIndexChanged.connect(self.process)
        self.hls_radio.clicked.connect(self.process)
        self.hls_combo.currentIndexChanged.connect(self.process)
        self.ycrcb_radio.clicked.connect(self.process)
        self.ycrcb_combo.currentIndexChanged.connect(self.process)
        self.xyz_radio.clicked.connect(self.process)
        self.xyz_combo.currentIndexChanged.connect(self.process)
        self.lab_radio.clicked.connect(self.process)
        self.lab_combo.currentIndexChanged.connect(self.process)
        self.luv_radio.clicked.connect(self.process)
        self.luv_combo.currentIndexChanged.connect(self.process)

        self.viewer = ImageViewer(image, image)
        self.process()

        grid_layout = QGridLayout()
        grid_layout.addWidget(self.rgb_radio, 0, 0)
        grid_layout.addWidget(self.rgb_combo, 0, 1)
        grid_layout.addWidget(self.cmyk_radio, 0, 2)
        grid_layout.addWidget(self.cmyk_combo, 0, 3)
        grid_layout.addWidget(self.gray_radio, 0, 4)
        grid_layout.addWidget(self.gray_combo, 0, 5)
        grid_layout.addWidget(self.hsv_radio, 1, 0)
        grid_layout.addWidget(self.hsv_combo, 1, 1)
        grid_layout.addWidget(self.hls_radio, 1, 2)
        grid_layout.addWidget(self.hls_combo, 1, 3)
        grid_layout.addWidget(self.ycrcb_radio, 1, 4)
        grid_layout.addWidget(self.ycrcb_combo, 1, 5)
        grid_layout.addWidget(self.xyz_radio, 2, 0)
        grid_layout.addWidget(self.xyz_combo, 2, 1)
        grid_layout.addWidget(self.lab_radio, 2, 2)
        grid_layout.addWidget(self.lab_combo, 2, 3)
        grid_layout.addWidget(self.luv_radio, 2, 4)
        grid_layout.addWidget(self.luv_combo, 2, 5)
        top_layout = QHBoxLayout()
        top_layout.addLayout(grid_layout)
        top_layout.addStretch()

        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.viewer)
        self.setLayout(main_layout)

    def process(self):
        if self.rgb_radio.isChecked():
            channel = self.rgb[:, :, self.rgb_combo.currentIndex()]
            self.last_radio = self.rgb_radio
        elif self.cmyk_radio.isChecked():
            channel = self.cmyk[:, :, self.cmyk_combo.currentIndex()]
            self.last_radio = self.cmyk_radio
        elif self.gray_radio.isChecked():
            channel = self.gray[:, :, self.gray_combo.currentIndex()]
            self.last_radio = self.gray_radio
        elif self.hsv_radio.isChecked():
            channel = self.hsv[:, :, self.hsv_combo.currentIndex()]
            self.last_radio = self.hsv_radio
        elif self.hls_radio.isChecked():
            channel = self.hls[:, :, self.hls_combo.currentIndex()]
            self.last_radio = self.hls_radio
        elif self.ycrcb_radio.isChecked():
            channel = self.ycrcb[:, :, self.ycrcb_combo.currentIndex()]
            self.last_radio = self.ycrcb_radio
        elif self.luv_radio.isChecked():
            channel = self.luv[:, :, self.luv_combo.currentIndex()]
            self.last_radio = self.luv_radio
        elif self.xyz_radio.isChecked():
            channel = self.xyz[:, :, self.xyz_combo.currentIndex()]
            self.last_radio = self.xyz_radio
        elif self.lab_radio.isChecked():
            channel = self.lab[:, :, self.lab_combo.currentIndex()]
            self.last_radio = self.lab_radio
        else:
            self.last_radio.setChecked(True)
            return
        modify_font(self.rgb_radio, bold=False)
        modify_font(self.cmyk_radio, bold=False)
        modify_font(self.gray_radio, bold=False)
        modify_font(self.hsv_radio, bold=False)
        modify_font(self.hls_radio, bold=False)
        modify_font(self.ycrcb_radio, bold=False)
        modify_font(self.luv_radio, bold=False)
        modify_font(self.xyz_radio, bold=False)
        modify_font(self.lab_radio, bold=False)
        modify_font(self.last_radio, bold=True)
        self.viewer.update_processed(cv.cvtColor(channel, cv.COLOR_GRAY2BGR))
