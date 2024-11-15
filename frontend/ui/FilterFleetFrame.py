from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableView, QFrame, QLineEdit, QVBoxLayout, QMessageBox, QGridLayout, QLabel, QPushButton, \
    QAbstractItemView, QComboBox
from urllib.parse import urlparse
import requests
from functools import partial


# class FilterFleetFrame(QFrame):
#     def __init__(self, class_name, api_url, parent=None, header_title="title", filtr_parameteres_pojazd=None, refresh_callback=None):
#         super().__init__(parent)
#
#         self.api_url = api_url  # URL dla POST danych
#         self.class_name = class_name
#         self.refresh_callback = refresh_callback  # Przechowujemy funkcję odświeżania
#
#         # Dane potrzebne do zrobienia formularza
#         self.fields = {}
#         self.columns = self.load_columns()
#
#         # Do przesuwania oknem
#         self.is_moving = False
#         self.mouse_press_pos = None
#
#         # wymiary okna
#         self.app_width = 0
#         self.app_height = 0
#         available_rect = self.parent().screen().availableGeometry()
#         self.app_width = available_rect.width()
#         self.app_height = available_rect.height()
#         self.row_height = 50
#         self.row_count = sum(1 for col in self.columns if not col.get('primary_key'))
#         self.height = self.row_count * self.row_height + 120
#         self.width = 500
#
#         # Ustawienie UI
#         self.setup_ui(header_title)
#
#     def setup_ui(self, title):
#         self.setGeometry(int(self.app_width / 2 - self.width / 2), int(self.app_height / 2 - self.height / 2),
#                          self.width, self.height)
#         self.setStyleSheet("""
#                             QFrame {
#                                 background-color: #bacbbc;
#                                 border: 2px solid #90aa92 ;
#                             }
#                             QPushButton {
#                                 color: #5d5d5d;
#                                 background-color: #b9bece; /* Ustawia przezroczyste tło */
#                                 border: 2px solid #5d5d5d; /* Ustawia kolor ramki (czarny) */
#                                 border-radius: 10px; /* Zaokrąglone rogi ramki */
#                                 padding: 5px; /* Wewnętrzne odstępy, opcjonalne */
#                                 font-size: 14px;  /* Rozmiar czcionki */
#                                 font-family: Arial, sans-serif;  /* Czcionka */
#                             }
#                             QPushButton:hover {
#                                 background-color: #a2a6b4; /* Ustawia kolor tła po najechaniu */
#                             }
#                             QPushButton:pressed {
#                                 background-color: #8a8e9a;  /* Kolor tła po kliknięciu */
#                             }
#                             QPushButton:disabled {
#                                 background-color: #bdc3c7;  /* Kolor tła dla nieaktywnych przycisków */
#                                 color: #7f8c8d;  /* Kolor tekstu dla nieaktywnych przycisków */
#                                 border: 2px solid #95a5a6;  /* Obramowanie dla nieaktywnych przycisków */
#                             }
#                             QLabel {
#                                 color: #5d5d5d;  /* Kolor tekstu dla etykiet (przykład: pomarańczowy) */
#                                 background-color: transparent;  /* Przezroczyste tło dla etykiet */
#                                 border: none;  /* Brak ramki dla etykiet */
#                             }""")
#
#         # główny widget na formularz
#         self.addAreaWidget = QtWidgets.QWidget(self)
#         self.addAreaWidget.setGeometry(QtCore.QRect(50, 50, 400, self.row_count * self.row_height))
#         self.addAreaWidget.setStyleSheet("""QLabel {
#                                                 background-color: #90aa92;
#                                                 padding: 2px;
#                                                 border: 0px solid #cfb796 ;  /* Brak ramki dla etykiet */
#                                                 border-radius: 5px;
#                                                 font-size: 14px;
#                                             }""")
#         self.addAreaWidget.setObjectName("scrollAreaWidgetContents")
#
#         # układ formularza
#         self.gridLayout_add = QtWidgets.QGridLayout(self.addAreaWidget)
#         self.gridLayout_add.setContentsMargins(0, 0, 0, 0)
#         self.gridLayout_add.setSpacing(10)  # Ustaw stały odstęp między elementami
#         self.gridLayout_add.setObjectName("gridLayout_edit")
#
#         # Formularz
#         self.setup_fields(self.columns)
#
#         # Nagłówke okna
#         self.widget_header = QtWidgets.QWidget(self)
#         self.widget_header.setGeometry(QtCore.QRect(0, 0, self.width, 40))
#         self.widget_header.setObjectName("widget_header_frame_edit")
#         self.widget_header.setStyleSheet("""
#                                             QWidget {
#                                                 background: #90aa92;
#                                                 border-radius: 10px;
#
#                                             }""")
#
#         # Nazwa okna
#         self.label_header = QtWidgets.QLabel(self.widget_header)
#         self.label_header.setGeometry(QtCore.QRect(int(self.widget_header.width() / 2 - 100), 10, 200, 20))
#         self.label_header.setAlignment(Qt.AlignCenter)
#         self.label_header.setText(title)
#         self.label_header.setStyleSheet("""
#                                             QLabel {
#                                                 font-size: 16px;
#                                                 font-weight: bold;  /* Ustawienie pogrubienia tekstu */
#                                             }""")
#         self.label_header.setObjectName("label_frame_edit")
#
#         # Zamknięcie okna
#         self.button_exit = QtWidgets.QPushButton(self.widget_header)
#         self.button_exit.setEnabled(True)
#         self.button_exit.setGeometry(QtCore.QRect(self.widget_header.width() - 35, 5, 30, 30))
#         self.button_exit.setStyleSheet("""
#                                         QPushButton {
#                                           background-color: #c84043; /* Ustawia przezroczyste tło */
#                                           border: 2px solid white; /* Ustawia kolor ramki */
#                                           border-radius: 10px; /* Zaokrąglone rogi ramki */
#                                           padding: 5px; /* Wewnętrzne odstępy, opcjonalne */
#                                           opacity: 0.5;
#                                         }
#                                         QPushButton:hover {
#                                           background-color: #a73639; /* Ustawia kolor tła po najechaniu */
#                                         }""")
#         self.button_exit.setText("")
#         icon1 = QtGui.QIcon()
#         icon1.addPixmap(QtGui.QPixmap("icons/cross_white.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
#         self.button_exit.setIcon(icon1)
#         self.button_exit.setIconSize(QtCore.QSize(15, 15))
#         self.button_exit.setObjectName("button_exit_frame_edit")
#         self.button_exit.clicked.connect(self.close_window)
#
#         # Przycisk wyczyszczenia zmian
#         self.button_clear = QtWidgets.QPushButton(self)
#         self.button_clear.setGeometry(QtCore.QRect(int(self.width / 2) - 200 - 10, self.height - 50, 200, 40))
#         self.button_clear.setText("Wyczyść")
#         self.button_clear.setObjectName("button_clear")
#         self.button_clear.clicked.connect(self.clear_fields)
#
#         # Przycisk zapisania zmian
#         self.button_save = QtWidgets.QPushButton(self)
#         self.button_save.setGeometry(
#             QtCore.QRect(int(self.width / 2) + 10, self.button_clear.pos().y(), 200, 40))
#         self.button_save.setText("Filtruj")
#         self.button_save.setStyleSheet("""QPushButton {
#                                             background-color: #94e17e; /* Ustawia przezroczyste tło */
#                                         }
#                                         QPushButton:hover {
#                                            background-color: #89ce74; /* Ustawia kolor tła po najechaniu */
#                                         }
#                                         QPushButton:pressed {
#                                            background-color: #70a85f;  /* Kolor tła po kliknięciu */
#                                         }""")
#         self.button_save.setObjectName("button_save")
#         self.button_save.clicked.connect(self.save_changes)
#
#     def load_columns(self):
#         try:
#             # Żądanie do endpointu pobierania kolumn
#             tmp = f"http://127.0.0.1:5000/api/columns/{self.class_name}"
#             response = requests.get(tmp)
#             if response.status_code == 200:
#                 return response.json()
#             else:
#                 print("Błąd pobierania kolumn:", response.status_code, response.text)
#         except Exception as e:
#             print("Błąd połączenia z API:", str(e))
#
#     def setup_fields(self, columns):
#         row = 0
#         tmp = {}
#         for column in columns:
#             column_name = column['friendly_name']
#             input_type = column.get('input_type')
#             inputs = column.get('inputs')
#
#             if column['primary_key'] == True:
#                 continue
#
#             # Tworzymy etykietę
#             label = QLabel(column_name)
#             label.setFixedHeight(30)
#             self.gridLayout_add.addWidget(label, row, 0)
#
#             # Tworzymy rozwijaną listę (QComboBox) dla idKierowcy
#             if column['foreign_key'] == True:
#                 tmp = column
#                 label = QLabel("")
#                 label.setFixedHeight(30)
#                 self.fields[column_name] = label
#                 self.gridLayout_add.addWidget(label, row, 1)
#             # Tworzymy rozwijaną listę (QComboBox) dla typu pojazdu
#             elif input_type == 'enum':
#                 # combo_box = QComboBox()
#                 # # Dodajemy do combo boxa wszystkie wartości Enum TypPojazdu
#                 # combo_box.addItem("")  # Pusty element na początku, który będzie ustawiony jako wybrany
#                 # combo_box.addItems([typ for typ in inputs])
#                 # combo_box.setObjectName(f"combo_box_{column_name}")
#                 # combo_box.setCurrentIndex(0)  # Indeks 0 odpowiada pierwszemu elementowi (pustemu)
#                 # self.gridLayout_add.addWidget(combo_box, row, 1)
#                 # self.fields[column_name] = combo_box
#                 continue
#
#             # Tworzymy rozwijaną listę (QComboBox) dla typu pojazdu
#             #elif input_type == 'list' and isinstance(inputs, str):
#             elif input_type == 'list' and isinstance(inputs, str):
#                 combo_box = QComboBox()
#                 combo_box.addItem("", "")  # Pusty element na początku
#                 domian_url = urlparse(self.api_url).netloc  # sparsowanie domeny
#                 # Dodajemy dane z API do combo box
#                 self.populate_combo_box_from_api(combo_box, f"http://{domian_url}/{inputs}")
#                 self.fields[column_name] = combo_box
#
#                 name_to_connect = tmp['friendly_name'] if tmp['input_type'] == column_name else "None"
#
#                 self.gridLayout_add.addWidget(combo_box, row, 1)
#                 # Aktualizacja pola ID przy wyborze z ComboBox
#                 # combo_box.currentIndexChanged.connect(lambda idx, cb=combo_box: self.update_id_field(cb, column_name))
#                 combo_box.currentIndexChanged.connect(partial(self.update_id_field, combo_box, name_to_connect))
#             else:
#                 # Tworzymy pole tekstowe
#                 line_edit = QLineEdit()
#                 line_edit.setPlaceholderText(f"Wprowadź {column_name}")
#                 line_edit.setObjectName(f"line_edit_{column_name}")
#                 self.gridLayout_add.addWidget(line_edit, row, 1)
#                 self.fields[column_name] = line_edit
#
#             row += 1
#
#     def populate_combo_box_from_api(self, combo_box, api_endpoint):
#         """
#         Pobiera dane z API i ładuje do QComboBox.
#         """
#         try:
#             response = requests.get(api_endpoint)
#             if response.status_code == 200:
#                 data = response.json()
#                 for item in data:
#                     display_text = item['data']
#                     combo_box.addItem(display_text, item['ID'])  # Ustawiamy `ID` jako ukryte dane
#
#             else:
#                 print(f"API error: {response.status_code}")
#
#         except Exception as e:
#             print(f"Error fetching data from API: {e}")
#
#     def update_id_field(self, combo_box, field_name):
#         """
#         Aktualizuje pole ID w `model_data` na podstawie wyboru w `QComboBox`.
#         """
#         print(f"Trying to update FIELD {field_name} to {combo_box.currentData()}")
#
#         selected_id = combo_box.currentData()
#         if field_name != None:
#             self.fields[field_name].setText(str(selected_id))  # Aktualizuje `idKierowca` lub inne powiązane pole ID
#
#     def clear_fields(self):
#         # Przechodzimy przez wszystkie pola i ustawiamy pustą wartość
#         for field in self.fields.values():
#             if isinstance(field, QComboBox):
#                 # Ustawiamy QComboBox na domyślny (pierwszy element na liście lub pusty)
#                 field.setCurrentIndex(0)  # Możesz użyć -1, jeśli chcesz, aby było puste
#             else:
#                 field.clear()  # Dla innych pól (QLineEdit) czyścimy wartość
#
#     def save_changes(self):
#         self.filtr_parameteres_pojazd = {}
#         print(f"Zapis {self.class_name} z FilterFleetFrame")
#
#         for field_name, field in self.fields.items():
#             if isinstance(field, QLineEdit):
#                 field_value = field.text().strip()
#                 if field_value:
#                     self.filtr_parameteres_pojazd[field_name] = field_value
#                     print(f"Pole {field_name} ma wartość: {field_value}")
#
#             elif isinstance(field, QComboBox):
#                 field_value = field.currentText().strip()
#                 if field_value:
#                     self.filtr_parameteres_pojazd[field_name] = field_value
#                     print(f"Pole {field_name} ma wybraną wartość: {field_value}")
#
#             elif isinstance(field, QLabel):
#                 field_value = field.text().strip()
#                 if field_value:
#                     self.filtr_parameteres_pojazd[field_name] = field_value
#                     print(f"Pole {field_name} ma wybraną wartość: {field_value}")
#
#         # Potwierdzenie, że filtr został zapisany
#         print("Zapisane filtry:", self.filtr_parameteres_pojazd)
#
#         # Wywołujemy funkcję odświeżania z zapisanymi filtrami
#         if self.refresh_callback:
#             self.refresh_callback(self.filtr_parameteres_pojazd)
#
#         self.close()  # Zamykamy okno
#
#     def close_window(self):
#         if self.refresh_callback:
#             self.refresh_callback()  # Wywołujemy metodę odświeżania, jeżeli została przekazana
#         self.close()  # Zamykamy okno
#
#     # Mouse event overrides for dragging
#     def mousePressEvent(self, event):
#         if event.button() == QtCore.Qt.LeftButton:
#             self.is_moving = True
#             self.mouse_press_pos = event.globalPos() - self.pos()
#             event.accept()
#
#     def mouseMoveEvent(self, event):
#         if self.is_moving and event.buttons() & QtCore.Qt.LeftButton:
#             self.move(event.globalPos() - self.mouse_press_pos)
#             event.accept()
#
#     def mouseReleaseEvent(self, event):
#         self.is_moving = False

