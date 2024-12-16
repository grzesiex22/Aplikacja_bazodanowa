import os
from fileinput import close

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QTableView, QFrame, QLineEdit, QVBoxLayout, QMessageBox, QGridLayout, QLabel, QPushButton, \
    QAbstractItemView, QComboBox, QSpinBox, QDialog
from urllib.parse import urlparse
import requests
from functools import partial


class JakiPojazd(QFrame):
    finished = pyqtSignal()

    def __init__(self, api_url, parent=None, header_title="title", refresh_callback=None):
        super().__init__(parent)
        print("Okno JakiPojazd zostało utworzone.")

        # Pełna ścieżka do folderu z ikonami
        self.icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'icons')).replace('\\', '/')

        # Styl dla QComboBox
        file_path = os.path.join(os.path.dirname(__file__), '..', 'qss', 'FilterFrame_QComboBox.qss')
        with open(file_path, "r") as file:
            self.combobox_style = file.read()
        self.combobox_style = self.combobox_style.replace('url(icons/', f'url({self.icon_path}/')

        self.api_url = api_url  # URL dla danych z API
        self.refresh_callback = refresh_callback  # Przechowujemy funkcję odświeżania

        # Do przesuwania oknem
        self.is_moving = False
        self.mouse_press_pos = None

        # Wymiary okna
        self.app_width = 0
        self.app_height = 0
        available_rect = self.parent().screen().availableGeometry()
        self.app_width = available_rect.width()
        self.app_height = available_rect.height()
        self.row_height = 50
        self.height = 200
        self.width = 500

        # Inicjalizacja pól
        self.setup_ui(header_title)  # Budowa interfejsu

    def setup_ui(self, title):
        """
        Budowanie całego UI, w tym dodanie nagłówka i przycisków.
        """
        self.setGeometry(int(self.app_width / 2 - self.width / 2), int(self.app_height / 2 - self.height / 2),
                         self.width, self.height)
        # # Sprawdź, czy okno nie jest wyświetlane poza ekranem
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        if self.app_width > 0 and self.app_height > 0:
            print(f"Ustawiono geometrię okna: {self.width}x{self.height}")
        else:
            print("Błąd w ustawianiu geometrii okna.")

        self.frame = QtWidgets.QFrame(self)
        self.frame.setGeometry(0, 0, self.width, self.height)
        self.frame.setStyleSheet("""
            QFrame {
                background-color: #c4bbf0;
                border: 2px solid #ac97e2;
                border-radius: 10px;
            }
            QLabel {
                color: #333333;
                background-color: transparent;
                border: none;
            }
        """)

        # Widget na formularz
        self.addAreaWidget = QtWidgets.QWidget(self)
        self.addAreaWidget.setGeometry(QtCore.QRect(50, 50, self.width-100, self.row_height))

        self.gridLayout_add = QtWidgets.QGridLayout(self.addAreaWidget)
        self.gridLayout_add.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_add.setSpacing(10)

        # Dodanie QComboBox
        self.vehicle_combobox = QComboBox()  # Tworzymy QComboBox
        self.vehicle_combobox.setStyleSheet(self.combobox_style)
        self.gridLayout_add.addWidget(self.vehicle_combobox, 0, 0)

        # Przycisk wyczyszczenia zmian
        self.button_clear = QtWidgets.QPushButton(self)
        self.button_clear.setGeometry(QtCore.QRect(30, 150, 200, 40))
        self.button_clear.setText("Wyczyść")
        self.button_clear.setObjectName("button_clear")
        self.button_clear.clicked.connect(self.clear_fields)

        # Przycisk zatwierdzenia
        self.button_save = QtWidgets.QPushButton(self)
        self.button_save.setGeometry(QtCore.QRect(260, 150, 200, 40))
        self.button_save.setText("Przypisz")
        self.button_save.clicked.connect(self.save_selection)
        self.button_save.setStyleSheet("""
            QPushButton {
                background-color: #94e17e;
            }
            QPushButton:hover {
                background-color: #89ce74;
            }
            QPushButton:pressed {
                background-color: #70a85f;
            }
        """)

        # Nagłówek
        self.widget_header = QtWidgets.QWidget(self)
        self.widget_header.setGeometry(QtCore.QRect(0, 0, self.width, 40))
        self.widget_header.setStyleSheet("""
            QWidget {
                background: #ac97e2;
                border-radius: 10px;
            }
        """)
        self.label_header = QtWidgets.QLabel(self.widget_header)
        self.label_header.setGeometry(QtCore.QRect(150, 10, 200, 20))
        self.label_header.setAlignment(Qt.AlignCenter)
        self.label_header.setText(title)
        self.label_header.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
            }
        """)

        # Zamknięcie okna
        self.button_exit = QtWidgets.QPushButton(self.widget_header)
        self.button_exit.setGeometry(QtCore.QRect(self.widget_header.width() - 35, 5, 30, 30))
        self.button_exit.setStyleSheet("""
            QPushButton {
                background-color: #c84043;
                border: 2px solid white;
                border-radius: 10px;
                opacity: 0.5;
            }
            QPushButton:hover {
                background-color: #a73639;
            }
        """)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(f"{self.icon_path}/cross_white.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_exit.setIcon(icon1)
        self.button_exit.setIconSize(QtCore.QSize(15, 15))
        self.button_exit.clicked.connect(self.close_window)

        # self.show()
        self.populate_vehicle_combobox()

    def populate_vehicle_combobox(self):
        """
        Pobiera dane z API i ładuje je do QComboBox.
        """
        self.vehicle_combobox.clear()  # Wyczyszczenie obecnych elementów
        self.vehicle_combobox.addItem("", "")  # Dodanie pustego elementu

        try:
            api_endpoint = f"{self.api_url}/pojazd/show/alltochoice"
            response = requests.get(api_endpoint, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):  # Sprawdzenie, czy dane są listą
                    for item in data:
                        display_text = item.get('data', 'Brak danych')  # Pobierz tekst do wyświetlenia
                        item_id = item.get('ID', '')  # Pobierz ID elementu
                        self.vehicle_combobox.addItem(display_text, item_id)
                else:
                    QMessageBox.warning(self, "Błąd danych", "Dane zwrócone z API mają niepoprawny format.")
            else:
                QMessageBox.warning(self, "Błąd API", f"Nie udało się pobrać danych.\nKod: {response.status_code}")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Błąd", f"Nie udało się połączyć z API.\nSzczegóły: {e}")

    def save_selection(self):
        """
        Zapisuje wybrany pojazd.
        """
        selected_id = self.vehicle_combobox.currentData()
        selected_text = self.vehicle_combobox.currentText()

        self.vehicle_data = {
            'id': selected_id,
            'name': selected_text
        }

        if selected_id:
            # QMessageBox.information(self, "Wybrano pojazd", f"Wybrano: {selected_text}\nID: {selected_id}")
            if self.refresh_callback:
                self.refresh_callback(self.vehicle_data)  # Przekazanie vehicle_data do callbacku
            self.close_window()
            print("Dane pojazdu zapisane.")
            print("koniec save_selection")
        else:
            QMessageBox.warning(self, "Błąd", "Nie wybrano żadnego pojazdu.")

    def close_window(self):
        self.finished.emit()
        self.close()

    def clear_fields(self):
        """
        Czyści pola formularza.
        """
        self.vehicle_combobox.setCurrentIndex(0)

    # Obsługa przesuwania okna
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_moving = True
            self.mouse_press_pos = event.globalPos() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.is_moving and event.buttons() & Qt.LeftButton:
            screen_geometry = self.screen().geometry()
            new_position = event.globalPos() - self.mouse_press_pos
            x = max(screen_geometry.left(), min(new_position.x(), screen_geometry.right() - self.width))
            y = max(screen_geometry.top(), min(new_position.y(), screen_geometry.bottom() - self.height))
            self.move(x, y)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.is_moving = False
