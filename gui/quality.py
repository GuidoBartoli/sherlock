import subprocess
from shutil import copyfile

import cv2 as cv
import numpy as np
from PySide2.QtCore import QTemporaryFile, Qt
from PySide2.QtGui import QColor
from PySide2.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QGridLayout,
    QTableWidget,
    QTableWidgetItem,
    QAbstractItemView)

from .jpeg import TABLE_SIZE, ZIG_ZAG, DCT_SIZE, get_tables
from .tools import ToolWidget
from .utility import modify_font, exiftool_exe, clip_value


class QualityWidget(ToolWidget):
    def __init__(self, filename, parent=None):
        super(QualityWidget, self).__init__(parent)

        MRK = b'\xFF'
        SOI = b'\xD8'
        DQT = b'\xDB'
        # DHT = b'\xC4'
        MSK = b'\x0F'
        PAD = b'\x00'

        MAX_TABLES = 2
        LEN_OFFSET = 2
        LUMA_IDX = 0
        CHROMA_IDX = 1

        luma = np.zeros((DCT_SIZE, DCT_SIZE), dtype=int)
        chroma = np.zeros((DCT_SIZE, DCT_SIZE), dtype=int)
        temp_file = QTemporaryFile()
        if temp_file.open():
            copyfile(filename, temp_file.fileName())
            subprocess.run([exiftool_exe(), '-all=', '-overwrite_original', temp_file.fileName()],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            found = False
            with open(temp_file.fileName(), 'rb') as file:
                first = file.read(1)
                if first not in [MRK, SOI]:
                    self.show_error(self.tr('File is not a JPEG image!'))
                    return
                while True:
                    if not self.find_next(file, [MRK, DQT, PAD]):
                        break
                    length = file.read(1)[0] - LEN_OFFSET
                    if length <= 0 or length % (TABLE_SIZE + 1) != 0:
                        continue
                    while length > 0:
                        mode = file.read(1)
                        if not mode:
                            break
                        index = mode[0] & MSK[0]
                        if index >= MAX_TABLES:
                            break
                        length -= 1
                        for k in range(TABLE_SIZE):
                            b = file.read(1)[0]
                            if not b:
                                break
                            length -= 1
                            i, j = ZIG_ZAG[k]
                            if index == LUMA_IDX:
                                luma[i, j] = b
                            elif index == CHROMA_IDX:
                                chroma[i, j] = b
                        else:
                            found = True
        if not found:
            self.show_error(self.tr('Unable to find JPEG tables!'))
            return

        levels = [(1 - (np.mean(t.ravel()[1:]) - 1) / 254) * 100 for t in [luma, chroma]]
        distance = np.zeros(101)
        for q in range(101):
            lu, ch = cv.split(get_tables(q))
            lu_diff = np.mean(cv.absdiff(luma, lu))
            ch_diff = np.mean(cv.absdiff(chroma, ch))
            distance[q] = (lu_diff + 2 * ch_diff) / 3
        closest = np.argmin(distance)
        deviation = distance[closest]
        if deviation == 0:
            quality = closest
            message = '(standard tables)'
        else:
            quality = int(np.round(closest - deviation))
            message = '(deviation from standard = {:.4f})'.format(deviation)
        quality_label = QLabel(self.tr('Last saved JPEG quality: {}% {}'.format(quality, message)))
        modify_font(quality_label, bold=True)

        luma_label = QLabel(self.tr('Luminance Quantization Table (level = {:.2f}%)\n'.format(levels[0])))
        luma_label.setAlignment(Qt.AlignCenter)
        modify_font(luma_label, underline=True)
        luma_table = self.create_table(luma)
        luma_table.setMaximumHeight(200)
        chroma_label = QLabel(self.tr('Chrominance Quantization Table (level = {:.2f}%)\n'.format(levels[1])))
        chroma_label.setAlignment(Qt.AlignCenter)
        modify_font(chroma_label, underline=True)
        chroma_table = self.create_table(chroma)
        chroma_table.setMaximumHeight(200)

        main_layout = QGridLayout()
        main_layout.addWidget(luma_label, 0, 0)
        main_layout.addWidget(luma_table, 1, 0)
        main_layout.addWidget(chroma_label, 0, 1)
        main_layout.addWidget(chroma_table, 1, 1)
        main_layout.addWidget(quality_label, 2, 0, 1, 2)
        self.setLayout(main_layout)
        self.setFixedSize(880, 270)

    def show_error(self, message):
        error_label = QLabel(message)
        modify_font(error_label, bold=True)
        error_label.setStyleSheet('color: #FF0000')
        error_label.setAlignment(Qt.AlignCenter)
        main_layout = QVBoxLayout()
        main_layout.addWidget(error_label)
        self.setLayout(main_layout)

    @staticmethod
    def find_next(file, markers):
        while True:
            for m in markers:
                b = file.read(1)
                if not b:
                    return False
                if b != m:
                    break
            else:
                return True

    @staticmethod
    def create_table(matrix):
        table_widget = QTableWidget(DCT_SIZE, DCT_SIZE)
        hsv = np.array([[[0, 192, 255]]])
        maximum = clip_value(np.max(matrix) - 1, minv=1)
        for i in range(DCT_SIZE):
            for j in range(DCT_SIZE):
                value = matrix[i, j]
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                hsv[0, 0, 0] = 64 - 64 * ((value - 1) / maximum)
                rgb = cv.cvtColor(hsv.astype(np.uint8), cv.COLOR_HSV2RGB)
                item.setBackgroundColor(QColor(rgb[0, 0, 0], rgb[0, 0, 1], rgb[0, 0, 2]))
                table_widget.setItem(i, j, item)
        table_widget.resizeRowsToContents()
        table_widget.resizeColumnsToContents()
        table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        modify_font(table_widget, mono=True)
        return table_widget
