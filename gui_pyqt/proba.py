from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QStandardItemModel, QStandardItem

class MyWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Tworzenie głównego widgetu
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)

        # Ustawienie layoutu
        layout = QtWidgets.QVBoxLayout(central_widget)

        # Tworzenie QScrollArea
        scroll_area = QtWidgets.QScrollArea(self)
        scroll_area.setWidgetResizable(True)  # Rozciąganie zawartości
        scroll_area.setStyleSheet("""
            QScrollBar:vertical {
                border: 2px solid #d3d3d3;
                background: #accccb;
                width: 20px;
                margin: 22px 0 22px 0;
            }

            QScrollBar::handle:vertical {
                background: #c0c0c0;
                min-height: 20px;
                border-radius: 10px;
            }

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                background: none;
            }

            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                background: none;
                width: 0;
                height: 0;
            }
        """)

        # Tworzenie QWidget jako kontenera dla QTableView
        table_container = QtWidgets.QWidget(scroll_area)
        scroll_area.setWidget(table_container)

        # Tworzenie layoutu dla kontenera
        container_layout = QtWidgets.QVBoxLayout(table_container)

        # Tworzenie QTableView
        self.table_view = QtWidgets.QTableView(self)
        self.model = QStandardItemModel(20, 5)  # 20 wierszy, 5 kolumn
        self.model.setHorizontalHeaderLabels(['Col1', 'Col2', 'Col3', 'Col4', 'Col5'])

        # Dodanie przykładowych danych
        for row in range(20):
            for column in range(5):
                item = QStandardItem(f"Item {row},{column}")
                self.model.setItem(row, column, item)

        self.table_view.setModel(self.model)

        # Dodanie QTableView do kontenera
        container_layout.addWidget(self.table_view)

        # Dodanie QScrollArea do głównego layoutu
        layout.addWidget(scroll_area)

        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('QTableView in QScrollArea')

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = MyWindow()
    window.show()
    app.exec_()
