import os

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QTableView, QFrame, QLineEdit, QVBoxLayout, QMessageBox, QGridLayout, QLabel, QPushButton, \
    QAbstractItemView, QComboBox
from urllib.parse import urlparse
import requests
from functools import partial
from Aplikacja_bazodanowa.frontend.ui.MultiSelectComboBox import MultiSelectComboBox



class FilterFrame(QFrame):
    # Deklaracja sygnału
    filtersUpdated = pyqtSignal(dict)  # Sygnał, który wysyła słownik filtrów
    finished = pyqtSignal()  # Sygnał do informowania o zakończeniu pracy okna

    def __init__(self, columns_info, filters, api_url, screen_type=None,  parent=None, header_title="title", refresh_callback=None):
        super().__init__(parent)


        self.api_url = api_url  # URL dla POST danych
        self.columns = columns_info
        self.filters = filters
        self.screen_type = screen_type
        self.refresh_callback = refresh_callback  # Przechowujemy funkcję odświeżania

        self.filtr_parameteres = {}


        # styl dla MultiSelectComboBox
        file_path = os.path.join(os.path.dirname(__file__), '..', 'qss', 'MultiSelectComboBox.qss')
        with open(file_path, "r") as file:
            self.combobox_style = file.read()

        # styl dla QLineEdit
        file_path = os.path.join(os.path.dirname(__file__), '..', 'qss', 'FiltrFrame_QLineEdit.qss')
        with open(file_path, "r") as file:
            self.lineEdit_style = file.read()

        # Dane potrzebne do zrobienia formularza
        self.fields = {}
        self.stable_fields = {}

        # Do przesuwania oknem
        self.is_moving = False
        self.mouse_press_pos = None

        # wymiary okna
        self.app_width = 0
        self.app_height = 0
        available_rect = self.parent().screen().availableGeometry()
        self.app_width = available_rect.width()
        self.app_height = available_rect.height()
        self.row_height = 50
        self.row_count = sum(1 for col in self.columns if col.get('filter'))
        self.height = self.row_count * self.row_height + 120
        self.width = 600
        self.multiSelectWidth = 200

        # Ustawienie UI
        self.setup_ui(header_title)


    def setup_ui(self, title):
        self.setGeometry(int(self.app_width / 2 - self.width / 2), int(self.app_height / 2 - self.height / 2),
                         self.width, self.height)
        self.setStyleSheet("""
                            QFrame {
                                background-color: #c4bbf0;
                                border: 2px solid #ac97e2 ; 
                            }
                            QPushButton {
                                color: #5d5d5d;
                                background-color: #b9bece; /* Ustawia przezroczyste tło */
                                border: 2px solid #5d5d5d; /* Ustawia kolor ramki (czarny) */
                                border-radius: 10px; /* Zaokrąglone rogi ramki */
                                padding: 5px; /* Wewnętrzne odstępy, opcjonalne */
                                font-size: 14px;  /* Rozmiar czcionki */
                                font-family: Arial, sans-serif;  /* Czcionka */
                            }
                            QPushButton:hover {
                                background-color: #a2a6b4; /* Ustawia kolor tła po najechaniu */
                            }
                            QPushButton:pressed {
                                background-color: #8a8e9a;  /* Kolor tła po kliknięciu */
                            }
                            QPushButton:disabled {
                                background-color: #bdc3c7;  /* Kolor tła dla nieaktywnych przycisków */
                                color: #7f8c8d;  /* Kolor tekstu dla nieaktywnych przycisków */
                                border: 2px solid #95a5a6;  /* Obramowanie dla nieaktywnych przycisków */
                            }
                            QLabel {
                                color: #5d5d5d;  /* Kolor tekstu dla etykiet (przykład: pomarańczowy) */
                                background-color: transparent;  /* Przezroczyste tło dla etykiet */
                                border: none;  /* Brak ramki dla etykiet */
                            }""")

        # główny widget na formularz
        self.filtrAreaWidget = QtWidgets.QWidget(self)
        self.filtrAreaWidget.setGeometry(QtCore.QRect(50, 50, 500, self.row_count * self.row_height))
        self.filtrAreaWidget.setStyleSheet("""QLabel {
                                                background-color: #ac97e2;
                                                padding: 2px;
                                                border: none ;  /* Brak ramki dla etykiet */
                                                border-radius: 5px;
                                                font-size: 14px;
                                            }""")
        self.filtrAreaWidget.setObjectName("scrollAreaWidgetContents")

        # układ formularza
        self.gridLayout_add = QtWidgets.QGridLayout(self.filtrAreaWidget)
        self.gridLayout_add.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_add.setSpacing(10)  # Ustaw stały odstęp między elementami
        self.gridLayout_add.setObjectName("gridLayout_edit")

        # Formularz
        self.setup_fields(self.columns)

        # Nagłówke okna
        self.widget_header = QtWidgets.QWidget(self)
        self.widget_header.setGeometry(QtCore.QRect(0, 0, self.width, 40))
        self.widget_header.setObjectName("widget_header_frame_edit")
        self.widget_header.setStyleSheet("""
                                            QWidget {
                                                background: #ac97e2;
                                                border-radius: 10px;

                                            }""")

        # Nazwa okna
        self.label_header = QtWidgets.QLabel(self.widget_header)
        self.label_header.setGeometry(QtCore.QRect(int(self.widget_header.width() / 2 - 100), 10, 200, 20))
        self.label_header.setAlignment(Qt.AlignCenter)
        self.label_header.setText(title)
        self.label_header.setStyleSheet("""
                                            QLabel {
                                                font-size: 16px;
                                                font-weight: bold;  /* Ustawienie pogrubienia tekstu */
                                            }""")
        self.label_header.setObjectName("label_frame_edit")

        # Zamknięcie okna
        self.button_exit = QtWidgets.QPushButton(self.widget_header)
        self.button_exit.setEnabled(True)
        self.button_exit.setGeometry(QtCore.QRect(self.widget_header.width() - 35, 5, 30, 30))
        self.button_exit.setStyleSheet("""
                                        QPushButton {
                                          background-color: #c84043; /* Ustawia przezroczyste tło */
                                          border: 2px solid white; /* Ustawia kolor ramki */
                                          border-radius: 10px; /* Zaokrąglone rogi ramki */
                                          padding: 5px; /* Wewnętrzne odstępy, opcjonalne */
                                          opacity: 0.5;
                                        }
                                        QPushButton:hover {
                                          background-color: #a73639; /* Ustawia kolor tła po najechaniu */
                                        }""")
        self.button_exit.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("icons/cross_white.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_exit.setIcon(icon1)
        self.button_exit.setIconSize(QtCore.QSize(15, 15))
        self.button_exit.setObjectName("button_exit_frame_edit")
        self.button_exit.clicked.connect(self.close_window)

        # Przycisk wyczyszczenia zmian
        self.button_clear = QtWidgets.QPushButton(self)
        self.button_clear.setGeometry(QtCore.QRect(int(self.width / 2) - 200 - 10, self.height - 50, 200, 40))
        self.button_clear.setText("Wyczyść")
        self.button_clear.setObjectName("button_clear")
        self.button_clear.clicked.connect(self.clear_fields)

        # Przycisk zapisania zmian
        self.button_save = QtWidgets.QPushButton(self)
        self.button_save.setGeometry(
            QtCore.QRect(int(self.width / 2) + 10, self.button_clear.pos().y(), 200, 40))
        self.button_save.setText("Filtruj")
        self.button_save.setStyleSheet("""QPushButton {
                                            background-color: #94e17e; /* Ustawia przezroczyste tło */
                                        }
                                        QPushButton:hover {
                                           background-color: #89ce74; /* Ustawia kolor tła po najechaniu */
                                        }
                                        QPushButton:pressed {
                                           background-color: #70a85f;  /* Kolor tła po kliknięciu */
                                        }""")
        self.button_save.setObjectName("button_save")
        self.button_save.clicked.connect(self.save_changes)

        # Ustawienie okna jako modalnego
        # self.setWindowModality(Qt.ApplicationModal)
        # self.setAttribute(Qt.WA_TransparentForMouseEvents)


    def setup_fields(self, columns):
        row = 0
        tmp = {}
        for column in columns:
            column_name = column['friendly_name']
            input_type = column.get('input_type')
            inputs = column.get('inputs')
            filter_type = column.get('filter')

            if column['primary_key'] or column['foreign_key']:
                continue

            # Tworzymy rozwijaną listę (QComboBox) dla idKierowcy
            if not filter_type:
                # ustawia tekst na podstawie wczytanych filtrów jeśli istnieją
                if column_name in self.filters:
                    current_filter = self.filters[column_name]
                    self.stable_fields[column_name] = str(current_filter)
                else:
                    self.stable_fields[column_name] = ''
                continue

            # Tworzymy etykietę
            label = QLabel(column_name)
            label.setFixedHeight(30)
            self.gridLayout_add.addWidget(label, row, 0)

            if filter_type == 'text':
                # Tworzymy pole tekstowe
                line_edit = QLineEdit()
                line_edit.setPlaceholderText(f"Wprowadź {column_name}")
                line_edit.setObjectName(f"line_edit_{column_name}")
                line_edit.setFixedHeight(30)
                line_edit.setStyleSheet(self.lineEdit_style)

                # ustawia tekst na podstawie wczytanych filtrów jeśli istnieją
                if column_name in self.filters:
                    current_filter = self.filters[column_name]
                    line_edit.setText(str(current_filter))

                self.gridLayout_add.addWidget(line_edit, row, 1)
                self.fields[column_name] = line_edit
            elif filter_type == 'select':
                # tu połączenie po api i pobranie danych do filtrów
                try:
                    if self.screen_type:
                        # Jeśli 'screen_type' jest ustawiony, dodajemy go do parametrów zapytania
                        params = {
                            'filtr': column_name,
                            'Typ pojazdu': self.screen_type  # Dodanie 'Typ pojazdu' do parametrów
                        }
                    else:
                        # Jeśli 'screen_type' nie jest ustawiony, wysyłamy zapytanie bez tego parametru
                        params = {
                            'filtr': column_name
                        }

                    # Wykonanie żądania HTTP GET do API
                    response = requests.get(f"{self.api_url}/filtry", params=params)
                    if response.status_code == 200:
                        items_data = response.json()  # Pobranie danych w formacie JSON

                        # Tworzymy rozwijane checkboxy
                        line_edit = MultiSelectComboBox(items=items_data)

                        line_edit.setStyleSheet(self.combobox_style)
                        line_edit.setObjectName(f"multiselect_edit_{column_name}")

                        # Ustawia zaznaczone filtry na podstawie wczytanych filtrów
                        if column_name in self.filters:
                            current_filter = self.filters[column_name]
                            line_edit.setSelectedItems(current_filter)

                        line_edit.setFixedHeight(30)
                        self.gridLayout_add.addWidget(line_edit, row, 1)
                        self.fields[column_name] = line_edit
                    else:
                        print(f"Błąd API: {response.status_code}")
                except Exception as e:
                    print(f"Błąd przy ładowaniu danych: {str(e)}")

            row += 1

    def clear_fields(self):
        """
        Czyści wszystkie pola formularza.
        """
        # Przechodzimy przez wszystkie pola i ustawiamy pustą wartość
        for field in self.fields.values():
            if isinstance(field, MultiSelectComboBox):
                # Ustawiamy QComboBox na domyślny (pierwszy element na liście lub pusty)
                field.clearItems()  # Resetujemy zaznaczone elementy
            else:
                field.clear()  # Dla innych pól (QLineEdit) czyścimy wartość

    def save_changes(self):
        """
            Zapisuje wartości wprowadzone przez użytkownika do słownika filtrów,
            a następnie uruchamia proces odświeżania.
        """
        self.filtr_parameteres = {}
        print(f"Zapis z FilterFramev2")

        for field_name, field in self.fields.items():
            if isinstance(field, QLineEdit):
                field_value = field.text().strip()
                if field_value:
                    self.filtr_parameteres[field_name] = field_value
                    print(f"Pole {field_name} ma wartość: {field_value}")

            elif isinstance(field, MultiSelectComboBox):
                field_value = field.selectedItems()  # Zbieramy wybrane elementy
                if field_value:
                    self.filtr_parameteres[field_name] = field_value
                    print(f"Pole {field_name} ma wybrane wartości: {field_value}")

        for field_name, field in self.stable_fields.items():
            if isinstance(field, str):
                field_value = field.strip()
                if field_value:
                    self.filtr_parameteres[field_name] = field_value
                    print(f"Pole {field_name} ma wartość: {field_value}")
                else:
                    print(f"Pole {field_name} nie jest stringiem: {field_value}")

        # Potwierdzenie, że filtr został zapisany
        print("Zapisane filtry:", self.filtr_parameteres)

        self.close_window()  # Zamykamy okno

    def close_window(self):
        """
        Metoda zamykająca okno i emitująca sygnał z filtrami.
        """
        self.filtersUpdated.emit(self.filtr_parameteres)  # Emitujemy sygnał z filtrami

        if self.refresh_callback:
            self.refresh_callback()  # Wywołujemy metodę odświeżania, jeżeli została przekazana

        self.finished.emit()  # Emitowanie sygnału zakończenia
        self.close()  # Zamykamy okno


    # Mouse event overrides for dragging
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.is_moving = True
            self.mouse_press_pos = event.globalPos() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.is_moving and event.buttons() & QtCore.Qt.LeftButton:
            self.move(event.globalPos() - self.mouse_press_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.is_moving = False