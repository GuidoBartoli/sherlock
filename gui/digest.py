import os
import re

import cv2 as cv
import magic
from PySide2.QtCore import (
    QFileInfo,
    QLocale,
    QFile,
    QIODevice,
    QCryptographicHash)
from PySide2.QtWidgets import (
    QVBoxLayout,
    QMessageBox)

from .table import TableWidget
from .tools import ToolWidget
from .utility import human_size


def ballistics(filename):
    table = [['^DSCN[0-9]{4}\\.JPG$', 'Nikon Coolpix camera'],
             ['^DSC_[0-9]{4}\\.JPG$', 'Nikon digital camera'],
             ['^FUJI[0-9]{4}\\.JPG$', 'Fujifilm digital camera'],
             ['^IMG_[0-9]{4}\\.JPG$', 'Canon DSLR or iPhone camera'],
             ['^PIC[0-9]{5}\\.JPG$', 'Olympus D-600L camera']]
    for entry in table:
        if re.match(entry[0], filename, re.IGNORECASE) is not None:
            return entry[1]
    return 'Unknown source or manually renamed'


class DigestWidget(ToolWidget):
    def __init__(self, filename, image, parent=None):
        super(DigestWidget, self).__init__(parent)

        table = []

        file_info = QFileInfo(filename)
        table.append([self.tr('File'), self.tr('File name'), file_info.fileName()])
        table.append([None, self.tr('Parent folder'), str(file_info.dir().absolutePath())])
        table.append([None, self.tr('MIME type'), magic.from_file(filename, mime=True)])
        table.append([None, self.tr('File size'), '{} bytes ({})'.format(
            QLocale().toString(file_info.size()), human_size(file_info.size()))])
        table.append([None, self.tr('File owner'), file_info.owner()])
        table.append([None, self.tr('Permissions'), str(oct(os.stat(filename).st_mode)[-3:])])
        table.append([None, self.tr('Creation time'), file_info.birthTime().toLocalTime().toString()])
        table.append([None, self.tr('Last access'), file_info.lastRead().toLocalTime().toString()])
        table.append([None, self.tr('Last modified'), file_info.lastModified().toLocalTime().toString()])
        table.append([None, self.tr('Metadata changed'), file_info.metadataChangeTime().toLocalTime().toString()])
        table.append([None, self.tr('Name ballistics'), ballistics(file_info.fileName())])

        file = QFile(filename)
        if not file.open(QIODevice.ReadOnly):
            QMessageBox.warning(self, self.tr('Warning'), self.tr('Unable to read file from disk!'))
            return
        data = file.readAll()
        md5 = QCryptographicHash.hash(data, QCryptographicHash.Md5).toHex()
        table.append([self.tr('CryptoHash'), self.tr('MD5'), str(md5, encoding='utf-8')])
        sha1 = QCryptographicHash.hash(data, QCryptographicHash.Sha1).toHex()
        table.append([None, self.tr('SHA2-1'), str(sha1, encoding='utf-8')])
        sha224 = QCryptographicHash.hash(data, QCryptographicHash.Sha224).toHex()
        table.append([None, self.tr('SHA2-224'), str(sha224, encoding='utf-8')])
        sha256 = QCryptographicHash.hash(data, QCryptographicHash.Sha256).toHex()
        table.append([None, self.tr('SHA2-256'), str(sha256, encoding='utf-8')])
        sha384 = QCryptographicHash.hash(data, QCryptographicHash.Sha384).toHex()
        table.append([None, self.tr('SHA2-384'), str(sha384, encoding='utf-8')])
        sha512 = QCryptographicHash.hash(data, QCryptographicHash.Sha512).toHex()
        table.append([None, self.tr('SHA2-512'), str(sha512, encoding='utf-8')])

        sha3_224 = QCryptographicHash.hash(data, QCryptographicHash.Sha3_224).toHex()
        table.append([None, self.tr('SHA3-224'), str(sha3_224, encoding='utf-8')])
        sha3_256 = QCryptographicHash.hash(data, QCryptographicHash.Sha3_256).toHex()
        table.append([None, self.tr('SHA3-256'), str(sha3_256, encoding='utf-8')])
        sha3_384 = QCryptographicHash.hash(data, QCryptographicHash.Sha3_384).toHex()
        table.append([None, self.tr('SHA3-384'), str(sha3_384, encoding='utf-8')])
        sha3_512 = QCryptographicHash.hash(data, QCryptographicHash.Sha3_512).toHex()
        table.append([None, self.tr('SHA3-512'), str(sha3_512, encoding='utf-8')])

        table.append([self.tr('ImageHash'), self.tr('Average'), str(cv.img_hash.averageHash(image)[0])])
        # table_widget.item(15, 0).setToolTip(self.tr('Average hash'))
        table.append([None, self.tr('Block mean'), str(cv.img_hash.blockMeanHash(image)[0])])
        # table_widget.item(16, 0).setToolTip(self.tr('Block mean hash'))
        table.append([None, self.tr('Color moments'), str(cv.img_hash.colorMomentHash(image)[0])])
        # table_widget.item(17, 0).setToolTip(self.tr('Color moments hash'))
        table.append([None, self.tr('Marr-Hildreth'), str(cv.img_hash.marrHildrethHash(image)[0])])
        # table_widget.item(18, 0).setToolTip(self.tr('Marr-Hildreth hash'))
        table.append([None, self.tr('Perceptual'), str(cv.img_hash.pHash(image)[0])])
        # table_widget.item(19, 0).setToolTip(self.tr('Perceptual hash'))
        table.append([None, self.tr('Radial variance'), str(cv.img_hash.radialVarianceHash(image)[0])])
        # table_widget.item(20, 0).setToolTip(self.tr('Radial variance hash'))

        headers = [self.tr('Group'), self.tr('Property'), self.tr('Value')]
        table_widget = TableWidget(table, headers)
        main_layout = QVBoxLayout()
        main_layout.addWidget(table_widget)
        self.setLayout(main_layout)
        self.setMinimumSize(700, 520)
