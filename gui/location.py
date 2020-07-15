import os

from PySide2.QtCore import QUrl, QTemporaryDir, Qt
from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtWidgets import QVBoxLayout, QLabel

from .pyexiftool import exiftool
from .tools import ToolWidget
from .utility import exiftool_exe, modify_font


class LocationWidget(ToolWidget):
    def __init__(self, filename, parent=None):
        super(LocationWidget, self).__init__(parent)
        self.temp_dir = QTemporaryDir()
        if self.temp_dir.isValid():
            with exiftool.ExifTool(exiftool_exe()) as et:
                temp_file = os.path.join(self.temp_dir.path(), 'geo.html')
                metadata = et.get_metadata(filename)
                try:
                    lat = metadata['Composite:GPSLatitude']
                    long = metadata['Composite:GPSLongitude']
                except KeyError:
                    label = QLabel(self.tr('Geolocation data not found!'))
                    modify_font(label, bold=True)
                    label.setStyleSheet('color: #FF0000')
                    label.setAlignment(Qt.AlignCenter)
                    layout = QVBoxLayout()
                    layout.addWidget(label)
                    self.setLayout(layout)
                    return
                html = '<iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d2948.532014673314!2d{}!3d{}!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x0%3A0x0!2zNDLCsDIxJzA5LjAiTiA3McKwMDUnMjguMiJX!5e0!3m2!1sit!2sit!4v1590074026898!5m2!1sit!2sit" width="600" height="450" frameborder="0" style="border:0;" allowfullscreen="" aria-hidden="false" tabindex="0"></iframe>'.format(long, lat)
                with open(temp_file, 'w') as file:
                    file.write(html)
                web_view = QWebEngineView()
                web_view.load(QUrl('file://' + temp_file))
                layout = QVBoxLayout()
                layout.addWidget(web_view)
                self.setLayout(layout)
