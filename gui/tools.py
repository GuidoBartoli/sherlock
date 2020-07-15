from PySide2.QtCore import Qt, Signal
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import (
    QTreeWidget,
    QTreeWidgetItem,
    QWidget)

from .utility import modify_font


class ToolWidget(QWidget):
    info_message = Signal(str)

    def __init__(self, parent=None):
        super(ToolWidget, self).__init__(parent)


class ToolTree(QTreeWidget):
    def __init__(self, parent=None):
        super(ToolTree, self).__init__(parent)
        group_names = []
        tool_names = []
        tool_infos = []
        tool_progress = []  # 0 = da fare, 1 = debug, 2 = funzionante, 3 = completo

        # [0]
        group_names.append(self.tr('[General]'))
        tool_names.append([self.tr('Original Image'),
                           self.tr('File Digest'),
                           self.tr('Hex Editor'),
                           self.tr('Similar Search')])
        tool_infos.append([self.tr('Display the unaltered reference image for visual inspection'),
                           self.tr('Retrieve physical file information, crypto and perceptual hashes'),
                           self.tr('Open an external hexadecimal editor to show and edit raw bytes'),
                           self.tr('Browse online search services to find visually similar images')])
        tool_progress.extend([3, 3, 2, 2])

        # [1]
        group_names.append(self.tr('[Metadata]'))
        tool_names.append([self.tr('Header Structure'),
                           self.tr('EXIF Full Dump'),
                           self.tr('Thumbnail Analysis'),
                           self.tr('Geolocation data')])
        tool_infos.append([self.tr('Dump the file header structure and display an interactive view'),
                           self.tr('Scan through file metadata and gather all available information'),
                           self.tr('Extract optional embedded thumbnail and compare with original'),
                           self.tr('Retrieve optional geolocation data and show it on a world map')])
        tool_progress.extend([3, 3, 3, 2])

        # [2]
        group_names.append(self.tr('[Inspection]'))
        tool_names.append([self.tr('Enhancing Magnifier'),
                           self.tr('Channel Histogram'),
                           self.tr('Global Adjustments'),
                           self.tr('Reference Comparison')])
        tool_infos.append([self.tr('Magnifying glass with enhancements for better identifying forgeries'),
                           self.tr('Display single color channels or RGB composite interactive histogram'),
                           self.tr('Apply standard image adjustments (brightness, hue, saturation, ...)'),
                           self.tr('Open a synchronized double view for comparison with another picture')])
        tool_progress.extend([3, 3, 3, 3])

        # [3]
        group_names.append(self.tr('[Detail]'))
        tool_names.append([self.tr('Luminance Gradient'),
                           self.tr('Echo Edge Filter'),
                           self.tr('Wavelet Threshold'),
                           self.tr('Correlation Plot')])
        tool_infos.append([self.tr('Analyze horizontal/vertical brightness variations across the image'),
                           self.tr('Use derivative filters to reveal artificial out-of-focus regions'),
                           self.tr('Reconstruct image with different wavelet coefficient thresholds'),
                           self.tr('Exploit spatial correlation patterns among neighboring pixels')])
        tool_progress.extend([3, 3, 3, 0])

        # [4]
        group_names.append(self.tr('[Colors]'))
        tool_names.append([self.tr('RGB/HSV Plots'),
                           self.tr('Space Conversion'),
                           self.tr('PCA Projection'),
                           self.tr('Pixel Statistics')])
        tool_infos.append([self.tr('Display interactive 2D and 3D plots of RGB and HSV pixel values'),
                           self.tr('Convert RGB channels into HSV/YCbCr/Lab/Luv/CMYK/Gray spaces'),
                           self.tr('Use color PCA to project pixel onto most salient components'),
                           self.tr('Compute minimum/maximum/average RGB values for every pixel')])
        tool_progress.extend([3, 3, 3, 3])

        # [5]
        group_names.append(self.tr('[Noise]'))
        tool_names.append([self.tr('Noise Separation'),
                           self.tr('Min/Max Deviation'),
                           self.tr('Frequency Split'),
                           self.tr('Bit Plane Values')])
        tool_infos.append([self.tr('Estimate and extract different kind of image noise components'),
                           self.tr('Highlight pixels deviating from block-based min/max statistics'),
                           self.tr('Split image luminance into high and low frequency components'),
                           self.tr('Show individual bit planes to find inconsistent noise patterns')])
        tool_progress.extend([3, 3, 3, 3])

        # [6]
        group_names.append(self.tr('[JPEG]'))
        tool_names.append([self.tr('Error Level Analysis'),
                           self.tr('Quality Estimation'),
                           self.tr('Multiple Compression'),
                           self.tr('DCT Dimples Map')])
        tool_infos.append([self.tr('Show pixel-level difference against fixed compression levels'),
                           self.tr('Extract quantization tables and estimate last saved JPEG quality'),
                           self.tr('Use residuals to detect multiple compressions at different levels'),
                           self.tr('Analyze periodic quantization artifacts introduced by devices')])
        tool_progress.extend([3, 3, 1, 0])

        # [7]
        group_names.append(self.tr('[Tampering]'))
        tool_names.append([self.tr('Contrast Enhancement'),
                           self.tr('Copy-Move Forgery'),
                           self.tr('Composite Splicing'),
                           self.tr('Image Resampling')])
        tool_infos.append([self.tr('Analyze color distributions to detect contrast enhancements'),
                           self.tr('Use invariant feature descriptors to detect cloned regions'),
                           self.tr('Exploit DCT statistics for automatic splicing zone detection'),
                           self.tr('Estimate 2D pixel interpolation for detecting resampling traces')])
        tool_progress.extend([3, 3, 3, 0])

        # [8]
        group_names.append(self.tr('[Various]'))
        tool_names.append([self.tr('Median Filtering'),
                           self.tr('Illuminant Map'),
                           self.tr('PRNU Identification'),
                           self.tr('Stereogram Decoder')])
        tool_infos.append([self.tr('Detect processing traces left by nonlinear median filtering'),
                           self.tr('Estimate scene local light direction on estimated 3D surfaces'),
                           self.tr('Exploit sensor pattern noise introduced by different cameras'),
                           self.tr('Decode 3D images concealed inside crossed-eye autostereograms')])
        tool_progress.extend([0, 0, 0, 3])

        count = 0
        for i, group in enumerate(group_names):
            group_item = QTreeWidgetItem()
            group_item.setText(0, group)
            font = group_item.font(0)
            font.setBold(True)
            group_item.setFont(0, font)
            group_item.setData(0, Qt.UserRole, False)
            group_item.setIcon(0, QIcon('gui/icons/{}.svg'.format(i)))
            for j, tool in enumerate(tool_names[i]):
                tool_item = QTreeWidgetItem(group_item)
                tool_item.setText(0, tool)
                tool_item.setData(0, Qt.UserRole, True)
                tool_item.setData(0, Qt.UserRole + 1, i)
                tool_item.setData(0, Qt.UserRole + 2, j)
                tool_item.setToolTip(0, tool_infos[i][j])
                if tool_progress[count] == 0:
                    modify_font(tool_item, italic=True)
                count += 1
            self.addTopLevelItem(group_item)
        self.expandAll()
        self.setColumnCount(1)
        self.header().setVisible(False)
        self.setMaximumWidth(300)
        self.version = '{:.2f}a'.format(sum(tool_progress) / 100)

    def set_bold(self, tool, enabled):
        items = self.findItems(tool, Qt.MatchFixedString | Qt.MatchRecursive)
        if items:
            modify_font(items[0], bold=enabled)


