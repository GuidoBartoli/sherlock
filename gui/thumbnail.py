import subprocess

import cv2 as cv
from PySide2.QtCore import QTemporaryFile, Qt
from PySide2.QtWidgets import (
    QLabel,
    QVBoxLayout)

from .tools import ToolWidget
from .utility import modify_font, exiftool_exe
from .viewer import ImageViewer


class ThumbWidget(ToolWidget):
    def __init__(self, filename, image, parent=None):
        super(ThumbWidget, self).__init__(parent)

        temp_file = QTemporaryFile()
        if temp_file.open():
            output = subprocess.check_output([exiftool_exe(), '-b', '-ThumbnailImage', filename])
            temp_name = temp_file.fileName()
            with open(temp_name, 'wb') as file:
                file.write(output)
            thumb = cv.imread(temp_name, cv.IMREAD_COLOR)
            if thumb is None:
                self.show_error(self.tr('Thumbnail image not found!'))
                return
            # resized = cv.resize(image, thumb.shape[:-1][::-1], interpolation=cv.INTER_AREA)
            resized = cv.resize(thumb, image.shape[:-1][::-1], interpolation=cv.INTER_LANCZOS4)
            diff = cv.absdiff(image, resized)

            # image_aspect = image.shape[1] / image.shape[0]
            # thumb_aspect = thumb.shape[1] / thumb.shape[0]
            # if thumb_aspect < image_aspect:
            #     shape = (thumb.shape[1] // image_aspect, thumb.shape[1])
            # elif thumb_aspect > image_aspect:
            #     shape = (thumb.shape[0], thumb.shape[0] * image_aspect)
            # else:
            #     shape = thumb.shape
            # resized = cv.resize(image, shape, None, 0, 0, interpolation=cv.INTER_AREA)
            # top = (thumb.shape[0] - resized.shape[0]) / 2
            # bottom = top
            # left = (thumb.shape[1] - resized.shape[1]) / 2
            # right = left
            # padded = cv.copyMakeBorder(resized, top, bottom, left, right, cv.BORDER_CONSTANT)
            # if padded.shape != thumb.shape:
            #     padded = cv.resize(padded, thumb.shape, interpolation=cv.INTER_AREA)
            # diff = cv.cvtColor(cv.absdiff(thumb, padded), cv.COLOR_BGR2GRAY)

            viewer = ImageViewer(resized, diff)
            layout = QVBoxLayout()
            layout.addWidget(viewer)
            self.setLayout(layout)

    def show_error(self, message):
        error_label = QLabel(message)
        modify_font(error_label, bold=True)
        error_label.setStyleSheet('color: #FF0000')
        error_label.setAlignment(Qt.AlignCenter)
        main_layout = QVBoxLayout()
        main_layout.addWidget(error_label)
        self.setLayout(main_layout)
