import cv2 as cv
import numpy as np
from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QPushButton,
    QComboBox,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QProgressDialog)

from .tools import ToolWidget
from .utility import compute_hist, gray_to_bgr
from .viewer import ImageViewer


class ContrastWidget(ToolWidget):
    def __init__(self, image, parent=None):
        super(ContrastWidget, self).__init__(parent)

        self.algo_combo = QComboBox()
        self.algo_combo.addItems(
            [self.tr('Histogram Error'), self.tr('Channel Similarity'), self.tr('Joint probability')])
        self.algo_combo.setToolTip(self.tr('Joint Probability merges Histogram Error and Channel Similarity'))
        self.algo_combo.setCurrentIndex(2)
        self.block_combo = QComboBox()
        self.block_combo.addItems(['32', '64', '128', '256'])
        self.block_combo.setCurrentIndex(1)
        self.block_combo.setToolTip(self.tr('Size of analyzed blocks'))
        self.process_button = QPushButton(self.tr('Process'))
        self.process_button.setToolTip(self.tr('Perform contrast enhancement analysis'))

        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel(self.tr('Algorithm:')))
        top_layout.addWidget(self.algo_combo)
        top_layout.addWidget(QLabel(self.tr('Block size:')))
        top_layout.addWidget(self.block_combo)
        top_layout.addWidget(self.process_button)
        top_layout.addStretch()

        self.image = image
        self.viewer = ImageViewer(self.image, self.image)
        self.error = self.chsim = self.joint = None
        self.canceled = False

        self.process_button.clicked.connect(self.process)
        self.algo_combo.currentIndexChanged.connect(self.choose)
        self.block_combo.currentIndexChanged.connect(self.reset)

        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.viewer)
        self.setLayout(main_layout)

    def reset(self):
        self.viewer.update_processed(self.image)
        self.process_button.setEnabled(True)
        self.error = self.chsim = self.joint = None

    def cancel(self):
        self.canceled = True

    def choose(self):
        if any([i is None for i in [self.error, self.chsim, self.joint]]):
            return
        algo = self.algo_combo.currentIndex()
        if algo == 0:
            output = self.error
        elif algo == 1:
            output = self.chsim
        elif algo == 2:
            output = self.joint
        else:
            return
        self.viewer.update_processed(output)

    def process(self):
        rows0, cols0, _ = self.image.shape
        block = int(self.block_combo.currentText())
        color = cv.copyMakeBorder(self.image, 0, rows0 % block, 0, cols0 % block, cv.BORDER_CONSTANT)
        gray = cv.cvtColor(color, cv.COLOR_BGR2GRAY)
        rows, cols = gray.shape

        kx, ky = cv.getDerivKernels(1, 1, 1)
        bd, gd, rd = [cv.sepFilter2D(c, cv.CV_32F, kx, ky) for c in cv.split(color)]
        tri = (np.abs(gd - rd) + np.abs(gd - bd) + np.abs(rd - bd)) / 3
        avg = (np.abs(bd) + np.abs(gd) + np.abs(rd)) / 3

        window = np.arange(256).astype(np.float32)
        cutoff = 8
        window[:cutoff] = (1 - np.cos(np.pi * window[:cutoff] / cutoff)) / 2
        window[-cutoff:] = (1 + np.cos(np.pi * (window[-cutoff:] + cutoff - 255) / cutoff)) / 2
        window[cutoff:-cutoff] = 1
        weight = ((np.arange(256) - 128) / 128) ** 2

        self.chsim = np.zeros(((rows // block) + 1, (cols // block) + 1), np.float32)
        self.error = np.copy(self.chsim)
        self.joint = np.copy(self.chsim)
        progress = QProgressDialog(
            self.tr('Detecting enhancements...'), self.tr('Cancel'), 0, self.chsim.size, self)
        progress.canceled.connect(self.cancel)
        progress.setWindowModality(Qt.WindowModal)

        max_err = 0.185
        max_sim = 0.75
        p = 0
        for i in range(0, rows, block):
            for j in range(0, cols, block):
                hist = compute_hist(gray[i:i + block, j:j + block]) * window
                hist = cv.normalize(hist, None, 0, 1, cv.NORM_MINMAX)
                dft = np.fft.fftshift(cv.dft(hist, flags=cv.DFT_COMPLEX_OUTPUT))
                mag = cv.magnitude(dft[:, :, 0], dft[:, :, 1])
                mag = cv.normalize(mag, None, 0, 1, cv.NORM_MINMAX).flatten()

                diff = 0
                for k in range(2, 254):
                    yl = 2 * hist[k - 1] - hist[k - 2]
                    yr = 2 * hist[k + 1] - hist[k + 2]
                    d = abs(hist[k] - (yl + yr) / 2)
                    if d > diff:
                        diff = d
                ed = np.sum(mag)
                if ed == 0:
                    error = 0
                else:
                    en = np.sum(mag * weight)
                    error = en / ed
                    if error > max_err:
                        error = 1
                    else:
                        error /= max_err
                    error *= np.sqrt(diff)
                self.error[i // block, j // block] = error

                avg_m = np.mean(avg[i:i + block, j:j + block])
                if avg_m == 0:
                    chsim = 0
                else:
                    tri_m = np.mean(tri[i:i + block, j:j + block])
                    chsim = tri_m / avg_m
                    if chsim > max_sim:
                        chsim = 1
                    else:
                        chsim /= max_sim
                self.chsim[i // block, j // block] = chsim

                self.joint[i // block, j // block] = error * chsim

                if self.canceled:
                    self.canceled = False
                    return
                progress.setValue(p)
                p += 1

        progress.setValue(self.chsim.size)
        self.chsim = cv.medianBlur(cv.convertScaleAbs(self.chsim, None, 255), 3)
        self.chsim = gray_to_bgr(cv.resize(self.chsim, None, None, block, block, cv.INTER_NEAREST)[:rows0, :cols0])
        self.error = cv.medianBlur(cv.convertScaleAbs(self.error, None, 255), 3)
        self.error = gray_to_bgr(cv.resize(self.error, None, None, block, block, cv.INTER_NEAREST)[:rows0, :cols0])
        self.joint = cv.medianBlur(cv.convertScaleAbs(self.joint, None, 255), 3)
        self.joint = gray_to_bgr(cv.resize(self.joint, None, None, block, block, cv.INTER_NEAREST)[:rows0, :cols0])
        self.process_button.setEnabled(False)
        self.choose()
