import os
import sys

from PySide2.QtCore import Qt, QSettings
from PySide2.QtGui import QKeySequence, QIcon
from PySide2.QtWidgets import (
    QApplication,
    QMainWindow,
    QMdiArea,
    QMdiSubWindow,
    QDockWidget,
    QAction,
    QMessageBox)

from .adjust import AdjustWidget
from .cloning import CloningWidget
from .comparison import ComparisonWidget
from .contrast import ContrastWidget
from .digest import DigestWidget
from .echo import EchoWidget
from .editor import EditorWidget
from .ela import ElaWidget
from .exif import ExifWidget
from .frequency import FrequencyWidget
from .gradient import GradientWidget
from .header import HeaderWidget
from .histogram import HistWidget
from .location import LocationWidget
from .magnifier import MagnifierWidget
# from median import MedianWidget
from .minmax import MinMaxWidget
from .multiple import MultipleWidget
from .noise import NoiseWidget
from .original import OriginalWidget
from .pca import PcaWidget
from .planes import PlanesWidget
from .plots import PlotsWidget
from .quality import QualityWidget
from .reverse import ReverseWidget
from .space import SpaceWidget
from .splicing import SplicingWidget
from .stats import StatsWidget
from .stereogram import StereoWidget
from .thumbnail import ThumbWidget
from .tools import ToolTree
from .utility import modify_font, load_image
from .wavelets import WaveletWidget

