import os
from time import time

import cv2 as cv
import numpy as np
from PySide2.QtCore import QCoreApplication
from PySide2.QtWidgets import (
    QPushButton,
    QGridLayout,
    QMessageBox)

from .jpeg import estimate_qf
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from .noiseprint.noiseprint import genNoiseprint
from .noiseprint.noiseprint_blind import genMappUint8
from .noiseprint.noiseprint_blind import noiseprint_blind_post
from .tools import ToolWidget
from .utility import modify_font, norm_mat, gray_to_bgr
from .viewer import ImageViewer


class SplicingWidget(ToolWidget):
    def __init__(self, image, parent=None):
        super(SplicingWidget, self).__init__(parent)

        self.image = image
        self.image0 = cv.cvtColor(self.image, cv.COLOR_BGR2GRAY).astype(np.float32) / 255
        self.noise = self.map = None

        self.noise_button = QPushButton(self.tr('(1/2) Estimate noise'))
        modify_font(self.noise_button, bold=True)
        gray = np.full_like(self.image, 127)
        self.noise_viewer = ImageViewer(self.image, gray, self.tr('Estimated noise print'), export=True)
        self.map_button = QPushButton(self.tr('(2/2) Compute heatmap'))
        modify_font(self.map_button, bold=True)
        self.map_button.setEnabled(False)
        self.map_viewer = ImageViewer(self.image, gray, self.tr('Splicing probability heatmap'))

        self.noise_button.clicked.connect(self.estimate_noise)
        self.noise_button.toggled.connect(self.estimate_noise)
        self.map_button.clicked.connect(self.compute_map)
        self.map_button.toggled.connect(self.compute_map)

        main_layout = QGridLayout()
        main_layout.addWidget(self.noise_viewer, 0, 0)
        main_layout.addWidget(self.noise_button, 1, 0)
        main_layout.addWidget(self.map_viewer, 0, 1)
        main_layout.addWidget(self.map_button, 1, 1)
        self.setLayout(main_layout)

    def estimate_noise(self):
        if self.noise is None:
            start = time()
            self.noise_button.setText(self.tr('Estimating noise, please wait...'))
            modify_font(self.noise_button, bold=False, italic=True)
            QCoreApplication.processEvents()

            qf = estimate_qf(self.image)
            self.noise = genNoiseprint(self.image0, qf, model_name='net')
            vmin, vmax, _, _ = cv.minMaxLoc(self.noise[34:-34, 34:-34])
            self.noise_viewer.update_processed(norm_mat(self.noise.clip(vmin, vmax), to_bgr=True))
            elapsed = time() - start

            self.noise_button.setText(self.tr('Noise estimated ({:.1f} s)'.format(elapsed)))
            modify_font(self.noise_button, bold=False, italic=False)
            self.map_button.setEnabled(True)
            self.noise_button.setCheckable(True)
        self.noise_button.setChecked(True)

    def compute_map(self):
        if self.map is None:
            start = time()
            self.map_button.setText(self.tr('Computing heatmap, please wait...'))
            modify_font(self.map_button, bold=False, italic=True)
            QCoreApplication.processEvents()

            mapp, valid, range0, range1, imgsize, other = noiseprint_blind_post(self.noise, self.image0)
            if mapp is None:
                QMessageBox.critical(self, self.tr('Error'), self.tr('Too many invalid blocks!'))
                return
            self.map = cv.applyColorMap(genMappUint8(mapp, valid, range0, range1, imgsize), cv.COLORMAP_JET)
            self.map_viewer.update_processed(self.map)
            elapsed = time() - start

            self.map_button.setText(self.tr('Heatmap computed ({:.1f} s)'.format(elapsed)))
            modify_font(self.map_button, bold=False, italic=False)
            self.map_button.setCheckable(True)
        self.map_button.setChecked(True)
        self.noise_viewer.viewChanged.connect(self.map_viewer.changeView)
        self.map_viewer.viewChanged.connect(self.noise_viewer.changeView)
