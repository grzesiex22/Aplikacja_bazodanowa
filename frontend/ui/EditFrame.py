from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QLineEdit, QMessageBox, QGridLayout, QLabel, QPushButton, QAbstractItemView
import requests


class EditFrame(QFrame):
    def __init__(self, data, parent=None, header_title="title", refresh_callback=None):
        super().__init__(parent)

        self.model_data = data
        self.driver_id = None
        self.refresh_callback = refresh_callback  # Przechowujemy funkcję odświeżania
        self.fields = {}

        self.app_width = 0
        self.app_height = 0
        available_rect = self.parent().screen().availableGeometry()
        self.app_width = available_rect.width()
        self.app_height = available_rect.height()


        self.is_moving = False  # For tracking if the frame is being moved
        self.mouse_press_pos = None  # To store the initial position of the mouse press
        self.row_count = sum(1 for col in self.model_data if not col.get('primary_key'))
        self.row_height = 50

        self.height = self.row_count*self.row_height+120
        self.width = 500
        self.setGeometry(int(self.app_width/2-self.width/2), int(self.app_height/2-self.height/2), self.width, self.height)
        self.setStyleSheet("""
                            QFrame {
                                background-color: #e6d9c3;
                                border: 2px solid #cfb796 ; 
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

        self.scrollAreaWidget = QtWidgets.QWidget(self)
        self.scrollAreaWidget.setGeometry(QtCore.QRect(50, 50, 400, self.row_count*self.row_height))
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
        icon1.addPixmap(QtGui.QPixmap("icons/cross_white.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
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
        self.button_delete.clicked.connect(self.delete_driver)

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


    def setup_fields(self):
        row = 0

        # Iteracja przez dane modelu (np. wartości z bazy danych)
        for column in self.model_data:
            column_name = column['name']
            column_label = column['label']
            column_value = column['value']  # Zakładając, że 'value' zawiera wartość kolumny

            if not column.get('primary_key'):  # Pomijamy kolumny będące kluczem głównym
                # Etykieta dla kolumny
                label = QLabel(column_label)
                label.setFixedHeight(30)
                self.gridLayout_edit.addWidget(label, row, 0)

                # Pole edycyjne
                line_edit = QLineEdit(str(column_value))
                line_edit.setPlaceholderText(f"Wprowadź {column_name}")
                line_edit.setObjectName(f"line_edit_{column_name}")
                self.gridLayout_edit.addWidget(line_edit, row, 1)

                self.fields[column_name] = line_edit  # Dodaj pole do słownika

                row += 1  # Zwiększamy numer wiersza
            else:
                self.driver_id = column_value  # klucz główny


    def restore_initial_values(self):
        row = 0

        # Przechodzimy przez wszystkie kolumny z model_data i przywracamy wartości do pól
        for column in self.model_data:
            column_name = column['name']
            column_value = column['value']  # Pobierz oryginalną wartość

            if not column.get('primary_key'):  # Pomijamy klucz główny
                if column_name in self.fields:
                    # Przywracamy wartość do odpowiedniego pola formularza
                    line_edit = self.fields[column_name]
                    line_edit.setText(str(column_value))  # Ustawiamy wartość pola na początkową
                    row += 1  # Zwiększamy numer wiersza



    def save_changes(self):
        data = {}  # Tworzymy pusty słownik na dane
        # Iterujemy przez wszystkie pola w formularzu
        for field_name, field in self.fields.items():
            # Sprawdzamy, czy pole jest typu QLineEdit oraz czy zawiera tekst
            if isinstance(field, QLineEdit) and field.text().strip():
                data[field_name] = field.text().strip()  # Dodajemy dane z pola do słownika

        # Użyj requests do wysłania zapytania PUT
        try:
            print(f"Data to update: {data}")
            response = requests.put(f'http://127.0.0.1:5000/kierowca/{self.driver_id}', json=data)

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




    def delete_driver(self):

        # Wywołanie API DELETE do usunięcia kierowcy
        try:
            response = requests.delete(f'http://127.0.0.1:5000/kierowca/{self.driver_id}')
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
        self.close()


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