class MainWindow(QMainWindow):
    max_recent = 5

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        QApplication.setApplicationName('Sherloq')
        QApplication.setOrganizationName('Guido Bartoli')
        QApplication.setOrganizationDomain('www.guidobartoli.com')
        QApplication.setApplicationVersion(ToolTree().version)
        QApplication.setWindowIcon(QIcon('gui/icons/sherloq_white.png'))
        self.setWindowTitle('{} {}'.format(QApplication.applicationName(), QApplication.applicationVersion()))
        self.mdi_area = QMdiArea()
        self.setCentralWidget(self.mdi_area)
        self.filename = None
        self.image = None
        modify_font(self.statusBar(), bold=True)

        tree_dock = QDockWidget(self.tr('TOOLS'), self)
        tree_dock.setObjectName('tree_dock')
        tree_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.LeftDockWidgetArea, tree_dock)
        self.tree_widget = ToolTree()
        self.tree_widget.setObjectName('tree_widget')
        self.tree_widget.itemDoubleClicked.connect(self.open_tool)
        tree_dock.setWidget(self.tree_widget)

        tools_action = tree_dock.toggleViewAction()
        tools_action.setText(self.tr('Show tools'))
        tools_action.setToolTip(self.tr('Toggle toolset visibility'))
        tools_action.setShortcut(QKeySequence(Qt.Key_Tab))
        tools_action.setObjectName('tools_action')
        tools_action.setIcon(QIcon('gui/icons/tools.svg'))

        help_action = QAction(self.tr('Show help'), self)
        help_action.setToolTip(self.tr('Toggle online help'))
        help_action.setShortcut(QKeySequence.HelpContents)
        help_action.setObjectName('help_action')
        help_action.setIcon(QIcon('gui/icons/help.svg'))
        help_action.setCheckable(True)
        help_action.setEnabled(False)

        load_action = QAction(self.tr('&Load image...'), self)
        load_action.setToolTip(self.tr('Load an image to analyze'))
        load_action.setShortcut(QKeySequence.Open)
        load_action.triggered.connect(self.load_file)
        load_action.setObjectName('load_action')
        load_action.setIcon(QIcon('gui/icons/load.svg'))

        quit_action = QAction(self.tr('&Quit'), self)
        quit_action.setToolTip(self.tr('Exit from Sherloq'))
        quit_action.setShortcut(QKeySequence.Quit)
        quit_action.triggered.connect(self.close)
        quit_action.setObjectName('quit_action')
        quit_action.setIcon(QIcon('gui/icons/quit.svg'))

        tabbed_action = QAction(self.tr('&Tabbed'), self)
        tabbed_action.setToolTip(self.tr('Toggle tabbed view for window area'))
        tabbed_action.setShortcut(QKeySequence(Qt.Key_F10))
        tabbed_action.setCheckable(True)
        tabbed_action.triggered.connect(self.toggle_view)
        tabbed_action.setObjectName('tabbed_action')
        tabbed_action.setIcon(QIcon('gui/icons/tabbed.svg'))

        prev_action = QAction(self.tr('&Previous'), self)
        prev_action.setToolTip(self.tr('Select the previous tool window'))
        prev_action.setShortcut(QKeySequence.PreviousChild)
        prev_action.triggered.connect(self.mdi_area.activatePreviousSubWindow)
        prev_action.setObjectName('prev_action')
        prev_action.setIcon(QIcon('gui/icons/previous.svg'))

        next_action = QAction(self.tr('&Next'), self)
        next_action.setToolTip(self.tr('Select the next tool window'))
        next_action.setShortcut(QKeySequence.NextChild)
        next_action.triggered.connect(self.mdi_area.activateNextSubWindow)
        next_action.setObjectName('next_action')
        next_action.setIcon(QIcon('gui/icons/next.svg'))

        tile_action = QAction(self.tr('&Tile'), self)
        tile_action.setToolTip(self.tr('Arrange windows into non-overlapping views'))
        tile_action.setShortcut(QKeySequence(Qt.Key_F11))
        tile_action.triggered.connect(self.mdi_area.tileSubWindows)
        tile_action.setObjectName('tile_action')
        tile_action.setIcon(QIcon('gui/icons/tile.svg'))

        cascade_action = QAction(self.tr('&Cascade'), self)
        cascade_action.setToolTip(self.tr('Arrange windows into overlapping views'))
        cascade_action.setShortcut(QKeySequence(Qt.Key_F12))
        cascade_action.triggered.connect(self.mdi_area.cascadeSubWindows)
        cascade_action.setObjectName('cascade_action')
        cascade_action.setIcon(QIcon('gui/icons/cascade.svg'))

        close_action = QAction(self.tr('Close &All'), self)
        close_action.setToolTip(self.tr('Close all open tool windows'))
        close_action.setShortcut(QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_W))
        close_action.triggered.connect(self.mdi_area.closeAllSubWindows)
        close_action.setObjectName('close_action')
        close_action.setIcon(QIcon('gui/icons/close.svg'))

        self.full_action = QAction(self.tr('Full screen'), self)
        self.full_action.setToolTip(self.tr('Switch to full screen mode'))
        self.full_action.setShortcut(QKeySequence.FullScreen)
        self.full_action.triggered.connect(self.change_view)
        self.full_action.setObjectName('full_action')
        self.full_action.setIcon(QIcon('gui/icons/full.svg'))

        self.normal_action = QAction(self.tr('Normal view'), self)
        self.normal_action.setToolTip(self.tr('Back to normal view mode'))
        self.normal_action.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_F12))
        self.normal_action.triggered.connect(self.change_view)
        self.normal_action.setObjectName('normal_action')
        self.normal_action.setIcon(QIcon('gui/icons/normal.svg'))

        about_action = QAction(self.tr('&About...'), self)
        about_action.setToolTip(self.tr('Information about this program'))
        about_action.triggered.connect(self.show_about)
        about_action.setObjectName('about_action')
        about_action.setIcon(QIcon('gui/icons/sherloq_alpha.png'))

        about_qt_action = QAction(self.tr('About &Qt'), self)
        about_qt_action.setToolTip(self.tr('Information about the Qt Framework'))
        about_qt_action.triggered.connect(QApplication.aboutQt)
        about_qt_action.setIcon(QIcon('gui/icons/Qt.svg'))

        file_menu = self.menuBar().addMenu(self.tr('&File'))
        file_menu.addAction(load_action)
        file_menu.addSeparator()
        self.recent_actions = [None]*self.max_recent
        for i in range(len(self.recent_actions)):
            self.recent_actions[i] = QAction(self)
            self.recent_actions[i].setVisible(False)
            self.recent_actions[i].triggered.connect(self.open_recent)
            file_menu.addAction(self.recent_actions[i])
        file_menu.addSeparator()
        file_menu.addAction(quit_action)

        view_menu = self.menuBar().addMenu(self.tr('&View'))
        view_menu.addAction(tools_action)
        view_menu.addAction(help_action)
        view_menu.addSeparator()
        view_menu.addAction(self.full_action)
        view_menu.addAction(self.normal_action)

        window_menu = self.menuBar().addMenu(self.tr('&Window'))
        window_menu.addAction(prev_action)
        window_menu.addAction(next_action)
        window_menu.addSeparator()
        window_menu.addAction(tile_action)
        window_menu.addAction(cascade_action)
        window_menu.addAction(tabbed_action)
        window_menu.addSeparator()
        window_menu.addAction(close_action)

        help_menu = self.menuBar().addMenu(self.tr('&Help'))
        help_menu.addAction(help_action)
        help_menu.addSeparator()
        help_menu.addAction(about_action)
        help_menu.addAction(about_qt_action)

        main_toolbar = self.addToolBar(self.tr('&Toolbar'))
        main_toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        main_toolbar.addAction(load_action)
        main_toolbar.addSeparator()
        main_toolbar.addAction(tools_action)
        main_toolbar.addAction(help_action)
        main_toolbar.addSeparator()
        main_toolbar.addAction(prev_action)
        main_toolbar.addAction(next_action)
        main_toolbar.addSeparator()
        main_toolbar.addAction(tile_action)
        main_toolbar.addAction(cascade_action)
        main_toolbar.addAction(tabbed_action)
        main_toolbar.addAction(close_action)
        # main_toolbar.addSeparator()
        # main_toolbar.addAction(self.normal_action)
        # main_toolbar.addAction(self.full_action)
        main_toolbar.setAllowedAreas(Qt.TopToolBarArea | Qt.BottomToolBarArea)
        main_toolbar.setObjectName('main_toolbar')

        settings = QSettings()
        settings.beginGroup('main_window')
        self.restoreGeometry(settings.value('geometry'))
        self.restoreState(settings.value('state'))
        self.recent_files = settings.value('recent_files')
        if self.recent_files is None:
            self.recent_files = []
        elif not isinstance(self.recent_files, list):
            self.recent_files = [self.recent_files]
        self.update_recent()
        settings.endGroup()

        prev_action.setEnabled(False)
        next_action.setEnabled(False)
        tile_action.setEnabled(False)
        cascade_action.setEnabled(False)
        close_action.setEnabled(False)
        tabbed_action.setEnabled(False)
        self.tree_widget.setEnabled(False)
        self.showNormal()
        self.normal_action.setEnabled(False)
        self.show_message(self.tr('Ready'))

    def change_view(self):
        if self.isFullScreen():
            self.showNormal()
            self.showMaximized()
            self.full_action.setEnabled(True)
            self.normal_action.setEnabled(False)
        else:
            self.showFullScreen()
            self.full_action.setEnabled(False)
            self.normal_action.setEnabled(True)

    def closeEvent(self, event):
        settings = QSettings()
        settings.beginGroup('main_window')
        settings.setValue('geometry', self.saveGeometry())
        settings.setValue('state', self.saveState())
        settings.setValue('recent_files', self.recent_files)
        settings.endGroup()
        super(MainWindow, self).closeEvent(event)

    def update_recent(self):
        if not self.recent_files:
            return
        self.recent_files = [f for f in self.recent_files if os.path.isfile(f)]
        for i in range(len(self.recent_actions)):
            if i < len(self.recent_files):
                text = '&{} {}'.format(i + 1, os.path.basename(self.recent_files[i]))
                self.recent_actions[i].setText(text)
                self.recent_actions[i].setData(self.recent_files[i])
                self.recent_actions[i].setVisible(True)
            else:
                self.recent_actions[i].setVisible(False)

    def open_recent(self):
        action = self.sender()
        if action:
            filename, basename, image = load_image(self, action.data())
            self.initialize(filename, basename, image)

    def initialize(self, filename, basename, image):
        self.filename = filename
        self.image = image
        self.findChild(ToolTree, 'tree_widget').setEnabled(True)
        self.findChild(QAction, 'prev_action').setEnabled(True)
        self.findChild(QAction, 'next_action').setEnabled(True)
        self.findChild(QAction, 'tile_action').setEnabled(True)
        self.findChild(QAction, 'cascade_action').setEnabled(True)
        self.findChild(QAction, 'close_action').setEnabled(True)
        self.findChild(QAction, 'tabbed_action').setEnabled(True)
        self.setWindowTitle('[{}] - {} {}'.format(
            basename, QApplication.applicationName(), QApplication.applicationVersion()))
        if filename not in self.recent_files:
            self.recent_files.insert(0, filename)
            if len(self.recent_files) > self.max_recent:
                self.recent_files = self.recent_files[:self.max_recent]
            self.update_recent()
        self.show_message(self.tr('Image "{}" successfully loaded'.format(basename)))

        # FIXME: disable_bold della chiusura viene chiamato DOPO open_tool e nell'albero la voce NON diventa neretto
        self.mdi_area.closeAllSubWindows()
        self.open_tool(self.tree_widget.topLevelItem(0).child(0), None)

    def load_file(self):
        filename, basename, image = load_image(self)
        if filename is None:
            return
        self.initialize(filename, basename, image)

    def open_tool(self, item, _):
        if not item.data(0, Qt.UserRole):
            return
        group = item.data(0, Qt.UserRole + 1)
        tool = item.data(0, Qt.UserRole + 2)
        for sub_window in self.mdi_area.subWindowList():
            if sub_window.windowTitle() == item.text(0):
                sub_window.setWindowState(Qt.WindowActive)
                sub_window.setFocus()
                return

        if group == 0:
            if tool == 0:
                tool_widget = OriginalWidget(self.image)
            elif tool == 1:
                tool_widget = DigestWidget(self.filename, self.image)
            elif tool == 2:
                tool_widget = EditorWidget()
            elif tool == 3:
                tool_widget = ReverseWidget()
            else:
                return
        elif group == 1:
            if tool == 0:
                tool_widget = HeaderWidget(self.filename)
            elif tool == 1:
                tool_widget = ExifWidget(self.filename)
            elif tool == 2:
                tool_widget = ThumbWidget(self.filename, self.image)
            elif tool == 3:
                tool_widget = LocationWidget(self.filename)
            else:
                return
        elif group == 2:
            if tool == 0:
                tool_widget = MagnifierWidget(self.image)
            elif tool == 1:
                tool_widget = HistWidget(self.image)
            elif tool == 2:
                tool_widget = AdjustWidget(self.image)
            elif tool == 3:
                tool_widget = ComparisonWidget(self.filename, self.image)
            else:
                return
        elif group == 3:
            if tool == 0:
                tool_widget = GradientWidget(self.image)
            elif tool == 1:
                tool_widget = EchoWidget(self.image)
            elif tool == 2:
                tool_widget = WaveletWidget(self.image)
            else:
                return
        elif group == 4:
            if tool == 0:
                tool_widget = PlotsWidget(self.image)
            elif tool == 1:
                tool_widget = SpaceWidget(self.image)
            elif tool == 2:
                tool_widget = PcaWidget(self.image)
            elif tool == 3:
                tool_widget = StatsWidget(self.image)
            else:
                return
        elif group == 5:
            if tool == 0:
                tool_widget = NoiseWidget(self.image)
            elif tool == 1:
                tool_widget = MinMaxWidget(self.image)
            elif tool == 2:
                tool_widget = FrequencyWidget(self.image)
            elif tool == 3:
                tool_widget = PlanesWidget(self.image)
            else:
                return
        elif group == 6:
            if tool == 0:
                tool_widget = ElaWidget(self.image)
            elif tool == 1:
                tool_widget = QualityWidget(self.filename)
            elif tool == 2:
                tool_widget = MultipleWidget(self.image)
            else:
                return
        elif group == 7:
            if tool == 0:
                tool_widget = ContrastWidget(self.image)
            elif tool == 1:
                tool_widget = CloningWidget(self.image)
            elif tool == 2:
                tool_widget = SplicingWidget(self.image)
            else:
                return
        elif group == 8:
            # if tool == 0:
            #     tool_widget = MedianWidget(self.image)
            if tool == 3:
                tool_widget = StereoWidget(self.image)
            else:
                return
        else:
            return

        # FIXME: Aggiungere un metodo init e dopo fare il connect, senn\`o i messaggi inviati nel costruttore non arrivano
        tool_widget.info_message.connect(self.show_message)

        sub_window = QMdiSubWindow()
        sub_window.setWidget(tool_widget)
        sub_window.setWindowTitle(item.text(0))
        sub_window.setObjectName(item.text(0))
        sub_window.setAttribute(Qt.WA_DeleteOnClose)
        sub_window.setWindowIcon(QIcon('gui/icons/{}.svg'.format(group)))
        self.mdi_area.addSubWindow(sub_window)
        sub_window.show()
        sub_window.destroyed.connect(self.disable_bold)
        self.tree_widget.set_bold(item.text(0), enabled=True)

    def disable_bold(self, item):
        self.tree_widget.set_bold(item.windowTitle(), enabled=False)

    def toggle_view(self, tabbed):
        if tabbed:
            self.mdi_area.setViewMode(QMdiArea.TabbedView)
            self.mdi_area.setTabsClosable(True)
            self.mdi_area.setTabsMovable(True)
        else:
            self.mdi_area.setViewMode(QMdiArea.SubWindowView)
        self.findChild(QAction, 'tile_action').setEnabled(not tabbed)
        self.findChild(QAction, 'cascade_action').setEnabled(not tabbed)

    def show_about(self):
        message = '<h2>{} {}</h2>'.format(QApplication.applicationName(), QApplication.applicationVersion())
        message += '<h3>A digital image forensic toolkit</h3>'
        message += '<p>author: <a href="{}">{}</a></p>'.format(
            QApplication.organizationDomain(), QApplication.organizationName())
        message += '<p>source: <a href="https://github.com/GuidoBartoli/sherloq">GitHub repository</a></p>'
        QMessageBox.about(self, self.tr('About'), message)

    def show_message(self, message):
        self.statusBar().showMessage(message, 10000)


def main():
    application = QApplication(sys.argv)
    mainwindow = MainWindow()
    sys.exit(application.exec_())
    mainwindow.show()

if __name__ == '__main__':
    main()
