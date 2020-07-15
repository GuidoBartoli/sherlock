from time import time

import cv2 as cv
import numpy as np
from PySide2.QtWidgets import (
    QHBoxLayout,
    QSpinBox,
    QCheckBox,
    QWidget,
    QComboBox,
    QLabel,
    QVBoxLayout,
    QDoubleSpinBox,
    QGridLayout,
    QTabWidget)
from matplotlib.backends.backend_qt5agg import (
    FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure

from .tools import ToolWidget
from .utility import elapsed_time


class PlotsWidget(ToolWidget):
    def __init__(self, image, parent=None):
        super(PlotsWidget, self).__init__(parent)

        choices = ['Red', 'Green', 'Blue', 'Hue', 'Saturation', 'Value']
        self.xaxis_combo = QComboBox()
        self.xaxis_combo.addItems(choices)
        self.xaxis_combo.setCurrentIndex(3)
        self.yaxis_combo = QComboBox()
        self.yaxis_combo.addItems(choices)
        self.yaxis_combo.setCurrentIndex(4)
        self.zaxis_combo = QComboBox()
        self.zaxis_combo.addItems(choices)
        self.zaxis_combo.setCurrentIndex(5)
        self.sampling_spin = QSpinBox()
        levels = int(np.log2(min(image.shape[:-1])))
        self.sampling_spin.setRange(0, levels)
        self.sampling_spin.setSpecialValueText(self.tr('Off'))
        # self.sampling_spin.setSuffix(self.tr(' level(s)'))
        self.sampling_spin.setValue(1)
        self.size_spin = QSpinBox()
        self.size_spin.setRange(1, 10)
        self.size_spin.setValue(1)
        self.size_spin.setSuffix(self.tr(' pt'))
        self.style_combo = QComboBox()
        self.markers = [',', '.', 'o', '8', 's', 'p', 'P', '*', 'h', 'H', 'X', 'D']
        self.style_combo.addItems(
            ['pixel', 'point', 'circle', 'octa', 'square', 'penta', 'plus', 'star', 'hexa1', 'hexa2', 'cross', 'diamond'])
        self.alpha_spin = QDoubleSpinBox()
        self.alpha_spin.setRange(0, 1)
        self.alpha_spin.setDecimals(2)
        self.alpha_spin.setSingleStep(0.05)
        self.alpha_spin.setValue(1)
        self.colors_check = QCheckBox(self.tr('Show colors'))
        self.grid_check = QCheckBox(self.tr('Show grid'))
        self.norm_check = QCheckBox(self.tr('Normalized'))
        self.total_label = QLabel()

        img = np.copy(image)
        self.colors = [None] * (levels + 1)
        for scale in range(levels + 1):
            rgb = cv.cvtColor(img.astype(np.float32) / 255, cv.COLOR_BGR2RGB)
            hsv = cv.cvtColor(rgb, cv.COLOR_RGB2HSV)
            hsv[:, :, 0] /= 360
            shape = (img.shape[0] * img.shape[1], img.shape[2])
            self.colors[scale] = np.concatenate((np.reshape(rgb, shape), np.reshape(hsv, shape)), axis=1)
            img = cv.pyrDown(img)

        figure2 = Figure()
        plot2_canvas = FigureCanvas(figure2)
        self.axes2 = plot2_canvas.figure.subplots()
        toolbar2 = NavigationToolbar(plot2_canvas, self)
        plot2_layout = QVBoxLayout()
        plot2_layout.addWidget(plot2_canvas)
        plot2_layout.addWidget(toolbar2)
        plot2_widget = QWidget()
        plot2_widget.setLayout(plot2_layout)

        figure3 = Figure()
        plot3_canvas = FigureCanvas(figure3)
        self.axes3 = plot3_canvas.figure.add_subplot(111, projection='3d')
        toolbar3 = NavigationToolbar(plot3_canvas, self)
        plot3_layout = QVBoxLayout()
        plot3_layout.addWidget(plot3_canvas)
        plot3_layout.addWidget(toolbar3)
        plot3_widget = QWidget()
        plot3_widget.setLayout(plot3_layout)

        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(plot2_widget, '2D Plot')
        self.tab_widget.addTab(plot3_widget, '3D Plot')
        self.redraw()
        figure2.set_tight_layout(True)
        figure3.set_tight_layout(True)

        self.xaxis_combo.currentIndexChanged.connect(self.redraw)
        self.yaxis_combo.currentIndexChanged.connect(self.redraw)
        self.zaxis_combo.currentIndexChanged.connect(self.redraw)
        self.sampling_spin.valueChanged.connect(self.redraw)
        self.size_spin.valueChanged.connect(self.redraw)
        self.style_combo.currentIndexChanged.connect(self.redraw)
        self.alpha_spin.valueChanged.connect(self.redraw)
        self.colors_check.stateChanged.connect(self.redraw)
        self.grid_check.stateChanged.connect(self.redraw)
        self.norm_check.stateChanged.connect(self.redraw)
        self.tab_widget.currentChanged.connect(self.redraw)

        params_layout = QGridLayout()
        params_layout.addWidget(QLabel(self.tr('X axis:')), 0, 0)
        params_layout.addWidget(self.xaxis_combo, 0, 1)
        params_layout.addWidget(QLabel(self.tr('Y axis:')), 1, 0)
        params_layout.addWidget(self.yaxis_combo, 1, 1)
        params_layout.addWidget(QLabel(self.tr('Z axis:')), 2, 0)
        params_layout.addWidget(self.zaxis_combo, 2, 1)
        params_layout.addWidget(QLabel(self.tr('Subsampling:')), 0, 2)
        params_layout.addWidget(self.sampling_spin, 0, 3)
        params_layout.addWidget(QLabel(self.tr('Point size:')), 1, 2)
        params_layout.addWidget(self.size_spin, 1, 3)
        # params_layout.addWidget(QLabel(self.tr('Point style:')), 2, 2)
        # params_layout.addWidget(self.style_combo, 3, 4)
        params_layout.addWidget(QLabel(self.tr('Point alpha:')), 2, 2)
        params_layout.addWidget(self.alpha_spin, 2, 3)
        params_layout.addWidget(self.colors_check, 0, 4)
        params_layout.addWidget(self.grid_check, 1, 4)
        params_layout.addWidget(self.total_label, 2, 4)
        bottom_layout = QHBoxLayout()
        bottom_layout.addLayout(params_layout)
        bottom_layout.addStretch()

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tab_widget)
        main_layout.addLayout(bottom_layout)
        self.setLayout(main_layout)

    def redraw(self):
        start = time()
        v = self.sampling_spin.value()
        x = self.colors[v][:, self.xaxis_combo.currentIndex()]
        y = self.colors[v][:, self.yaxis_combo.currentIndex()]
        s = self.size_spin.value()**2
        c = None if not self.colors_check.isChecked() else self.colors[v][:, :3]

        if self.tab_widget.currentIndex() == 0:
            self.zaxis_combo.setEnabled(False)
            self.grid_check.setEnabled(True)
            self.alpha_spin.setEnabled(True)
            a = self.alpha_spin.value()
            xlim = self.axes2.get_xlim()
            ylim = self.axes2.get_ylim()
            self.axes2.clear()
            self.axes2.set_facecolor([0.5] * 3 if c is not None else [1.0] * 3)
            self.axes2.scatter(x, y, s, c, '.', alpha=a)
            self.axes2.set_xlabel(self.xaxis_combo.currentText())
            self.axes2.set_ylabel(self.yaxis_combo.currentText())
            self.axes2.grid(self.grid_check.isChecked(), which='both')
            self.axes2.set_xlim(xlim)
            self.axes2.set_ylim(ylim)
            self.axes2.figure.canvas.draw()
        else:
            self.zaxis_combo.setEnabled(True)
            self.grid_check.setEnabled(False)
            self.alpha_spin.setEnabled(False)
            z = self.colors[v][:, self.zaxis_combo.currentIndex()]
            self.axes3.clear()
            self.axes3.set_facecolor([0.5] * 3 if c is not None else [1.0] * 3)
            self.axes3.scatter(x, y, z, s=s, c=c, marker='.', depthshade=True)
            self.axes3.set_xlabel(self.xaxis_combo.currentText())
            self.axes3.set_ylabel(self.yaxis_combo.currentText())
            self.axes3.set_zlabel(self.zaxis_combo.currentText())
            self.axes3.grid(self.grid_check.isChecked(), which='both')
            self.axes3.figure.canvas.draw()

        self.total_label.setText(self.tr('[{} points]'.format(len(x))))
        self.info_message.emit('Plot redraw = {}'.format(elapsed_time(start)))
