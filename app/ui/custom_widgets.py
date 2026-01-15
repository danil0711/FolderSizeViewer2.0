from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidgetItem


class SizeTableItem(QTableWidgetItem):
    def __lt__(self, other):
        return self.data(Qt.UserRole) < other.data(Qt.UserRole)

class FilesTableItem(QTableWidgetItem):
    def __lt__(self, other):
        return self.data(Qt.UserRole) < other.data(Qt.UserRole)