from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableView, QFrame, QLineEdit, QVBoxLayout, QMessageBox, QGridLayout, QLabel, QPushButton, \
    QAbstractItemView
import requests


class AddFrame(QFrame):
    def __init__(self, class_name, api_url, parent=None, header_title="title", refresh_callback=None):
        super().__init__(parent)

        self.api_url = api_url  # URL dla POST danych
        self.class_name = class_name
        self.refresh_callback = refresh_callback  # Przechowujemy funkcję odświeżania


        # Dane potrzebne do zrobienia formularza
        self.fields = {}
        self.columns = self.load_columns()

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
        self.row_count = sum(1 for col in self.columns if not col.get('primary_key'))
        self.height = self.row_count * self.row_height + 120
        self.width = 500

        # Ustawienie UI
        self.setup_ui(header_title)

    def setup_ui(self, title):
        self.setGeometry(int(self.app_width / 2 - self.width / 2), int(self.app_height / 2 - self.height / 2), self.width, self.height)
        self.setStyleSheet("""
                            QFrame {
                                background-color: #bacbbc;
                                border: 2px solid #90aa92 ; 
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
        self.addAreaWidget = QtWidgets.QWidget(self)
        self.addAreaWidget.setGeometry(QtCore.QRect(50, 50, 400, self.row_count * self.row_height))
        self.addAreaWidget.setStyleSheet("""QLabel {
                                                background-color: #90aa92;
                                                padding: 2px;
                                                border: 0px solid #cfb796 ;  /* Brak ramki dla etykiet */
                                                border-radius: 5px;
                                                font-size: 14px;
                                            }""")
        self.addAreaWidget.setObjectName("scrollAreaWidgetContents")

        # układ formularza
        self.gridLayout_add = QtWidgets.QGridLayout(self.addAreaWidget)
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
                                                background: #90aa92;
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
        self.button_save.setText("Zapisz")
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


    def load_columns(self):

        try:
            # Żądanie do endpointu pobierania kolumn
            tmp = f"http://127.0.0.1:5000/api/columns/{self.class_name}"
            response = requests.get(tmp)
            if response.status_code == 200:
                return response.json()
            else:
                print("Błąd pobierania kolumn:", response.status_code, response.text)
        except Exception as e:
            print("Błąd połączenia z API:", str(e))

    def setup_fields(self, columns):
        row = 0
        for column in columns:
            column_name = column['name']

            if column['primary_key'] == True:
                continue

            # Tworzymy etykietę
            label = QLabel(column_name)
            label.setFixedHeight(30)
            self.gridLayout_add.addWidget(label, row, 0)

            # Tworzymy pole tekstowe
            line_edit = QLineEdit()
            line_edit.setPlaceholderText(f"Wprowadź {column_name}")
            line_edit.setObjectName(f"line_edit_{column_name}")
            self.gridLayout_add.addWidget(line_edit, row, 1)
            self.fields[column_name] = line_edit
            row += 1


    def clear_fields(self):
        # Przechodzimy przez wszystkie pola i ustawiamy pustą wartość
        for field in self.fields.values():
            field.clear()


    def save_changes(self):
        data = {}  # Tworzymy pusty słownik na dane
        # Iterujemy przez wszystkie pola w formularzu
        for field_name, field in self.fields.items():
            # Sprawdzamy, czy pole jest typu QLineEdit oraz czy zawiera tekst
            if isinstance(field, QLineEdit):
                field_value = field.text().strip()
                print(f"Pole {field_name} ma wartość: {field_value}")  # Debugowanie
                data[field_name] = field_value  # Dodajemy dane z pola do słownika

        # WALIDACJA DANYCH ZA POMOCĄ API
        try:
            # Wywołanie endpointu walidacji
            response = requests.post(f"{self.api_url}/validate", json=data)
            if response.status_code != 200:
                # Jeżeli odpowiedź to błąd walidacji
                error_message = response.json().get('message', 'Wystąpił błąd walidacji')
                QMessageBox.warning(self, "Błąd walidacji", f"{error_message}")
                return  # Zatrzymujemy dalsze zapisywanie, bo dane są niepoprawne

        except Exception as e:
            print(f"Błąd połączenia z serwerem podczas walidacji: {e}")
            # Obsłuż błędy połączenia (np. brak dostępu do serwera)
            QMessageBox.critical(self, "Błąd", f"Wystąpił błąd podczas połączenia z API: {str(e)}")
            return

        # Wysłanie danych do API
        try:
            response = requests.post(f"{self.api_url}/add", json=data)
            if response.status_code == 201:
                print(f"Dodano nowy rekord do {self.class_name}")
                self.close_window()  # Zamknij QFrame po zapisaniu

            else:
                # Obsłuż błędy w odpowiedzi
                error_message = response.json().get('message', 'Wystąpił błąd')
                print(f"Błąd zapisu: {error_message}")
                # Tutaj możesz np. pokazać użytkownikowi komunikat o błędzie
                QMessageBox.warning(self, "Błąd",
                                    f"Błąd zapisu: {error_message}")
        except Exception as e:
            print(f"Błąd połączenia z serwerem: {e}")
            # Obsłuż błędy połączenia (np. brak dostępu do serwera)
            QMessageBox.critical(self, "Błąd", f"Wystąpił błąd podczas połączenia z API: {str(e)}")


    def close_window(self):
        if self.refresh_callback:
            self.refresh_callback()  # Wywołujemy metodę odświeżania, jeżeli została przekazana
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