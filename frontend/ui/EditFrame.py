import os

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QFrame, QLineEdit, QMessageBox, QGridLayout, QLabel, QPushButton, QAbstractItemView, \
    QComboBox, QListView, QSpinBox
from Aplikacja_bazodanowa.frontend.ui.DateLineEdit import DateLineEdit
from urllib.parse import urlparse
import requests
from functools import partial


class EditFrame(QFrame):
    finished = pyqtSignal()  # Sygnał do informowania o zakończeniu pracy okna

    def __init__(self, class_name, data, api_url, parent=None, header_title="title", refresh_callback=None):
        super().__init__(parent)
        # Pełna ścieżka do folderu z ikonami
        self.icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'icons')).replace('\\', '/')

        self.model_data = data
        self.class_name = class_name
        self.api_url = api_url
        self.refresh_callback = refresh_callback  # Przechowujemy funkcję odświeżania

        # styl dla QComboBox
        file_path = os.path.join(os.path.dirname(__file__), '..', 'qss', 'EditFrame_QComboBox.qss')
        with open(file_path, "r") as file:
            self.combobox_style = file.read()
        # Zastąp wszystkie względne ścieżki obrazków pełnymi ścieżkami
        self.combobox_style = self.combobox_style.replace('url(icons/', f'url({self.icon_path}/')

        # styl dla QLineEdit
        file_path = os.path.join(os.path.dirname(__file__), '..', 'qss', 'EditFrame_QLineEdit.qss')
        with open(file_path, "r") as file:
            self.lineEdit_style = file.read()
        # Zastąp wszystkie względne ścieżki obrazków pełnymi ścieżkami
        self.lineEdit_style = self.lineEdit_style.replace('url(icons/', f'url({self.icon_path}/')

        # styl dla QSpinBox
        file_path = os.path.join(os.path.dirname(__file__), '..', 'qss', 'EditFrame_QSpinBox.qss')
        with open(file_path, "r") as file:
            self.spinBox_style = file.read()
        # Zastąp wszystkie względne ścieżki obrazków pełnymi ścieżkami
        self.spinBox_style = self.spinBox_style.replace('url(icons/', f'url({self.icon_path}/')

        # Ustawienie QIntValidator (tylko liczby całkowite)
        self.validator = QIntValidator(0, 999999, self)  # Zakres od 0 do 999999

        self.fields = {}
        self.columns = self.load_columns()
        self.driver_id = None

        self.app_width = 0
        self.app_height = 0
        available_rect = self.parent().screen().availableGeometry()
        self.app_width = available_rect.width()
        self.app_height = available_rect.height()

        self.is_moving = False  # For tracking if the frame is being moved
        self.mouse_press_pos = None  # To store the initial position of the mouse press
        self.row_count = sum(1 for col in self.columns if not col.get('primary_key'))
        self.row_height = 50

        self.height = self.row_count*self.row_height+120
        self.width = 550
        self.setGeometry(int(self.app_width/2-self.width/2), int(self.app_height/2-self.height/2), self.width, self.height)
        self.setStyleSheet("""
                            QFrame {
                                background-color: #e6d9c3;
                                border: 2px solid #cfb796 ; 
                            }
                            QPushButton {
                                color: #333333;
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
                                color: #333333;  /* Kolor tekstu dla etykiet (przykład: pomarańczowy) */
                                background-color: transparent;  /* Przezroczyste tło dla etykiet */
                                border: none;  /* Brak ramki dla etykiet */
                            }""")

        self.scrollAreaWidget = QtWidgets.QWidget(self)
        self.scrollAreaWidget.setGeometry(QtCore.QRect(50, 50, 450, self.row_count*self.row_height))
        self.scrollAreaWidget.setStyleSheet("""QLabel {
                                                background-color: #cfb796;
                                                padding: 2px;
                                                border: 0px solid #cfb796 ;  /* Brak ramki dla etykiet */
                                                border-radius: 5px;
                                                font-size: 14px;
                                            }""")
        self.scrollAreaWidget.setObjectName("scrollAreaWidgetContents")

        self.gridLayout_edit = QtWidgets.QGridLayout(self.scrollAreaWidget)
        self.gridLayout_edit.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_edit.setSpacing(10)  # Ustaw stały odstęp między elementami
        self.gridLayout_edit.setObjectName("gridLayout_edit")

        # Dodanie etykiet i pól edycyjnych
        self.setup_fields()

        self.widget_header = QtWidgets.QWidget(self)
        self.widget_header.setGeometry(QtCore.QRect(0, 0, self.width, 40))
        self.widget_header.setObjectName("widget_header_frame_edit")
        self.widget_header.setStyleSheet("""
                                        QWidget {
                                            background: #cfb796;
                                            border-radius: 10px;
                                            
                                        }""")

        self.label_header = QtWidgets.QLabel(self.widget_header)
        self.label_header.setGeometry(QtCore.QRect(int(self.widget_header.width()/2-100), 10, 200, 20))
        self.label_header.setAlignment(Qt.AlignCenter)
        self.label_header.setText(header_title)
        self.label_header.setStyleSheet("""
                                            QLabel {
                                                font-size: 16px;
                                                font-weight: bold;  /* Ustawienie pogrubienia tekstu */
                                            }""")
        self.label_header.setObjectName("label_frame_edit")

        self.button_exit = QtWidgets.QPushButton(self.widget_header)
        self.button_exit.setEnabled(True)
        self.button_exit.setGeometry(QtCore.QRect(self.widget_header.width()-35, 5, 30, 30))
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
        icon1.addPixmap(QtGui.QPixmap(f"{self.icon_path}/cross_white.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_exit.setIcon(icon1)
        self.button_exit.setIconSize(QtCore.QSize(15, 15))
        self.button_exit.setObjectName("button_exit_frame_edit")
        self.button_exit.clicked.connect(self.close_window)

        self.button_clear = QtWidgets.QPushButton(self)
        self.button_clear.setGeometry(QtCore.QRect(int(self.width/2)-120-60-20, self.height-50, 120, 40))
        self.button_clear.setText("Wyczyść")
        self.button_clear.setObjectName("button_clear")
        self.button_clear.clicked.connect(self.restore_initial_values)


        self.button_delete = QtWidgets.QPushButton(self)
        self.button_delete.setGeometry(QtCore.QRect(int(self.width/2)-60, self.button_clear.pos().y(), 120, 40))
        self.button_delete.setText("Usuń")
        self.button_delete.setStyleSheet("""
                                        QPushButton {
                                            background-color: #da6163; /* Ustawia przezroczyste tło */
                                        }
                                        QPushButton:hover {
                                            background-color: #c54e5a; /* Ustawia kolor tła po najechaniu */
                                        }
                                        QPushButton:pressed {
                                            background-color: #b04652;  /* Kolor tła po kliknięciu */
                                        }""")
        self.button_delete.setObjectName("button_delete")
        self.button_delete.clicked.connect(self.delete_item)

        self.button_save = QtWidgets.QPushButton(self)
        self.button_save.setGeometry(QtCore.QRect(int(self.width/2)+60+20, self.button_clear.pos().y(), 120, 40))
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
            response = requests.get(f"http://127.0.0.1:5000/api/columns/{self.class_name}")
            if response.status_code == 200:
                return response.json()
            else:
                print("Błąd pobierania kolumn:", response.status_code, response.text)
        except Exception as e:
            print("Błąd połączenia z API:", str(e))


    def setup_fields(self):
        row = 0
        tmp = {}

        # Iterowanie po dwóch kolekcjach jednocześnie (self.model_data i self.columns)
        for column in self.columns:
            column_name = column['friendly_name']
            column_value = self.model_data[column_name]
            input_type = column.get('input_type')
            inputs = column.get('inputs')
            editable = column.get('editable')

            if column['primary_key'] == True:
                self.driver_id = column_value  # Przypisanie klucza głównego
                continue

            # Etykieta dla kolumny
            label = QLabel(column_name)
            label.setFixedHeight(30)
            self.gridLayout_edit.addWidget(label, row, 0)

            # Tworzymy rozwijaną listę (QComboBox) dla typu pojazdu
            if editable == False:
                tmp = column
                label = QLabel(str(column_value))
                label.setFixedHeight(30)
                self.fields[column_name] = label
                self.gridLayout_edit.addWidget(label, row, 1)
            # Tworzymy rozwijaną listę (QComboBox) dla typu pojazdu
            elif input_type == 'enum':
                combo_box = QComboBox()
                # Dodajemy do combo boxa wszystkie wartości Enum TypPojazdu
                combo_box.addItem("")  # Pusty element na początku, który będzie ustawiony jako wybrany
                combo_box.addItems([typ for typ in inputs])
                combo_box.setObjectName(f"combo_box_{column_name}")

                """ stylizaca """
                combo_box.setStyleSheet(self.combobox_style)  # styl
                combo_box.findChild(QFrame).setWindowFlags(Qt.Popup | Qt.NoDropShadowWindowHint)  # brak cienia

                view = QListView(combo_box)  # ustawienie widoku QcomboBox aby wyłączyć skracanie tekstu
                combo_box.setView(view)
                combo_box.view().setAutoScroll(False)  # Wyłącza autoscroll gdy myszka poza Qcombobox
                view.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

                combo_box.setCurrentIndex(0)  # Indeks 0 odpowiada pierwszemu elementowi (pustemu)
                combo_box.setFixedHeight(30)
                combo_box.setMaxVisibleItems(8)
                """ koniec stylizaci """

                # Ustawienie wybranej wartości na podstawie model_data
                print("printuje column_value")
                print(column_value)
                if column_value:  # Jeżeli w model_data jest wartość
                    index = combo_box.findText(str(column_value))  # Znajdujemy indeks opcji
                    if index != -1:  # Jeśli wartość została znaleziona
                        combo_box.setCurrentIndex(index)  # Ustawiamy odpowiednią opcję

                self.gridLayout_edit.addWidget(combo_box, row, 1)
                self.fields[column_name] = combo_box

            # Tworzymy rozwijaną listę (QComboBox) dla typu pojazdu
            elif input_type == 'list' and isinstance(inputs, str):
                combo_box = QComboBox()
                combo_box.addItem("", "")  # Pusty element na początku
                domian_url = urlparse(self.api_url).netloc  # sparsowanie domeny
                # Dodajemy dane z API do combo box
                self.populate_combo_box_from_api(combo_box, f"http://{domian_url}/{inputs}")
                self.fields[column_name] = combo_box

                """ stylizaca """
                combo_box.setStyleSheet(self.combobox_style)  # styl
                combo_box.findChild(QFrame).setWindowFlags(Qt.Popup | Qt.NoDropShadowWindowHint)  # brak cienia

                view = QListView(combo_box)  # ustawienie widoku QcomboBox aby wyłączyć skracanie tekstu
                combo_box.setView(view)
                combo_box.view().setAutoScroll(False)  # Wyłącza autoscroll gdy myszka poza Qcombobox
                view.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

                combo_box.setCurrentIndex(0)  # Indeks 0 odpowiada pierwszemu elementowi (pustemu)
                combo_box.setFixedHeight(30)
                combo_box.setMaxVisibleItems(8)
                """ koniec stylizaci """

                name_to_connect = tmp['friendly_name']

                # Ustawienie wybranej wartości na podstawie model_data
                if column_value:  # Jeżeli w model_data jest wartość
                    index = combo_box.findText(str(column_value))  # Znajdujemy indeks opcji
                    if index != -1:  # Jeśli wartość została znaleziona
                        combo_box.setCurrentIndex(index)  # Ustawiamy odpowiednią opcję

                self.gridLayout_edit.addWidget(combo_box, row, 1)

                # Aktualizacja pola ID przy wyborze z ComboBox
                combo_box.currentIndexChanged.connect(partial(self.update_id_field, combo_box, name_to_connect))

            elif input_type == 'text':
                # Pole edycyjne
                line_edit = QLineEdit(str(column_value))
                line_edit.setFixedHeight(30)
                line_edit.setPlaceholderText(f"Wprowadź {column_name}")
                line_edit.setObjectName(f"line_edit_{column_name}")
                line_edit.setStyleSheet(self.lineEdit_style)
                self.gridLayout_edit.addWidget(line_edit, row, 1)
                self.fields[column_name] = line_edit  # Dodaj pole do słownika
            elif input_type == 'readonly':
                label = QLabel(str(column_value))
                label.setFixedHeight(30)
                self.fields[column_name] = label
                self.gridLayout_edit.addWidget(label, row, 1)

            elif input_type == 'quantity':
                # Domyślnie używamy QSpinBox dla liczb całkowitych
                spin_box = QSpinBox()
                spin_box.setMinimum(1)  # Ustaw minimalną wartość
                spin_box.setMaximum(1000000)  # Ustaw maksymalną wartość (dostosuj według potrzeb)
                spin_box.setFixedHeight(30)
                spin_box.setObjectName(f"spin_box_{column_name}")
                spin_box.setStyleSheet(self.spinBox_style)

                if column_value is not None:  # Sprawdzenie, czy w model_data jest wartość
                    try:
                        spin_box.setValue(int(column_value))
                    except ValueError:
                        print(f"Błąd konwersji wartości '{column_value}' na liczbę całkowitą dla pola '{column_name}'")
                self.gridLayout_edit.addWidget(spin_box, row, 1)
                self.fields[column_name] = spin_box

            elif input_type == 'number':
                # Tworzymy pole tekstowe
                line_edit = QLineEdit(str(column_value))
                line_edit.setValidator(self.validator)
                line_edit.setPlaceholderText(f"Wprowadź {column_name}")
                line_edit.setFixedHeight(30)
                line_edit.setObjectName(f"line_edit_{column_name}")
                line_edit.setStyleSheet(self.lineEdit_style)
                self.gridLayout_edit.addWidget(line_edit, row, 1)
                self.fields[column_name] = line_edit
            elif input_type == 'data':
                # Tworzymy pole tekstowe dla daty
                date_edit = DateLineEdit(str(column_value))
                date_edit.setFixedHeight(30)
                date_edit.setObjectName(f"line_edit_{column_name}")
                date_edit.setStyleSheet(self.lineEdit_style)
                self.gridLayout_edit.addWidget(date_edit, row, 1)
                self.fields[column_name] = date_edit

            row += 1  # Zwiększamy numer wiersza


    def populate_combo_box_from_api(self, combo_box, api_endpoint):
        """
        Pobiera dane z API i ładuje do QComboBox.
        """
        try:
            response = requests.get(api_endpoint)
            if response.status_code == 200:
                data = response.json()
                for item in data:
                    display_text = item['data']
                    combo_box.addItem(display_text, item['ID'])  # Ustawiamy `ID` jako ukryte dane
                combo_box.setMaxVisibleItems(8)
            else:
                print(f"API error: {response.status_code}")

        except Exception as e:
            print(f"Error fetching data from API: {e}")

    def update_id_field(self, combo_box, field_name):
        """
        Aktualizuje pole ID w `model_data` na podstawie wyboru w `QComboBox`.
        """
        print(f"Trying to update FIELD {field_name} to {combo_box.currentData()}")

        selected_id = combo_box.currentData()
        if field_name != None:
            self.fields[field_name].setText(str(selected_id))   # Aktualizuje `idKierowca` lub inne powiązane pole ID

    def restore_initial_values(self):
        row = 0

        # Przechodzimy przez wszystkie kolumny z model_data i przywracamy wartości do pól
        for column in self.columns:
            column_name = column['friendly_name']
            column_value = self.model_data[column_name]  # Pobierz oryginalną wartość
            print(column_value)

            if column.get('primary_key'):
                continue  # Pomijamy klucz główny
            elif column_name in self.fields:
                field = self.fields[column_name]

                if isinstance(field, QLineEdit):
                    # Przywracamy wartość do pola QLineEdit
                    field.setText(str(column_value))  # Ustawiamy wartość pola na początkową

                elif isinstance(field, QComboBox):
                    # Przywracamy wartość do pola QComboBox
                    # Zakładając, że model_data zawiera wartość odpowiadającą jednej z opcji
                    index = field.findText(str(column_value))  # Znajdujemy indeks odpowiadający wartości
                    if index != -1:
                        field.setCurrentIndex(index)  # Ustawiamy wartość na odpowiedni indeks
                    else:
                        field.setCurrentIndex(
                            0)  # Jeśli wartość nie została znaleziona, ustawiamy domyślną wartość (np. pustą)
                elif isinstance(field, QSpinBox):
                    print("wartosc do QSpinBox", column_value)
                    field_value = int(column_value)   # Pobieramy aktualnie wybraną wartość
                    field.setValue(field_value)  # Dodajemy wartość z QSpinBox do słownika

                row += 1  # Zwiększamy numer wiersza


    def save_changes(self):
        data = {}  # Tworzymy pusty słownik na dane
        # Iterujemy przez wszystkie pola w formularzu
        for field_name, field in self.fields.items():
            # Sprawdzamy, czy pole jest typu QLineEdit oraz czy zawiera tekst
            if isinstance(field, QLineEdit):
                field_value = field.text().strip()
                print(f"Pole {field_name} ma wartość: {field_value}")  # Debugowanie
                data[field_name] = field_value  # Dodajemy dane z pola do słownika
            elif isinstance(field, QComboBox):
                field_value = field.currentText().strip()  # Pobieramy aktualnie wybraną wartość
                print(f"Pole {field_name} ma wybraną wartość: {field_value}")  # Debugowanie
                data[field_name] = field_value  # Dodajemy wartość z QComboBox do słownika
            elif isinstance(field, QLabel):
                field_value = field.text().strip()  # Pobieramy aktualnie wybraną wartość
                print(f"Pole {field_name} ma wybraną wartość: {field_value}")  # Debugowanie
                data[field_name] = field_value  # Dodajemy wartość z QComboBox do słownika
            elif isinstance(field, QSpinBox):
                field_value = field.value()  # Pobieramy aktualnie wybraną wartość
                print(f"Pole {field_name} ma wybraną wartość: {field_value}")  # Debugowanie
                data[field_name] = field_value  # Dodajemy wartość z QSpinBox do słownika

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

        # Użyj requests do wysłania zapytania PUT
        try:
            print(f"Data to update: {data}")
            response = requests.put(f'{self.api_url}/edit/{self.driver_id}', json=data)

            if response.status_code == 200:
                # Jeśli zapis się powiódł, zamknij okno
                self.close_window()
            else:
                # Obsłuż błędy w odpowiedzi
                error_message = response.json().get('message', 'Wystąpił błąd')
                print(f"Błąd zapisu: {error_message}")
                # Tutaj możesz np. pokazać użytkownikowi komunikat o błędzie
                QMessageBox.warning(self, "Błąd",
                                    f"Błąd zapisu: {error_message}")

        except requests.exceptions.RequestException as e:
            print(f"Błąd połączenia z serwerem: {e}")
            # Obsłuż błędy połączenia (np. brak dostępu do serwera)
            QMessageBox.critical(self, "Błąd", f"Wystąpił błąd podczas połączenia z API: {str(e)}")


    def delete_item(self):

        # Wywołanie API DELETE do usunięcia
        try:
            response = requests.delete(f'{self.api_url}/delete/{self.driver_id}')
            if response.status_code == 200:
                self.close_window()  # Zamknij po usunięciu
            else:
                # Obsłuż błędy w odpowiedzi
                error_message = response.json().get('message', 'Wystąpił błąd')
                print(f"Błąd zapisu: {error_message}")
                QMessageBox.warning(self, "Błąd",
                                    f"Błąd zapisu: {error_message}")

        except requests.exceptions.RequestException as e:
            print(f"Błąd połączenia z serwerem: {e}")
            # Obsłuż błędy połączenia (np. brak dostępu do serwera)
            QMessageBox.critical(self, "Błąd", f"Wystąpił błąd podczas połączenia z API: {str(e)}")


    def close_window(self):
        if self.refresh_callback:
            self.refresh_callback()

        self.finished.emit()  # Emitowanie sygnału zakończenia
        self.close()


    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.is_moving = True
            self.mouse_press_pos = event.globalPos() - self.pos()
            event.accept()


    # def mouseMoveEvent(self, event):
    #     if self.is_moving and event.buttons() & QtCore.Qt.LeftButton:
    #         self.move(event.globalPos() - self.mouse_press_pos)
    #         event.accept()

    def mouseMoveEvent(self, event):
        if self.is_moving and event.buttons() & Qt.LeftButton:
            screen_geometry = self.screen().geometry()  # Pobierz geometrię ekranu, na którym znajduje się okno
            new_position = event.globalPos() - self.mouse_press_pos  # Wylicz nową pozycję okna

            # Ogranicz pozycję okna do granic ekranu
            x = max(screen_geometry.left(), min(new_position.x(), screen_geometry.right() - self.width))
            y = max(screen_geometry.top(), min(new_position.y(), screen_geometry.bottom() - self.height))

            self.move(x, y)  # Przesuń okno na ograniczoną pozycję
            event.accept()


    def mouseReleaseEvent(self, event):
        self.is_moving = False