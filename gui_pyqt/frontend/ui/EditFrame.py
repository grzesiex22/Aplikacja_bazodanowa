from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QTableView, QFrame, QLineEdit, QVBoxLayout, QScrollArea, QGridLayout, QLabel, QPushButton, QAbstractItemView


class EditFrame(QFrame):
    def __init__(self, model, row, parent=None):
        super().__init__(parent)
        self.model = model
        self.row = row

        self.setWindowTitle("Edycja Wiersza")
        self.setGeometry(100, 100, 500, 500)
        self.setStyleSheet("background-color: #dff0ef;")

        # Layout dla QScrollArea
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setGeometry(QtCore.QRect(10, 10, 480, 400))  # Ustawienie rozmiaru scroll area
        self.scroll_area.setWidgetResizable(True)

        # Widget wewnętrzny dla QScrollArea
        self.scroll_widget = QtWidgets.QWidget()
        self.edit_layout = QGridLayout(self.scroll_widget)
        # Ustawienie layoutu dla scroll_widget
        self.scroll_widget.setLayout(self.edit_layout)
        self.scroll_area.setWidget(self.scroll_widget)  # Ustawienie scroll_widget jako widget scroll_area

        # Dodawanie etykiet i pól edycyjnych
        for column in range(self.model.columnCount()):
            header_item = self.model.horizontalHeaderItem(column)  # Pobierz nagłówek kolumny
            if header_item:
                header_text = header_item.text()  # Tekst nagłówka
                item = self.model.item(self.row, column)  # Element tabeli

                # Etykieta dla nagłówka
                label = QLabel(header_text)
                self.edit_layout.addWidget(label, column, 0)  # Pierwsza kolumna

                # Pole edycyjne
                line_edit = QLineEdit(item.text())
                line_edit.setObjectName(f"line_edit_{self.row}_{column}")  # Umożliwia późniejszy dostęp
                self.edit_layout.addWidget(line_edit, column, 1)  # Druga kolumna
                self.edit_layout.setRowMinimumHeight(column, 100)
        # Przycisk do zatwierdzenia zmian
        self.save_button = QPushButton("Zapisz", self)
        self.save_button.clicked.connect(self.save_changes)
        self.edit_layout.addWidget(self.save_button, self.model.columnCount(), 0, 1, 2)  # Przycisk zajmujący całą szerokość


    def save_changes(self):
        for column in range(self.model.columnCount()):
            line_edit = self.findChild(QLineEdit, f"line_edit_{self.row}_{column}")
            if line_edit:
                # Zaktualizuj model danych z wartościami z linii edycyjnej
                self.model.item(self.row, column).setText(line_edit.text())

        self.close()  # Zamknij QFrame po zapisaniu
