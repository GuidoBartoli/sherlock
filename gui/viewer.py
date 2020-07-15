import math

import cv2 as cv
import numpy as np
from PySide2.QtCore import (
    QSettings,
    Qt,
    Signal,
    QRect,
    QRectF)
from PySide2.QtGui import (
    QIcon,
    QPainter,
    QMatrix,
    QPixmap,
    QImage)
from PySide2.QtWidgets import (
    QLabel,
    QRadioButton,
    QToolButton,
    QFileDialog,
    QWidget,
    QGraphicsScene,
    QGraphicsView,
    QVBoxLayout,
    QHBoxLayout)

from .utility import mat2img, modify_font


class DynamicView(QGraphicsView):
    viewChanged = Signal(QRect, float, int, int)

    def __init__(self, image, parent=None):
        super(DynamicView, self).__init__(parent)
        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(Qt.darkGray)
        self.setScene(self.scene)
        self.set_image(image)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.ZOOM_STEP = 0.2
        self.mouse_pressed = False
        self.next_fit = False
        self.fit_scale = 0
        self.zoom_fit()

    def set_image(self, image):
        if type(image) is QPixmap:
            pixmap = image
        elif type(image) is QImage:
            pixmap = QPixmap.fromImage(image)
        elif type(image) is np.ndarray:
            pixmap = QPixmap.fromImage(mat2img(image))
        else:
            raise TypeError(self.tr('DynamicView.set_image: Unsupported type: {}'.format(type(image))))
        if not self.scene.items():
            self.scene.addPixmap(pixmap)
        else:
            self.scene.items()[0].setPixmap(pixmap)
        self.scene.setSceneRect(QRectF(pixmap.rect()))

    def zoom_full(self):
        self.set_scaling(1)
        self.next_fit = True
        self.notify_change()

    def zoom_fit(self):
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        self.fit_scale = self.matrix().m11()
        if self.fit_scale > 1:
            self.fit_scale = 1
            self.zoom_full()
        else:
            self.next_fit = False
            self.notify_change()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mouse_pressed = True
        QGraphicsView.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        QGraphicsView.mouseMoveEvent(self, event)
        if self.mouse_pressed:
            self.notify_change()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mouse_pressed = False
        QGraphicsView.mouseReleaseEvent(self, event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.next_fit:
                self.zoom_fit()
            else:
                self.zoom_full()
        QGraphicsView.mouseDoubleClickEvent(self, event)

    def wheelEvent(self, event):
        if event.delta() > 0:
            self.change_zoom(+1)
        else:
            self.change_zoom(-1)

    def resizeEvent(self, event):
        # FIXME: Se la finestra viene massimizzata, il valore di fit_scale non si aggiorna
        if self.matrix().m11() <= self.fit_scale:
            self.zoom_fit()
        else:
            self.notify_change()
        QGraphicsView.resizeEvent(self, event)

    def change_zoom(self, direction):
        level = math.log2(self.matrix().m11())
        if direction > 0:
            level += self.ZOOM_STEP
        else:
            level -= self.ZOOM_STEP
        scaling = 2 ** level
        if scaling < self.fit_scale:
            scaling = self.fit_scale
            self.next_fit = False
        elif scaling > 1:
            # scaling = 1
            if scaling > 4:
                scaling = 4
            self.next_fit = True
        self.set_scaling(scaling)
        self.notify_change()

    def set_scaling(self, scaling):
        matrix = QMatrix()
        matrix.scale(scaling, scaling)
        self.setMatrix(matrix)

    def change_view(self, _, new_scaling, new_horiz, new_vert):
        old_factor = self.matrix().m11()
        old_horiz = self.horizontalScrollBar().value()
        old_vert = self.verticalScrollBar().value()
        if new_scaling != old_factor or new_horiz != old_horiz or new_vert != old_vert:
            self.set_scaling(new_scaling)
            self.horizontalScrollBar().setValue(new_horiz)
            self.verticalScrollBar().setValue(new_vert)
            self.notify_change()

    def notify_change(self):
        scene_rect = self.get_rect()
        horiz_scroll = self.horizontalScrollBar().value()
        vert_scroll = self.verticalScrollBar().value()
        zoom_factor = self.matrix().m11()
        self.viewChanged.emit(scene_rect, zoom_factor, horiz_scroll, vert_scroll)

    def get_rect(self):
        top_left = self.mapToScene(0, 0).toPoint()
        if top_left.x() < 0:
            top_left.setX(0)
        if top_left.y() < 0:
            top_left.setY(0)
        view_size = self.viewport().size()
        bottom_right = self.mapToScene(view_size.width(), view_size.height()).toPoint()
        image_size = self.sceneRect().toRect()
        if bottom_right.x() >= image_size.width():
            bottom_right.setX(image_size.width() - 1)
        if bottom_right.y() >= image_size.height():
            bottom_right.setY(image_size.height() - 1)
        return QRect(top_left, bottom_right)


class ImageViewer(QWidget):
    viewChanged = Signal(QRect, float, int, int)

    def __init__(self, original, processed, title=None, parent=None, export=False):
        super(ImageViewer, self).__init__(parent)
        if original is None and processed is None:
            raise ValueError(self.tr('ImageViewer.__init__: Empty image received'))
        if original is None and processed is not None:
            original = processed
        self.original = original
        self.processed = processed
        if self.original is not None and self.processed is None:
            self.view = DynamicView(self.original)
        else:
            self.view = DynamicView(self.processed)

        # view_label = QLabel(self.tr('View:'))
        self.original_radio = QRadioButton(self.tr('Original'))
        self.original_radio.setToolTip(self.tr('Show the original image for comparison'))
        self.process_radio = QRadioButton(self.tr('Processed'))
        self.process_radio.setToolTip(self.tr('Show result of the current processing'))
        self.zoom_label = QLabel()
        full_button = QToolButton()
        full_button.setText(self.tr('100%'))
        fit_button = QToolButton()
        fit_button.setText(self.tr('Fit'))
        height, width, _ = self.original.shape
        size_label = QLabel(self.tr('[{}x{} px]'.format(height, width)))
        export_button = QToolButton()
        export_button.setToolTip(self.tr('Export current image to PNG'))
        # export_button.setText(self.tr('Export...'))
        export_button.setIcon(QIcon('gui/icons/export.svg'))

        tool_layout = QHBoxLayout()
        tool_layout.addWidget(QLabel(self.tr('Zoom:')))
        tool_layout.addWidget(self.zoom_label)
        # tool_layout.addWidget(full_button)
        # tool_layout.addWidget(fit_button)
        tool_layout.addStretch()
        if processed is not None:
            # tool_layout.addWidget(view_label)
            tool_layout.addWidget(self.original_radio)
            tool_layout.addWidget(self.process_radio)
            tool_layout.addStretch()
        tool_layout.addWidget(size_label)
        if export or processed is not None:
            tool_layout.addWidget(export_button)
        if processed is not None:
            self.original_radio.setChecked(False)
            self.process_radio.setChecked(True)
            self.toggle_mode(False)

        vert_layout = QVBoxLayout()
        if title is not None:
            self.title_label = QLabel(title)
            modify_font(self.title_label, bold=True)
            self.title_label.setAlignment(Qt.AlignCenter)
            vert_layout.addWidget(self.title_label)
        else:
            self.title_label = None
        vert_layout.addWidget(self.view)
        vert_layout.addLayout(tool_layout)
        self.setLayout(vert_layout)

        self.original_radio.toggled.connect(self.toggle_mode)
        fit_button.clicked.connect(self.view.zoom_fit)
        full_button.clicked.connect(self.view.zoom_full)
        export_button.clicked.connect(self.export_image)
        self.view.viewChanged.connect(self.forward_changed)

        # view_label.setVisible(processed is not None)
        # self.original_radio.setVisible(processed is not None)
        # self.process_radio.setVisible(processed is not None)
        # export_button.setVisible(processed is not None)
        # if processed is not None:
        #
        # self.adjustSize()

    def update_processed(self, image):
        if self.processed is None:
            return
        self.processed = image
        self.toggle_mode(self.original_radio.isChecked())

    def update_original(self, image):
        self.original = image
        self.toggle_mode(True)

    def changeView(self, rect, scaling, horizontal, vertical):
        self.view.change_view(rect, scaling, horizontal, vertical)

    def forward_changed(self, rect, scaling, horizontal, vertical):
        self.zoom_label.setText('{:.2f}%'.format(scaling*100))
        modify_font(self.zoom_label, scaling == 1)
        self.viewChanged.emit(rect, scaling, horizontal, vertical)

    def get_rect(self):
        return self.view.get_rect()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            if self.original_radio.isChecked():
                self.process_radio.setChecked(True)
            else:
                self.original_radio.setChecked(True)
        QWidget.keyPressEvent(self, event)

    def toggle_mode(self, toggled):
        if toggled:
            self.view.set_image(self.original)
        elif self.processed is not None:
            self.view.set_image(self.processed)

    def export_image(self):
        settings = QSettings()
        filename = QFileDialog.getSaveFileName(self, self.tr('Export image...'), settings.value('save_folder'),
                                               self.tr('PNG images (*.png)'))[0]
        if not filename:
            return
        if not filename.endswith('.png'):
            filename += '.png'
        cv.imwrite(filename, self.processed if self.processed is not None else self.original)

    def set_title(self, title):
        if self.title_label is not None:
            self.title_label.setText(title)
