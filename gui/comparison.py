import math
import os
from subprocess import run, PIPE

import cv2 as cv
import numpy as np
import sewar
from PySide2.QtCore import QTemporaryDir, Qt
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import (
    QAbstractItemView,
    QTableWidgetItem,
    QTableWidget,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QCheckBox,
    QLabel,
    QRadioButton,
    QProgressDialog)

from .tools import ToolWidget
from .utility import (
    norm_mat,
    equalize_img,
    modify_font,
    load_image,
    desaturate,
    butter_exe,
    ssimul_exe)
from .viewer import ImageViewer


class ComparisonWidget(ToolWidget):
    def __init__(self, filename, image, parent=None):
        super(ComparisonWidget, self).__init__(parent)

        load_button = QPushButton(self.tr('Load reference image...'))
        self.comp_label = QLabel(self.tr('Comparison:'))
        self.normal_radio = QRadioButton(self.tr('Normal'))
        self.normal_radio.setToolTip(self.tr('Show reference (raw pixels)'))
        self.normal_radio.setChecked(True)
        self.difference_radio = QRadioButton(self.tr('Difference'))
        self.difference_radio.setToolTip(self.tr('Show evidence/reference difference'))
        self.ssim_radio = QRadioButton(self.tr('SSIM Map'))
        self.ssim_radio.setToolTip(self.tr('Structure similarity quality map'))
        self.butter_radio = QRadioButton(self.tr('Butteraugli'))
        self.butter_radio.setToolTip(self.tr('Butteraugli spatial changes heatmap'))
        self.gray_check = QCheckBox(self.tr('Grayscale'))
        self.gray_check.setToolTip(self.tr('Show desaturated output'))
        self.equalize_check = QCheckBox(self.tr('Equalized'))
        self.equalize_check.setToolTip(self.tr('Apply histogram equalization'))
        self.last_radio = self.normal_radio
        self.metric_button = QPushButton(self.tr('Compute metrics'))
        self.metric_button.setToolTip(self.tr('Image quality assessment metrics'))

        self.evidence = image
        self.reference = self.difference = self.ssim_map = self.butter_map = None
        basename = os.path.basename(filename)
        self.evidence_viewer = ImageViewer(self.evidence, None, self.tr('Evidence: {}'.format(basename)))
        self.reference_viewer = ImageViewer(np.full_like(self.evidence, 127), None, self.tr('Reference'))

        self.table_widget = QTableWidget(21, 3)
        self.table_widget.setHorizontalHeaderLabels([self.tr('Metric'), self.tr('Value'), self.tr('Better')])
        self.table_widget.setItem(0, 0, QTableWidgetItem(self.tr('RMSE')))
        self.table_widget.setItem(0, 2, QTableWidgetItem(QIcon('gui/icons/low.svg'), '(0)'))
        self.table_widget.item(0, 0).setToolTip(self.tr(
            'Root Mean Square Error (RMSE) is commonly used to compare \n'
            'the difference between the reference and evidence images \n'
            'by directly computing the variation in pixel values. \n'
            'The combined image is close to the reference image when \n'
            'RMSE value is zero. RMSE is a good indicator of the spectral \n'
            'quality of the reference image.'))
        self.table_widget.setItem(1, 0, QTableWidgetItem(self.tr('SAM')))
        self.table_widget.setItem(1, 2, QTableWidgetItem(QIcon('gui/icons/low.svg'), '(0)'))
        self.table_widget.item(1, 0).setToolTip(self.tr(
            'It computes the spectral angle between the pixel, vector of the \n'
            'evidence image and reference image. It is worked out in either \n'
            'degrees or radians. It is performed on a pixel-by-pixel base. \n'
            'A SAM equal to zero denotes the absence of spectral distortion.'))
        self.table_widget.setItem(2, 0, QTableWidgetItem(self.tr('ERGAS')))
        self.table_widget.setItem(2, 2, QTableWidgetItem(QIcon('gui/icons/low.svg'), '(0)'))
        self.table_widget.item(2, 0).setToolTip(self.tr(
            'It is used to compute the quality of reference image in terms \n'
            'of normalized average error of each band of the reference image. \n'
            'Increase in the value of ERGAS indicates distortion in the \n'
            'reference image, lower value of ERGAS indicates that it is \n'
            'similar to the reference image.'))
        self.table_widget.setItem(3, 0, QTableWidgetItem(self.tr('MB')))
        self.table_widget.setItem(3, 2, QTableWidgetItem(QIcon('gui/icons/low.svg'), '(0)'))
        self.table_widget.item(3, 0).setToolTip(self.tr(
            'Mean Bias is the difference between the mean of the evidence \n'
            'image and reference image. The ideal value is zero and indicates \n'
            'that the evidence and reference images are similar. Mean value \n'
            'refers to the grey level of pixels in an image.'))
        self.table_widget.setItem(4, 0, QTableWidgetItem(self.tr('PFE')))
        self.table_widget.setItem(4, 2, QTableWidgetItem(QIcon('gui/icons/low.svg'), '(0)'))
        self.table_widget.item(4, 0).setToolTip(self.tr(
            'It computes the norm of the difference between the corresponding \n'
            'pixels of the reference and fused image to the norm of the reference \n'
            'image. When the calculated value is zero, it indicates that both the \n'
            'reference and fused images are similar and value will be increased \n'
            'when the merged image is not similar to the reference image.'))
        self.table_widget.setItem(5, 0, QTableWidgetItem(self.tr('PSNR')))
        self.table_widget.setItem(5, 2, QTableWidgetItem(QIcon('gui/icons/high.svg'), '(+' + u'\u221e' + ')'))
        self.table_widget.item(5, 0).setToolTip(self.tr(
            'It is widely used metric it is computed by the number of gray levels \n'
            'in the image divided by the corresponding pixels in the evidence and \n'
            'the reference images. When the value is high, both images are similar.'))
        self.table_widget.setItem(6, 0, QTableWidgetItem(self.tr('PSNR-B')))
        self.table_widget.setItem(6, 2, QTableWidgetItem(QIcon('gui/icons/high.svg'), '(+' + u'\u221e' + ')'))
        self.table_widget.item(6, 0).setToolTip(self.tr('PSNR with Blocking Effect Factor.'))
        self.table_widget.setItem(7, 0, QTableWidgetItem(self.tr('SSIM')))
        self.table_widget.setItem(7, 2, QTableWidgetItem(QIcon('gui/icons/high.svg'), '(1)'))
        self.table_widget.item(7, 0).setToolTip(self.tr(
            'SSIM is used to compare the local patterns of pixel intensities between \n'
            ' the reference and fused images. The range varies between -1 to 1. \n'
            'The value 1 indicates the reference and fused images are similar.'))
        self.table_widget.setItem(8, 0, QTableWidgetItem(self.tr('MS-SSIM')))
        self.table_widget.setItem(8, 2, QTableWidgetItem(QIcon('gui/icons/high.svg'), '(1)'))
        self.table_widget.item(8, 0).setToolTip(self.tr('Multiscale version of SSIM.'))
        self.table_widget.setItem(9, 0, QTableWidgetItem(self.tr('RASE')))
        self.table_widget.setItem(9, 2, QTableWidgetItem(QIcon('gui/icons/low.svg'), '(0)'))
        self.table_widget.item(9, 0).setToolTip(self.tr('Relative average spectral error'))
        self.table_widget.setItem(10, 0, QTableWidgetItem(self.tr('SCC')))
        self.table_widget.setItem(10, 2, QTableWidgetItem(QIcon('gui/icons/high.svg'), '(1)'))
        self.table_widget.item(10, 0).setToolTip(self.tr('Spatial Correlation Coefficient'))
        self.table_widget.setItem(11, 0, QTableWidgetItem(self.tr('UQI')))
        self.table_widget.setItem(11, 2, QTableWidgetItem(QIcon('gui/icons/high.svg'), '(1)'))
        self.table_widget.item(11, 0).setToolTip(self.tr('Universal Image Quality Index'))
        self.table_widget.setItem(12, 0, QTableWidgetItem(self.tr('VIF-P')))
        self.table_widget.setItem(12, 2, QTableWidgetItem(QIcon('gui/icons/high.svg'), '(1)'))
        self.table_widget.item(12, 0).setToolTip(self.tr('Pixel-based Visual Information Fidelity'))
        self.table_widget.setItem(13, 0, QTableWidgetItem(self.tr('SSIMulacra')))
        self.table_widget.setItem(13, 2, QTableWidgetItem(QIcon('gui/icons/low.svg'), '(0)'))
        self.table_widget.item(13, 0).setToolTip(self.tr('Structural SIMilarity Unveiling Local '
                                                         'And Compression Related Artifacts'))
        self.table_widget.setItem(14, 0, QTableWidgetItem(self.tr('Butteraugli')))
        self.table_widget.setItem(14, 2, QTableWidgetItem(QIcon('gui/icons/low.svg'), '(0)'))
        self.table_widget.item(14, 0).setToolTip(self.tr('Estimate psychovisual error'))
        self.table_widget.setItem(15, 0, QTableWidgetItem(self.tr('Correlation')))
        self.table_widget.setItem(15, 2, QTableWidgetItem(QIcon('gui/icons/high.svg'), '(1)'))
        self.table_widget.item(15, 0).setToolTip(self.tr('Histogram correlation'))
        self.table_widget.setItem(16, 0, QTableWidgetItem(self.tr('Chi-Square')))
        self.table_widget.setItem(16, 2, QTableWidgetItem(QIcon('gui/icons/low.svg'), '(0)'))
        self.table_widget.item(16, 0).setToolTip(self.tr('Histogram Chi-Square'))
        self.table_widget.setItem(17, 0, QTableWidgetItem(self.tr('Chi-Square 2')))
        self.table_widget.setItem(17, 2, QTableWidgetItem(QIcon('gui/icons/low.svg'), '(0)'))
        self.table_widget.item(17, 0).setToolTip(self.tr('Alternative Chi-Square'))
        self.table_widget.setItem(18, 0, QTableWidgetItem(self.tr('Intersection')))
        self.table_widget.setItem(18, 2, QTableWidgetItem(QIcon('gui/icons/high.svg'), '(+' + u'\u221e' + ')'))
        self.table_widget.item(18, 0).setToolTip(self.tr('Histogram intersection'))
        self.table_widget.setItem(19, 0, QTableWidgetItem(self.tr('Hellinger')))
        self.table_widget.setItem(19, 2, QTableWidgetItem(QIcon('gui/icons/low.svg'), '(0)'))
        self.table_widget.item(19, 0).setToolTip(self.tr('Histogram Hellinger distance'))
        self.table_widget.setItem(20, 0, QTableWidgetItem(self.tr('Divergence')))
        self.table_widget.setItem(20, 2, QTableWidgetItem(QIcon('gui/icons/low.svg'), '(0)'))
        self.table_widget.item(20, 0).setToolTip(self.tr('Kullback-Leibler divergence'))

        for i in range(self.table_widget.rowCount()):
            modify_font(self.table_widget.item(i, 0), bold=True)
        self.table_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_widget.resizeColumnsToContents()
        self.table_widget.setMaximumWidth(250)
        self.table_widget.setAlternatingRowColors(True)
        self.stopped = False

        self.comp_label.setEnabled(False)
        self.normal_radio.setEnabled(False)
        self.difference_radio.setEnabled(False)
        self.ssim_radio.setEnabled(False)
        self.butter_radio.setEnabled(False)
        self.gray_check.setEnabled(False)
        self.equalize_check.setEnabled(False)
        self.metric_button.setEnabled(False)
        self.table_widget.setEnabled(False)

        load_button.clicked.connect(self.load)
        self.normal_radio.clicked.connect(self.change)
        self.difference_radio.clicked.connect(self.change)
        self.butter_radio.clicked.connect(self.change)
        self.gray_check.stateChanged.connect(self.change)
        self.equalize_check.stateChanged.connect(self.change)
        self.ssim_radio.clicked.connect(self.change)
        self.evidence_viewer.viewChanged.connect(self.reference_viewer.changeView)
        self.reference_viewer.viewChanged.connect(self.evidence_viewer.changeView)
        self.metric_button.clicked.connect(self.metrics)

        top_layout = QHBoxLayout()
        top_layout.addWidget(load_button)
        top_layout.addStretch()
        top_layout.addWidget(self.comp_label)
        top_layout.addWidget(self.normal_radio)
        top_layout.addWidget(self.difference_radio)
        top_layout.addWidget(self.ssim_radio)
        top_layout.addWidget(self.butter_radio)
        top_layout.addWidget(self.gray_check)
        top_layout.addWidget(self.equalize_check)

        metric_layout = QVBoxLayout()
        index_label = QLabel(self.tr('Image Quality Assessment'))
        index_label.setAlignment(Qt.AlignCenter)
        modify_font(index_label, bold=True)
        metric_layout.addWidget(index_label)
        metric_layout.addWidget(self.table_widget)
        metric_layout.addWidget(self.metric_button)

        center_layout = QHBoxLayout()
        center_layout.addWidget(self.evidence_viewer)
        center_layout.addWidget(self.reference_viewer)
        center_layout.addLayout(metric_layout)

        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addLayout(center_layout)
        self.setLayout(main_layout)

    def load(self):
        filename, basename, reference = load_image(self)
        if filename is None:
            return
        if reference.shape != self.evidence.shape:
            QMessageBox.critical(self, self.tr('Error'), self.tr('Evidence and reference must have the same size!'))
            return
        self.reference = reference
        self.reference_viewer.set_title(self.tr('Reference: {}'.format(basename)))
        self.difference = norm_mat(cv.absdiff(self.evidence, self.reference))

        self.comp_label.setEnabled(True)
        self.normal_radio.setEnabled(True)
        self.difference_radio.setEnabled(True)
        self.ssim_radio.setEnabled(False)
        self.butter_radio.setEnabled(False)
        self.gray_check.setEnabled(True)
        self.equalize_check.setEnabled(True)
        self.metric_button.setEnabled(True)
        for i in range(self.table_widget.rowCount()):
            self.table_widget.setItem(i, 1, QTableWidgetItem())
        self.normal_radio.setChecked(True)
        self.table_widget.setEnabled(False)
        self.change()

    def change(self):
        if self.normal_radio.isChecked():
            result = self.reference
            self.gray_check.setEnabled(False)
            self.equalize_check.setEnabled(False)
            self.last_radio = self.normal_radio
        elif self.difference_radio.isChecked():
            result = self.difference
            self.gray_check.setEnabled(True)
            self.equalize_check.setEnabled(True)
            self.last_radio = self.difference_radio
        elif self.ssim_radio.isChecked():
            result = self.ssim_map
            self.gray_check.setEnabled(False)
            self.equalize_check.setEnabled(True)
            self.last_radio = self.ssim_radio
        elif self.butter_radio.isChecked():
            result = self.butter_map
            self.gray_check.setEnabled(True)
            self.equalize_check.setEnabled(False)
            self.last_radio = self.butter_radio
        else:
            self.last_radio.setChecked(True)
            return
        if self.equalize_check.isChecked():
            result = equalize_img(result)
        if self.gray_check.isChecked():
            result = desaturate(result)
        self.reference_viewer.update_original(result)

    def metrics(self):
        progress = QProgressDialog(
            self.tr('Computing metrics...'), self.tr('Cancel'), 1, self.table_widget.rowCount(), self)
        progress.canceled.connect(self.cancel)
        progress.setWindowModality(Qt.WindowModal)
        img1 = cv.cvtColor(self.evidence, cv.COLOR_BGR2GRAY)
        img2 = cv.cvtColor(self.reference, cv.COLOR_BGR2GRAY)
        x = img1.astype(np.float64)
        y = img2.astype(np.float64)

        rmse = self.rmse(x, y)
        progress.setValue(1)
        if self.stopped:
            return
        sam = sewar.sam(img1, img2)
        progress.setValue(2)
        if self.stopped:
            return
        ergas = sewar.ergas(img1, img2)
        progress.setValue(3)
        if self.stopped:
            return
        mb = self.mb(x, y)
        progress.setValue(4)
        if self.stopped:
            return
        pfe = self.pfe(x, y)
        progress.setValue(5)
        if self.stopped:
            return
        psnr = self.psnr(x, y)
        progress.setValue(6)
        if self.stopped:
            return
        try:
            psnrb = sewar.psnrb(img1, img2)
        except NameError:
            # FIXME: C'\`e un bug in psnrb (https://github.com/andrewekhalel/sewar/issues/17)
            psnrb = 0
        progress.setValue(7)
        if self.stopped:
            return
        ssim, self.ssim_map = self.ssim(x, y)
        progress.setValue(8)
        if self.stopped:
            return
        mssim = sewar.msssim(img1, img2).real
        progress.setValue(9)
        if self.stopped:
            return
        rase = sewar.rase(img1, img2)
        progress.setValue(10)
        if self.stopped:
            return
        scc = sewar.scc(img1, img2)
        progress.setValue(11)
        if self.stopped:
            return
        uqi = sewar.uqi(img1, img2)
        progress.setValue(12)
        if self.stopped:
            return
        vifp = sewar.vifp(img1, img2)
        progress.setValue(13)
        if self.stopped:
            return
        ssimul = self.ssimul(img1, img2)
        progress.setValue(14)
        if self.stopped:
            return
        butter, self.butter_map = self.butter(img1, img2)
        progress.setValue(15)
        if self.stopped:
            return

        sizes = [256, 256, 256]
        ranges = [0, 256] * 3
        channels = [0, 1, 2]
        hist1 = cv.calcHist([self.evidence], channels, None, sizes, ranges)
        hist2 = cv.calcHist([self.reference], channels, None, sizes, ranges)
        correlation = cv.compareHist(hist1, hist2, cv.HISTCMP_CORREL)
        progress.setValue(16)
        if self.stopped:
            return
        chi_square = cv.compareHist(hist1, hist2, cv.HISTCMP_CHISQR)
        progress.setValue(17)
        if self.stopped:
            return
        chi_square2 = cv.compareHist(hist1, hist2, cv.HISTCMP_CHISQR_ALT)
        progress.setValue(18)
        if self.stopped:
            return
        intersection = cv.compareHist(hist1, hist2, cv.HISTCMP_INTERSECT)
        progress.setValue(19)
        if self.stopped:
            return
        hellinger = cv.compareHist(hist1, hist2, cv.HISTCMP_HELLINGER)
        progress.setValue(20)
        if self.stopped:
            return
        divergence = cv.compareHist(hist1, hist2, cv.HISTCMP_KL_DIV)
        progress.setValue(21)

        self.table_widget.setItem(0, 1, QTableWidgetItem('{:.2f}'.format(rmse)))
        self.table_widget.setItem(1, 1, QTableWidgetItem('{:.4f}'.format(sam)))
        self.table_widget.setItem(2, 1, QTableWidgetItem('{:.2f}'.format(ergas)))
        self.table_widget.setItem(3, 1, QTableWidgetItem('{:.4f}'.format(mb)))
        self.table_widget.setItem(4, 1, QTableWidgetItem('{:.2f}'.format(pfe)))
        if psnr > 0:
            self.table_widget.setItem(5, 1, QTableWidgetItem('{:.2f} dB'.format(psnr)))
        else:
            self.table_widget.setItem(5, 1, QTableWidgetItem('+' + u'\u221e' + ' dB'))
        self.table_widget.setItem(6, 1, QTableWidgetItem('{:.2f}'.format(psnrb)))
        self.table_widget.setItem(7, 1, QTableWidgetItem('{:.4f}'.format(ssim)))
        self.table_widget.setItem(8, 1, QTableWidgetItem('{:.4f}'.format(mssim)))
        self.table_widget.setItem(9, 1, QTableWidgetItem('{:.2f}'.format(rase)))
        self.table_widget.setItem(10, 1, QTableWidgetItem('{:.4f}'.format(scc)))
        self.table_widget.setItem(11, 1, QTableWidgetItem('{:.4f}'.format(uqi)))
        self.table_widget.setItem(12, 1, QTableWidgetItem('{:.4f}'.format(vifp)))
        self.table_widget.setItem(13, 1, QTableWidgetItem('{:.4f}'.format(ssimul)))
        self.table_widget.setItem(14, 1, QTableWidgetItem('{:.2f}'.format(butter)))
        self.table_widget.setItem(15, 1, QTableWidgetItem('{:.2f}'.format(correlation)))
        self.table_widget.setItem(16, 1, QTableWidgetItem('{:.2f}'.format(chi_square)))
        self.table_widget.setItem(17, 1, QTableWidgetItem('{:.2f}'.format(chi_square2)))
        self.table_widget.setItem(18, 1, QTableWidgetItem('{:.2f}'.format(intersection)))
        self.table_widget.setItem(19, 1, QTableWidgetItem('{:.2f}'.format(hellinger)))
        self.table_widget.setItem(20, 1, QTableWidgetItem('{:.2f}'.format(divergence)))
        self.table_widget.resizeColumnsToContents()
        self.table_widget.setEnabled(True)
        self.metric_button.setEnabled(False)
        self.ssim_radio.setEnabled(True)
        self.butter_radio.setEnabled(True)

    def cancel(self):
        self.stopped = True

    @staticmethod
    def rmse(x, y):
        return np.sqrt(np.mean(np.square(x - y)))

    @staticmethod
    def mb(x, y):
        mx = np.mean(x)
        my = np.mean(y)
        return (mx - my) / mx

    @staticmethod
    def pfe(x, y):
        return np.linalg.norm(x - y) / np.linalg.norm(x) * 100

    @staticmethod
    def ssim(x, y):
        c1 = 6.5025
        c2 = 58.5225
        k = (11, 11)
        s = 1.5
        x2 = x ** 2
        y2 = y ** 2
        xy = x * y
        mu_x = cv.GaussianBlur(x, k, s)
        mu_y = cv.GaussianBlur(y, k, s)
        mu_x2 = mu_x ** 2
        mu_y2 = mu_y ** 2
        mu_xy = mu_x * mu_y
        s_x2 = cv.GaussianBlur(x2, k, s) - mu_x2
        s_y2 = cv.GaussianBlur(y2, k, s) - mu_y2
        s_xy = cv.GaussianBlur(xy, k, s) - mu_xy
        t1 = 2 * mu_xy + c1
        t2 = 2 * s_xy + c2
        t3 = t1 * t2
        t1 = mu_x2 + mu_y2 + c1
        t2 = s_x2 + s_y2 + c2
        t1 *= t2
        ssim_map = cv.divide(t3, t1)
        ssim = cv.mean(ssim_map)[0]
        return ssim, 255 - norm_mat(ssim_map, to_bgr=True)

    @staticmethod
    def corr(x, y):
        return np.corrcoef(x, y)[0, 1]

    @staticmethod
    def psnr(x, y):
        k = np.mean(np.square(x - y))
        if k == 0:
            return -1
        return 20 * math.log10((255**2) / k)

    @staticmethod
    def butter(x, y):
        try:
            exe = butter_exe()
            if exe is None:
                raise FileNotFoundError
            temp_dir = QTemporaryDir()
            if temp_dir.isValid():
                filename1 = os.path.join(temp_dir.path(), 'img1.png')
                cv.imwrite(filename1, x)
                filename2 = os.path.join(temp_dir.path(), 'img2.png')
                cv.imwrite(filename2, y)
                filename3 = os.path.join(temp_dir.path(), 'map.ppm')
                p = run([exe, filename1, filename2, filename3], stdout=PIPE)
                value = float(p.stdout)
                heatmap = cv.imread(filename3, cv.IMREAD_COLOR)
                return value, heatmap
        except FileNotFoundError:
            return -1, cv.cvtColor(np.full_like(x, 127), cv.COLOR_GRAY2BGR)

    @staticmethod
    def ssimul(x, y):
        try:
            exe = ssimul_exe()
            if exe is None:
                raise FileNotFoundError
            temp_dir = QTemporaryDir()
            if temp_dir.isValid():
                filename1 = os.path.join(temp_dir.path(), 'img1.png')
                cv.imwrite(filename1, x)
                filename2 = os.path.join(temp_dir.path(), 'img2.png')
                cv.imwrite(filename2, y)
                p = run([exe, filename1, filename2], stdout=PIPE)
                value = float(p.stdout)
                return value
        except FileNotFoundError:
            return -1
