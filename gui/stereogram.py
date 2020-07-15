import cv2 as cv
import numpy as np
from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QRadioButton,
    QLabel,
    QHBoxLayout,
    QVBoxLayout)

from .tools import ToolWidget
from .utility import norm_mat, modify_font, gray_to_bgr, norm_img
from .viewer import ImageViewer


class StereoWidget(ToolWidget):
    def __init__(self, image, parent=None):
        super(StereoWidget, self).__init__(parent)

        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        small = cv.resize(gray, None, None, 1, 0.5)
        start = 10
        end = small.shape[1] // 3
        diff = np.fromiter([cv.mean(cv.absdiff(small[:, i:], small[:, :-i]))[0] for i in range(start, end)], np.float32)
        _, maximum, _, argmax = cv.minMaxLoc(np.ediff1d(diff))
        if maximum < 2:
            error_label = QLabel(self.tr('Unable to detect stereogram!'))
            modify_font(error_label, bold=True)
            error_label.setStyleSheet('color: #FF0000')
            error_label.setAlignment(Qt.AlignCenter)
            main_layout = QVBoxLayout()
            main_layout.addWidget(error_label)
            self.setLayout(main_layout)
            return

        offset = argmax[1] + start
        a = image[:, offset:]
        b = image[:, :-offset]
        self.pattern = norm_img(cv.absdiff(a, b))
        temp = cv.cvtColor(self.pattern, cv.COLOR_BGR2GRAY)
        thr, _ = cv.threshold(temp, 0, 255, cv.THRESH_TRIANGLE)
        self.silhouette = cv.medianBlur(gray_to_bgr(cv.threshold(temp, thr, 255, cv.THRESH_BINARY)[1]), 3)
        a = cv.cvtColor(a, cv.COLOR_BGR2GRAY)
        b = cv.cvtColor(b, cv.COLOR_BGR2GRAY)
        flow = cv.calcOpticalFlowFarneback(a, b, None, 0.5, 5, 15, 5, 5, 1.2, cv.OPTFLOW_FARNEBACK_GAUSSIAN)[:, :, 0]
        self.depth = gray_to_bgr(norm_mat(flow))
        flow = np.repeat(cv.normalize(flow, None, 0, 1, cv.NORM_MINMAX)[:, :, np.newaxis], 3, axis=2)
        self.shaded = cv.normalize(self.pattern.astype(np.float32)*flow, None, 0, 255, cv.NORM_MINMAX).astype(np.uint8)
        self.viewer = ImageViewer(self.pattern, None, export=True)

        self.pattern_radio = QRadioButton(self.tr('Pattern'))
        self.pattern_radio.setChecked(True)
        self.pattern_radio.setToolTip(self.tr('Difference between raw and aligned image'))
        self.silhouette_radio = QRadioButton(self.tr('Silhouette'))
        self.silhouette_radio.setToolTip(self.tr('Apply threshold to discovered pattern'))
        self.depth_radio = QRadioButton(self.tr('Depth'))
        self.depth_radio.setToolTip(self.tr('Estimate 3D depth using optical flow'))
        self.shaded_radio = QRadioButton(self.tr('Shaded'))
        self.shaded_radio.setToolTip(self.tr('Combine pattern and depth information'))

        self.silhouette_radio.clicked.connect(self.process)
        self.pattern_radio.clicked.connect(self.process)
        self.depth_radio.clicked.connect(self.process)
        self.shaded_radio.clicked.connect(self.process)

        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel(self.tr('Mode:')))
        top_layout.addWidget(self.pattern_radio)
        top_layout.addWidget(self.silhouette_radio)
        top_layout.addWidget(self.depth_radio)
        top_layout.addWidget(self.shaded_radio)
        top_layout.addStretch()
        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.viewer)
        self.setLayout(main_layout)

    def process(self):
        if self.pattern_radio.isChecked():
            output = self.pattern
        elif self.silhouette_radio.isChecked():
            output = self.silhouette
        elif self.depth_radio.isChecked():
            output = self.depth
        elif self.shaded_radio.isChecked():
            output = self.shaded
        else:
            return
        self.viewer.update_original(output)
