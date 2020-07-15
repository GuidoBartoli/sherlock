import csv

from PySide2.QtCore import (
    Qt,
    QRect,
    QRegularExpression,
    QSettings,
    QFileInfo)
from PySide2.QtGui import (
    QIcon,
    QKeySequence,
    QCursor)
from PySide2.QtWidgets import (
    QToolTip,
    QApplication,
    QAbstractItemView,
    QVBoxLayout,
    QFileDialog,
    QTableWidgetItem,
    QTableWidget,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QToolButton,
    QWidget)

from .utility import modify_font


class TableWidget(QWidget):
    def __init__(self, table, headers, bold=True, mono=True, tooltips=None, align=False, search=True, parent=None):
        super(TableWidget, self).__init__(parent)

        self.table_widget = QTableWidget(len(table), len(table[0]))
        for i, row in enumerate(table):
            for j, item in enumerate(row):
                if item is not None:
                    self.table_widget.setItem(i, j, QTableWidgetItem(str(item)))
                    if tooltips is not None:
                        self.table_widget.setToolTip(tooltips[i][j])
                    modify_font(self.table_widget.item(i, j), bold=bold and j == 0, mono=mono)
                    if align:
                        self.table_widget.item(i, j).setTextAlignment(Qt.AlignRight)

        self.table_headers = headers
        self.table_widget.setHorizontalHeaderLabels(self.table_headers)
        self.table_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_widget.resizeColumnsToContents()
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.itemDoubleClicked.connect(self.copy)

        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel(self.tr('Search:')))
        self.search_edit = QLineEdit()
        self.search_edit.textChanged.connect(self.start)
        self.search_edit.returnPressed.connect(self.next)
        search_layout.addWidget(self.search_edit)

        clear_button = QToolButton()
        clear_button.setIcon(QIcon('gui/icons/clear.svg'))
        clear_button.setShortcut(QKeySequence.DeleteCompleteLine)
        clear_button.setToolTip(self.tr('Clear pattern'))
        clear_button.clicked.connect(self.search_edit.clear)
        search_layout.addWidget(clear_button)

        self.case_button = QToolButton()
        self.case_button.setText(self.tr('Aa'))
        self.case_button.setCheckable(True)
        self.case_button.toggled.connect(self.start)
        self.case_button.setToolTip(self.tr('Case sensitive'))
        search_layout.addWidget(self.case_button)

        self.word_button = QToolButton()
        self.word_button.setText(self.tr('W'))
        self.word_button.setCheckable(True)
        self.word_button.toggled.connect(self.start)
        self.word_button.setToolTip(self.tr('Whole words'))
        search_layout.addWidget(self.word_button)

        self.regex_button = QToolButton()
        self.regex_button.setText(self.tr('.*'))
        self.regex_button.setCheckable(True)
        self.regex_button.toggled.connect(self.start)
        self.regex_button.setToolTip(self.tr('Regular expression'))
        search_layout.addWidget(self.regex_button)

        prev_button = QToolButton()
        prev_button.setIcon(QIcon('gui/icons/up.svg'))
        prev_button.setShortcut(QKeySequence.FindPrevious)
        prev_button.clicked.connect(self.previous)
        prev_button.setToolTip(self.tr('Previous occurence'))
        search_layout.addWidget(prev_button)

        next_button = QToolButton()
        next_button.setIcon(QIcon('gui/icons/down.svg'))
        next_button.setShortcut(QKeySequence.FindNext)
        next_button.clicked.connect(self.next)
        next_button.setToolTip(self.tr('Next occurence'))
        search_layout.addWidget(next_button)

        self.matches_label = QLabel()
        search_layout.addWidget(self.matches_label)
        search_layout.addStretch()

        export_button = QToolButton()
        export_button.setText(self.tr('Export...'))
        export_button.setToolTip(self.tr('Save table content to CSV format'))
        export_button.clicked.connect(self.export)
        search_layout.addWidget(export_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.table_widget)
        if search:
            main_layout.addLayout(search_layout)
        self.setLayout(main_layout)

    def start(self):
        self.search(self.search_edit.text(), -1, -1, 1)

    def next(self):
        row = self.table_widget.currentRow()
        col = self.table_widget.currentColumn() + 1
        if col == self.table_widget.columnCount():
            row += 1
            col = 0
        self.search(self.search_edit.text(), row, col, +1)

    def previous(self):
        row = self.table_widget.currentRow()
        col = self.table_widget.currentColumn() - 1
        if col == -1:
            row -= 1
            col = self.table_widget.columnCount() - 1
        self.search(self.search_edit.text(), row, col, -1)

    def search(self, pattern, row, col, direction):
        nocase = not self.case_button.isChecked()
        word = self.word_button.isChecked()
        regex = self.regex_button.isChecked()
        matches = 0
        index = 0
        if direction > 0:
            row_range = range(self.table_widget.rowCount() - 1, -1, -1)
            col_range = range(self.table_widget.columnCount() - 1, -1, -1)
        else:
            row_range = range(self.table_widget.rowCount())
            col_range = range(self.table_widget.columnCount())
        for i in row_range:
            for j in col_range:
                item = self.table_widget.item(i, j)
                if item is not None:
                    text = item.text()
                    if regex:
                        match = QRegularExpression(pattern).match(text).hasMatch()
                    else:
                        if nocase:
                            text = text.lower()
                            pattern = pattern.lower()
                        if word:
                            match = text == pattern
                        else:
                            match = pattern in text
                    if match and pattern:
                        self.table_widget.item(i, j).setBackground(Qt.yellow)
                        if (direction > 0 and (i > row or i == row and j > col)) or \
                                (direction < 0 and (i < row or i == row and j < col)):
                            self.table_widget.setCurrentCell(i, j)
                            index = matches
                        matches += 1
                    else:
                        self.table_widget.item(i, j).setBackground(Qt.transparent)
        if pattern:
            self.matches_label.setVisible(True)
            if matches > 0:
                match = matches - index if direction > 0 else index + 1
                self.matches_label.setText(self.tr('match #{}/{}'.format(match, matches)))
                self.matches_label.setStyleSheet('color: #000000')
                modify_font(self.matches_label, bold=True)
            else:
                self.matches_label.setText(self.tr('not found!'))
                self.matches_label.setStyleSheet('color: #FF0000')
                modify_font(self.matches_label, italic=True)
        else:
            self.matches_label.setText('')

    def export(self):
        settings = QSettings()
        filename = QFileDialog.getSaveFileName(
            self, self.tr('Export metadata'), settings.value('save_folder'), self.tr('CSV files (*.csv)'))[0]
        if not filename:
            return
        if not filename.endswith('.csv'):
            filename += '.csv'
        settings.setValue('save_folder', QFileInfo(filename).absolutePath())

        rows = self.table_widget.rowCount()
        cols = self.table_widget.columnCount()
        table = [[None for _ in range(cols)] for __ in range(rows)]
        for i in range(rows):
            for j in range(cols):
                item = self.table_widget.item(i, j)
                if item is not None:
                    table[i][j] = item.text()
        with open(filename, 'w') as file:
            writer = csv.writer(file)
            writer.writerow(self.table_headers)
            writer.writerows(table)

    def copy(self, item):
        QApplication.clipboard().setText(item.text())
        QToolTip.showText(QCursor.pos(), self.tr('Cell contents copied to clipboard'), self, QRect(), 3000)
