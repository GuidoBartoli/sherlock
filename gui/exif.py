from PySide2.QtWidgets import QVBoxLayout

from .pyexiftool import exiftool
from .table import TableWidget
from .tools import ToolWidget
from .utility import exiftool_exe


class ExifWidget(ToolWidget):
    def __init__(self, filename, parent=None):
        super(ExifWidget, self).__init__(parent)
        table = []
        last = None
        with exiftool.ExifTool(exiftool_exe()) as et:
            metadata = et.get_metadata(filename)
            for tag, value in metadata.items():
                ignore = ['SourceFile', 'ExifTool:ExifTool', 'File:FileName', 'File:Directory',
                          'File:FileSize', 'File:FileModifyDate', 'File:FileInodeChangeDate',
                          'File:FileAccessDate', 'File:FileType', 'File:FilePermissions',
                          'File:FileTypeExtension', 'File:MIMEType']
                if not value or any(t in tag for t in ignore):
                    continue
                value = str(value).replace(', use -b option to extract', '')
                value = value.replace('Binary data ', 'Binary data: ')
                group, desc = tag.split(':')
                if last is None or group != last:
                    table.append([group, desc, value])
                    last = group
                else:
                    table.append([None, desc, value])
        headers = [self.tr('Group'), self.tr('Description'), self.tr('Value')]
        table_widget = TableWidget(table, headers)
        main_layout = QVBoxLayout()
        main_layout.addWidget(table_widget)
        self.setLayout(main_layout)
        self.setMinimumSize(740, 500)
