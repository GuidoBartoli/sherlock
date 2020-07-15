import cv2 as cv
from PySide2.QtCharts import QtCharts
from PySide2.QtCore import Qt
from PySide2.QtGui import QPainter
from PySide2.QtWidgets import (
    QVBoxLayout,
    QProgressDialog)

from .jpeg import compress_img
from .tools import ToolWidget


class MultipleWidget(ToolWidget):
    def __init__(self, image, parent=None):
        super(ToolWidget, self).__init__(parent)

        max_q = 101
        progress = QProgressDialog(self.tr('Computing residuals...'), None, 0, max_q, self)
        progress.setWindowModality(Qt.WindowModal)
        loss_series = QtCharts.QLineSeries()
        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        for q in range(max_q):
            loss = cv.mean(cv.absdiff(compress_img(gray, q, color=False), gray))
            loss_series.append(q, loss[0])
            progress.setValue(q)
        progress.setValue(max_q)

        loss_chart = QtCharts.QChart()
        loss_chart.legend().hide()
        loss_chart.setTitle(self.tr('Loss vs Compression'))
        loss_chart.addSeries(loss_series)
        loss_chart.createDefaultAxes()
        loss_chart.axisX().setRange(0, 100)
        loss_chart.axisX().setTitleText(self.tr('quality (%)'))
        loss_chart.axisX().setTickCount(11)
        loss_chart.axisX().setLabelFormat('%d')
        loss_chart.axisY().setTitleText(self.tr('loss (%)'))
        loss_chart.setMinimumSize(600, 400)
        font = loss_chart.titleFont()
        font.setBold(True)
        loss_chart.setTitleFont(font)
        loss_view = QtCharts.QChartView(loss_chart)
        loss_view.setRenderHint(QPainter.Antialiasing)

        main_layout = QVBoxLayout()
        main_layout.addWidget(loss_view)
        self.setLayout(main_layout)
