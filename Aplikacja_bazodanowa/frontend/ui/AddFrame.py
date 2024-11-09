from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QTableView, QFrame, QLineEdit, QVBoxLayout, QScrollArea, QGridLayout, QLabel, QPushButton, \
    QAbstractItemView
from sqlalchemy import inspect
from Aplikacja_bazodanowa.backend.models import Kierowca, Pojazd
import requests


class AddFrame(QFrame):
    def __init__(self, model_class, api_url, parent=None, header_title="title"):
    # def __init__(self, model_class, parent=None, header_title="title"):

        super().__init__(parent)

        self.app_width = 0
        self.app_height = 0
        available_rect = self.parent().screen().availableGeometry()
        self.app_width = available_rect.width()
        self.app_height = available_rect.height()

        self.is_moving = False  # For tracking if the frame is being moved
        self.mouse_press_pos = None  # To store the initial position of the mouse press
        self.row_height = 50
        self.row_count = 5

        height = self.row_count * self.row_height + 120
        width = 500
        self.setGeometry(int(self.app_width / 2 - width / 2), int(self.app_height / 2 - height / 2), width, height)
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

        self.addAreaWidget = QtWidgets.QWidget(self)
        self.addAreaWidget.setGeometry(QtCore.QRect(50, 50, 400, self.row_count * self.row_height))
        self.addAreaWidget.setStyleSheet("""QLabel {
                                                background-color: #cfb796;
                                                padding: 2px;
                                                border: 0px solid #cfb796 ;  /* Brak ramki dla etykiet */
                                                border-radius: 5px;
                                                font-size: 14px;
                                            }""")
        self.addAreaWidget.setObjectName("scrollAreaWidgetContents")

        self.gridLayout_add = QtWidgets.QGridLayout(self.addAreaWidget)
        self.gridLayout_add.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_add.setSpacing(10)  # Ustaw stały odstęp między elementami
        self.gridLayout_add.setObjectName("gridLayout_edit")

        # Wprowadzone dane
        # self.fields = {}
        #
        # with app.app_context():
        #     inspector = inspect(db.engine)
        #     columns = inspector.get_columns(model_class.__tablename__)
        #
        # row = 0
        # for column in columns:
        #     column_name = column['name']
        #     column_type = column['type'].__class__.__name__
        #
        #     # Pomijamy kolumnę klucza głównego (np. id)
        #     if column.get('primary_key'):
        #         continue
        #
        #     # Etykieta dla pola
        #     label = QLabel(column_name)
        #     label.setFixedHeight(30)
        #     self.gridLayout_form.addWidget(label, row, 0)
        #
        #     # Pole tekstowe lub inne na podstawie typu kolumny
        #     line_edit = QLineEdit()
        #     line_edit.setPlaceholderText(f"Wprowadź {column_name}")
        #     line_edit.setObjectName(f"line_edit_{column_name}")
        #     self.gridLayout_add.addWidget(line_edit, row, 1)
        #     self.fields[column_name] = line_edit
        #     row += 1


        self.widget_header = QtWidgets.QWidget(self)
        self.widget_header.setGeometry(QtCore.QRect(0, 0, self.width(), 40))
        self.widget_header.setObjectName("widget_header_frame_edit")
        self.widget_header.setStyleSheet("""
                                        QWidget {
                                            background: #cfb796;
                                            border-radius: 10px;

                                        }""")

        self.label_header = QtWidgets.QLabel(self.widget_header)
        self.label_header.setGeometry(QtCore.QRect(int(self.widget_header.width() / 2 - 50), 10, 100, 20))
        self.label_header.setText(header_title)
        self.label_header.setStyleSheet("""
                                            QLabel {
                                                font-size: 16px;
                                                font-weight: bold;  /* Ustawienie pogrubienia tekstu */
                                            }""")
        self.label_header.setObjectName("label_frame_edit")

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

        self.button_clear = QtWidgets.QPushButton(self)
        self.button_clear.setGeometry(QtCore.QRect(int(self.width() / 2) - 200 - 10, self.height() - 50, 200, 40))
        self.button_clear.setText("Wyczyść")
        self.button_clear.setObjectName("button_clear")


        self.button_save = QtWidgets.QPushButton(self)
        self.button_save.setGeometry(
            QtCore.QRect(int(self.width() / 2) + 10, self.button_clear.pos().y(), 120, 40))
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
    #     self.button_save.clicked.connect(self.save_changes)
    #
    # def save_changes(self):
    #     # Pobieranie danych z pól formularza
    #     data = {field_name: field.text().strip() for field_name, field in self.fields.items() if field.text().strip()}
    #
    #     # Wysłanie danych do API
    #     try:
    #         response = requests.post(self.api_url, json=data)
    #         if response.status_code == 201:
    #             print(f"Dodano nowy rekord do {self.model_class.__name__}")
    #             # Czyszczenie pól po dodaniu rekordu
    #             for field in self.fields.values():
    #                 field.clear()
    #         else:
    #             print(f"Błąd podczas dodawania: {response.status_code} - {response.text}")
    #     except Exception as e:
    #         print(f"Błąd połączenia z API: {str(e)}")
    #     self.close()  # Zamknij QFrame po zapisaniu

    def close_window(self):
        self.close()

    # # Mouse event overrides for dragging
    # def mousePressEvent(self, event):
    #     if event.button() == QtCore.Qt.LeftButton:
    #         self.is_moving = True
    #         self.mouse_press_pos = event.globalPos() - self.pos()
    #         event.accept()
    #
    # def mouseMoveEvent(self, event):
    #     if self.is_moving and event.buttons() & QtCore.Qt.LeftButton:
    #         self.move(event.globalPos() - self.mouse_press_pos)
    #         event.accept()
    #
    # def mouseReleaseEvent(self, event):
    #     self.is_moving = False