class FilterFleetFrame(QFrame):
    def __init__(self, class_name, api_url, parent=None, header_title="title", filtr_parameteres_pojazd=None, refresh_callback=None):
        super().__init__(parent)

        self.api_url = api_url  # URL dla POST danych
        self.class_name = class_name
        self.refresh_callback = refresh_callback  # Funkcja odświeżania
        self.filtr_parameteres_pojazd = filtr_parameteres_pojazd or {}  # Dane do wypełnienia filtrów

        # Dane potrzebne do utworzenia formularza
        self.fields = {}
        self.columns = self.load_columns()

        # Wymiary okna
        self.is_moving = False
        self.mouse_press_pos = None

        available_rect = self.parent().screen().availableGeometry()
        self.app_width = available_rect.width()
        self.app_height = available_rect.height()
        self.row_height = 50
        self.row_count = sum(1 for col in self.columns if not col.get('primary_key'))
        self.height = self.row_count * self.row_height + 120
        self.width = 500

        # Tworzenie interfejsu użytkownika
        self.setup_ui(header_title)

    def load_columns(self):
        """
        Pobiera kolumny z API na podstawie `class_name`.
        """
        try:
            url = f"http://127.0.0.1:5000/api/columns/{self.class_name}"
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                print("Błąd pobierania kolumn:", response.status_code, response.text)
                return []
        except Exception as e:
            print("Błąd połączenia z API:", str(e))
            return []

    def setup_ui(self, title):
        """
        Tworzy główny interfejs użytkownika.
        """
        self.setGeometry(int(self.app_width / 2 - self.width / 2), int(self.app_height / 2 - self.height / 2),
                         self.width, self.height)
        self.setStyleSheet("QFrame { background-color: #bacbbc; border: 2px solid #90aa92; }")

        # Główny widget formularza
        self.addAreaWidget = QtWidgets.QWidget(self)
        self.addAreaWidget.setGeometry(QtCore.QRect(50, 50, 400, self.row_count * self.row_height))
        self.gridLayout_add = QtWidgets.QGridLayout(self.addAreaWidget)
        self.gridLayout_add.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_add.setSpacing(10)

        # Formularz
        self.setup_fields(self.columns)

        # Przycisk wyczyszczenia zmian
        self.button_clear = QtWidgets.QPushButton("Wyczyść", self)
        self.button_clear.setGeometry(QtCore.QRect(int(self.width / 2) - 200 - 10, self.height - 50, 200, 40))
        self.button_clear.clicked.connect(self.clear_fields)

        # Przycisk zapisania zmian
        self.button_save = QtWidgets.QPushButton("Filtruj", self)
        self.button_save.setGeometry(QtCore.QRect(int(self.width / 2) + 10, self.button_clear.pos().y(), 200, 40))
        self.button_save.clicked.connect(self.save_changes)

    def setup_fields(self, columns):
        """
        Tworzy pola formularza na podstawie kolumn.
        """
        row = 0
        for column in columns:
            column_name = column['friendly_name']
            input_type = column.get('input_type')
            inputs = column.get('inputs')

            if column['primary_key']:
                continue

            # Tworzenie etykiety
            label = QLabel(column_name)
            label.setFixedHeight(30)
            self.gridLayout_add.addWidget(label, row, 0)

            if column['foreign_key']:
                # Klucz obcy: wyświetlany tekst
                display_label = QLabel("")
                display_label.setFixedHeight(30)
                self.fields[column_name] = display_label
                self.gridLayout_add.addWidget(display_label, row, 1)
                if column_name in self.filtr_parameteres_pojazd:
                    display_label.setText(self.filtr_parameteres_pojazd[column_name])

            elif input_type == 'enum' or (input_type == 'list' and isinstance(inputs, str)):
                # ComboBox dla typu listy lub enum
                combo_box = QComboBox()
                combo_box.addItem("", "")  # Pusty element na początku
                if input_type == 'list' and isinstance(inputs, str):
                    api_url = f"{urlparse(self.api_url).scheme}://{urlparse(self.api_url).netloc}/{inputs}"
                    self.populate_combo_box_from_api(combo_box, api_url)
                self.fields[column_name] = combo_box
                self.gridLayout_add.addWidget(combo_box, row, 1)
                if column_name in self.filtr_parameteres_pojazd:
                    idx = combo_box.findText(self.filtr_parameteres_pojazd[column_name])
                    if idx >= 0:
                        combo_box.setCurrentIndex(idx)

            else:
                # Pole tekstowe
                line_edit = QLineEdit()
                line_edit.setPlaceholderText(f"Wprowadź {column_name}")
                self.fields[column_name] = line_edit
                self.gridLayout_add.addWidget(line_edit, row, 1)
                if column_name in self.filtr_parameteres_pojazd:
                    line_edit.setText(self.filtr_parameteres_pojazd[column_name])

            row += 1

    def populate_combo_box_from_api(self, combo_box, api_endpoint):
        """
        Pobiera dane z API i wypełnia nimi QComboBox.
        """
        try:
            response = requests.get(api_endpoint)
            if response.status_code == 200:
                data = response.json()
                for item in data:
                    combo_box.addItem(item['data'], item['ID'])
            else:
                print(f"API error: {response.status_code}")
        except Exception as e:
            print(f"Error fetching data from API: {e}")

    def clear_fields(self):
        """
        Resetuje wszystkie pola formularza.
        """
        for field in self.fields.values():
            if isinstance(field, QLineEdit):
                field.clear()
            elif isinstance(field, QComboBox):
                field.setCurrentIndex(0)
            elif isinstance(field, QLabel):
                field.setText("")

    def save_changes(self):
        """
        Zapisuje zmiany i przekazuje dane do `refresh_callback`.
        """
        self.filtr_parameteres_pojazd = {}
        for field_name, field in self.fields.items():
            if isinstance(field, QLineEdit):
                value = field.text().strip()
            elif isinstance(field, QComboBox):
                value = field.currentText().strip()
            elif isinstance(field, QLabel):
                value = field.text().strip()
            else:
                continue

            if value:
                self.filtr_parameteres_pojazd[field_name] = value

        if self.refresh_callback:
            self.refresh_callback(self.filtr_parameteres_pojazd)

        self.close()
