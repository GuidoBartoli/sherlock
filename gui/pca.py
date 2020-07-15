import cv2 as cv
import numpy as np
from PySide2.QtWidgets import (
    QAbstractItemView,
    QTableWidgetItem,
    QTableWidget,
    QVBoxLayout,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QRadioButton,
    QCheckBox)

from .tools import ToolWidget
from .utility import norm_mat, modify_font, norm_img, equalize_img
from .viewer import ImageViewer


class PcaWidget(ToolWidget):
    def __init__(self, image, parent=None):
        super(PcaWidget, self).__init__(parent)

        self.component_combo = QComboBox()
        self.component_combo.addItems([self.tr('#{}'.format(i + 1)) for i in range(3)])
        self.distance_radio = QRadioButton(self.tr('Distance'))
        self.distance_radio.setToolTip(self.tr('Distance from the closest point on selected component'))
        self.project_radio = QRadioButton(self.tr('Projection'))
        self.project_radio.setToolTip(self.tr('Projection onto the selected principal component'))
        self.crossprod_radio = QRadioButton(self.tr('Cross product'))
        self.crossprod_radio.setToolTip(self.tr('Cross product between input and selected component'))
        self.distance_radio.setChecked(True)
        self.last_radio = self.distance_radio
        self.invert_check = QCheckBox(self.tr('Invert'))
        self.invert_check.setToolTip(self.tr('Output bitwise complement'))
        self.equalize_check = QCheckBox(self.tr('Equalize'))
        self.equalize_check.setToolTip(self.tr('Apply histogram equalization'))

        rows, cols, chans = image.shape
        x = np.reshape(image, (rows * cols, chans)).astype(np.float32)
        mu, ev, ew = cv.PCACompute2(x, np.array([]))
        p = np.reshape(cv.PCAProject(x, mu, ev), (rows, cols, chans))
        x0 = image.astype(np.float32) - mu
        self.output = []
        for i, v in enumerate(ev):
            cross = np.cross(x0, v)
            distance = np.linalg.norm(cross, axis=2) / np.linalg.norm(v)
            project = p[:, :, i]
            self.output.extend([norm_mat(distance, to_bgr=True), norm_mat(project, to_bgr=True), norm_img(cross)])

        table_data = [[mu[0, 2], mu[0, 1], mu[0, 0]],
                      [ev[0, 2], ev[0, 1], ev[0, 0]],
                      [ev[1, 2], ev[1, 1], ev[1, 0]],
                      [ev[2, 2], ev[2, 1], ev[2, 0]],
                      [ew[2, 0], ew[1, 0], ew[0, 0]]]
        table_widget = QTableWidget(5, 4)
        table_widget.setHorizontalHeaderLabels([
            self.tr('Element'), self.tr('Red'), self.tr('Green'), self.tr('Blue')])
        table_widget.setItem(0, 0, QTableWidgetItem(self.tr('Mean vector')))
        table_widget.setItem(1, 0, QTableWidgetItem(self.tr('Eigenvector 1')))
        table_widget.setItem(2, 0, QTableWidgetItem(self.tr('Eigenvector 2')))
        table_widget.setItem(3, 0, QTableWidgetItem(self.tr('Eigenvector 3')))
        table_widget.setItem(4, 0, QTableWidgetItem(self.tr('Eigenvalues')))
        for i in range(len(table_data)):
            modify_font(table_widget.item(i, 0), bold=True)
            for j in range(len(table_data[i])):
                table_widget.setItem(i, j + 1, QTableWidgetItem(str(table_data[i][j])))
        # item = QTableWidgetItem()
        # item.setBackgroundColor(QColor(mu[0, 2], mu[0, 1], mu[0, 0]))
        # table_widget.setItem(0, 4, item)
        # table_widget.resizeRowsToContents()
        # table_widget.resizeColumnsToContents()
        table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        table_widget.setMaximumHeight(190)

        self.viewer = ImageViewer(image, image, None)
        self.process()

        self.component_combo.currentIndexChanged.connect(self.process)
        self.distance_radio.clicked.connect(self.process)
        self.project_radio.clicked.connect(self.process)
        self.crossprod_radio.clicked.connect(self.process)
        self.invert_check.stateChanged.connect(self.process)
        self.equalize_check.stateChanged.connect(self.process)

        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel(self.tr('Component:')))
        top_layout.addWidget(self.component_combo)
        top_layout.addWidget(QLabel(self.tr('Mode:')))
        top_layout.addWidget(self.distance_radio)
        top_layout.addWidget(self.project_radio)
        top_layout.addWidget(self.crossprod_radio)
        top_layout.addWidget(self.invert_check)
        top_layout.addWidget(self.equalize_check)
        top_layout.addStretch()
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(table_widget)

        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.viewer)
        main_layout.addLayout(bottom_layout)
        self.setLayout(main_layout)

    def process(self):
        index = 3*self.component_combo.currentIndex()
        if self.distance_radio.isChecked():
            output = self.output[index]
            self.last_radio = self.distance_radio
        elif self.project_radio.isChecked():
            output = self.output[index + 1]
            self.last_radio = self.project_radio
        elif self.crossprod_radio.isChecked():
            output = self.output[index + 2]
            self.last_radio = self.crossprod_radio
        else:
            self.last_radio.setChecked(True)
            return
        if self.invert_check.isChecked():
            output = cv.bitwise_not(output)
        if self.equalize_check.isChecked():
            output = equalize_img(output)
        self.viewer.update_processed(output)
