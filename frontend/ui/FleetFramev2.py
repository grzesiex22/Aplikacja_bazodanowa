import json

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QTableView, QHeaderView, QAbstractItemView, QLineEdit, QButtonGroup, QVBoxLayout, \
    QHBoxLayout, QMessageBox, QApplication
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon, QFont  # Poprawny import
from PyQt5.QtCore import Qt, QTimer
from Aplikacja_bazodanowa.frontend.ui.EditFrame import EditFrame
from Aplikacja_bazodanowa.frontend.ui.AddFrame import AddFrame
from Aplikacja_bazodanowa.frontend.ui.FilterFrame import FilterFrame
from Aplikacja_bazodanowa.frontend.ui.Raport_Frame import SimpleGenerateRaport
from Aplikacja_bazodanowa.backend.models import TypPojazdu
import os
from enum import Enum, auto
import requests

#do raportu
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import fonts
from PyQt5.QtGui import QStandardItem
from datetime import datetime
import textwrap

class ScreenType(Enum):
    CIAGNIKI = 1
    NACZEPY = 2
    KIEROWCY = 3

class OverlayWidget(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setGeometry(parent.rect())
        self.setStyleSheet("background-color: rgba(0, 0, 0, 120);")  # Semi-transparent black
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)  # To block mouse events
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setCursor(Qt.WaitCursor)  # Ustawienie kursora oczekiwania na czas blokad

class FleetFrame(QtWidgets.QFrame):
    def __init__(self, parent=None, api_url=None):
        super(FleetFrame, self).__init__(parent)

        # Pełna ścieżka do folderu z ikonami
        self.icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'icons')).replace('\\', '/')

        # Inicjalizacja
        self.screen_type = ScreenType.CIAGNIKI
        self.api_url = api_url

        # Informacje dla tabeli pojazdy
        self.model_pojazd = QStandardItemModel()
        self.model_pojazd_columns_info, self.primary_key_index_pojazd, self.foreign_key_index_pojazd \
            = self.load_column_headers("pojazd", model=self.model_pojazd)
        self.sort_parameteres_pojazd = {'sort_by': None, 'order': 'asc'}  # przechowuje aktualne parametry sortowania pojazdu
        self.filtr_parameteres_ciagnik = {'Typ pojazdu': TypPojazdu.Ciągnik.value}
        self.filtr_parameteres_naczepa = {'Typ pojazdu': TypPojazdu.Naczepa.value}
        self.current_sorted_column_pojazd = None  # potrzebne do zmiany sortowania asc/desc

        # Informacje dla tabeli kierowcy
        self.model_kierowca = QStandardItemModel()
        self.model_kierowca_columns_info, self.primary_key_index_kierowca, self.foreign_key_index_kierowca \
            = self.load_column_headers("kierowca", model=self.model_kierowca)
        self.sort_parameteres_kierowca = {'sort_by': None, 'order': 'asc'}  # przechowuje aktualne parametry sortowania kierowcy
        self.filtr_parameteres_kierowca = {}  # przechowuje aktualne parametry sortowania pojazdu
        self.current_sorted_column_kierowca = None  # potrzebne do zmiany sortowania asc/desc

        self.primary_key_index = None  # aktualne pole z kluczem głównym (potrzebne by było wiadomow skąd pobrać ID i aby ukryć kolumne)
        self.foreign_key_index = []  # aktualne pole z kluczem głównym (potrzebne by ukryć kolumny)

        # Ustawienie rozmiaru floty
        self.width = 0
        self.height = 0
        available_rect = self.parent().screen().availableGeometry()
        self.width = available_rect.width()
        self.height = available_rect.height()
        self.setFixedSize(self.width, self.height)

        self.setup_fleet()  # Ustawienie ramki floty

        self.hide()  # schowanie się

    def setup_fleet(self):

        # Ramka floty
        self.setEnabled(False)
        self.setGeometry(QtCore.QRect(0, 50, self.width, self.height))
        self.setStyleSheet("QFrame {"
                            "    background-color: #caf0ef;"
                            "    border: 0px solid #e67e22;"
                            "    border-radius: 15px;"
                            "    font-family: Arial, sans-serif;"
                            "    font-size: 14px;"
                            "}")

        # Widget dla tytułu floty
        self.widget_frame_header = QtWidgets.QWidget(self)
        self.widget_frame_header.setGeometry(QtCore.QRect(0, 0, self.width, 50))
        self.widget_frame_header.setStyleSheet("QWidget {"
                                                "    background-color: #accccb;"
                                                "    border: 0px solid #e67e22;"
                                                "    border-radius: 15px;"
                                                "}"
                                               "QLabel {"
                                               "    color: #333333;  /* Kolor tekstu dla etykiet */"
                                               "    background-color: transparent;  /* Przezroczyste tło dla etykiet */"
                                               "    border: none;  /* Brak ramki dla etykiet */"
                                               "    font-size: 20px;  /* Rozmiar czcionki */"
                                               "    font-weight: bold;  /* Ustawienie pogrubienia tekstu */"
                                               "}"
                                               "QPushButton {"
                                               "    background-color: #a0bebd;"  # Kolor przycisku
                                               "    border: 2px solid white; /* Ustawia kolor ramki (czarny) */"
                                               "    border-radius: 15px; /* Zaokrąglone rogi ramki */"
                                               "    padding: 5px; /* Wewnętrzne odstępy, opcjonalne */"
                                               "}"
                                               "QPushButton:hover {"
                                               "    background-color: #8ea8a7; /* Ustawia kolor tła po najechaniu */"
                                               "}")

        self.widget_frame_header.setObjectName("widget_flota_header")

        self.label_frame_header = QtWidgets.QLabel(self.widget_frame_header)
        self.label_frame_header.setGeometry(QtCore.QRect(int(self.width / 2 - 200 / 2), 10, 200, 30))
        self.label_frame_header.setAlignment(Qt.AlignCenter)
        self.label_frame_header.setObjectName("label_flota_header")
        self.label_frame_header.setText("Flota")

        self.button_exit_frame = QtWidgets.QPushButton(self.widget_frame_header)
        self.button_exit_frame.setGeometry(QtCore.QRect(self.width - 40 - 10, 5, 40, 40))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(f"{self.icon_path}/undo_white.png"), QIcon.Normal, QIcon.Off)
        self.button_exit_frame.setIcon(icon)
        self.button_exit_frame.setIconSize(QtCore.QSize(30, 30))
        self.button_exit_frame.setObjectName("button_exit_flota")
        # Połączenie przycisku zamykania
        self.button_exit_frame.clicked.connect(self.hide_flota)


        # Tworzenie QScrollArea
        table_frame_width = self.width - 500
        table_frame_height = self.height - 50 - 150 - 100
        table_frame_side_margin = int(self.width / 2 - table_frame_width / 2)
        table_frame_top_margin = 150

        self.scroll_area = QtWidgets.QScrollArea(self)
        self.scroll_area.setGeometry(QtCore.QRect(
            table_frame_side_margin, table_frame_top_margin, table_frame_width, table_frame_height))
        self.scroll_area.setWidgetResizable(False)  # Rozciąganie zawartości

        # Wczytanie stylu z pliku
        file_path = os.path.join(os.path.dirname(__file__), '..', 'qss', 'FleetFrame_QScrollArea.qss')
        with open(file_path, "r") as file:
            stylesheet = file.read()
        # Zastąp wszystkie względne ścieżki obrazków pełnymi ścieżkami
        stylesheet = stylesheet.replace('url(icons/', f'url({self.icon_path}/')
        self.scroll_area.setStyleSheet(stylesheet)
        self.scroll_area.viewport().update()

        # Ustawienie tabeli
        self.tableView_flota = QTableView(self.scroll_area)
        self.tableView_flota.setGeometry(QtCore.QRect(0, 0, table_frame_width, table_frame_height))
        # Wczytanie stylu z pliku
        file_path = os.path.join(os.path.dirname(__file__), '..', 'qss', 'FleetFrame_QTableView.qss')
        with open(file_path, "r") as file:
            stylesheet = file.read()
        # Zastąp wszystkie względne ścieżki obrazków pełnymi ścieżkami
        stylesheet = stylesheet.replace('url(icons/', f'url({self.icon_path}/')
        self.tableView_flota.setStyleSheet(stylesheet)

        self.tableView_flota.setObjectName("tableView_flota")
        self.tableView_flota.setModel(self.model_kierowca)
        self.tableView_flota.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableView_flota.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableView_flota.setAlternatingRowColors(True)
        # self.tableView_flota.resizeColumnsToContents()

        # self.tableView_flota.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        # self.tableView_flota.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        self.tableView_flota.horizontalHeader().setSectionsClickable(True)
        self.tableView_flota.setCornerButtonEnabled(False)  # Usuwa kwadrat w lewym górnym rogu

        # Umożliwienie zmiany szerokości kolumn przez użytkownika
        header = self.tableView_flota.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)  # Umożliwia interaktywne zmienianie rozmiaru
        header.setStretchLastSection(False)  # Ostatnia kolumna nie rozciąga się na całą szerokość
        header.setSectionsClickable(True)  # Sekcje są klikalne, co umożliwia zmianę szerokości

        # Połączenie sygnału podwójnego kliknięcia z funkcją
        self.tableView_flota.doubleClicked.connect(self.on_table_double_click)
        self.tableView_flota.horizontalHeader().sectionClicked.connect(self.sort_by_column)

        """
        Przyciski dolne
        """
        self.widget_bottom_buttons = QtWidgets.QWidget(self)
        self.widget_bottom_buttons.setGeometry(QtCore.QRect(int(self.width/2-1000/2),
                                                            table_frame_top_margin + table_frame_height + 20,
                                                            1000, 60))
        self.widget_bottom_buttons.setObjectName("widget_bottom_buttons")

        self.button_dodaj = QtWidgets.QPushButton(self.widget_bottom_buttons)
        self.button_dodaj.setFixedHeight(60)
        self.button_dodaj.setText("DODAJ")
        self.button_dodaj.setStyleSheet("QPushButton {"
                                              "     color: #5d5d5d;"
                                              "    background-color: #79cf65; /* Ustawia przezroczyste tło */"
                                              "    border: 2px solid #5d5d5d; /* Ustawia kolor ramki (czarny) */"
                                              "    border-radius: 15px; /* Zaokrąglone rogi ramki */"
                                              "    padding: 5px; /* Wewnętrzne odstępy, opcjonalne */"
                                              "    font-size: 20px;  /* Rozmiar czcionki */"
                                              "    font-family: Arial, sans-serif;  /* Czcionka */"
                                              "}"
                                              "QPushButton:hover {"
                                              "    background-color: #6bb558; /* Ustawia kolor tła po najechaniu */"
                                              "}"
                                              "QPushButton:pressed {"
                                              "    background-color: #4e8340;  /* Kolor tła po kliknięciu */"
                                              "    border: 2px solid #4e8340; /* Ustawia kolor ramki (czarny) */"
                                              "}")
        self.button_dodaj.setObjectName("button_flota_dodaj")
        self.button_dodaj.clicked.connect(self.add_new_line)

        self.button_raport = QtWidgets.QPushButton(self.widget_bottom_buttons)
        self.button_raport.setFixedHeight(60)
        self.button_raport.setText("GENERUJ RAPORT")
        self.button_raport.setStyleSheet("""QPushButton {
                                                      color: #5d5d5d;
                                                      background-color: #c4bbf0; /* Ustawia przezroczyste tło */
                                                      border: 2px solid #5d5d5d; /* Ustawia kolor ramki (czarny) */
                                                      border-radius: 15px; /* Zaokrąglone rogi ramki */
                                                      padding: 5px; /* Wewnętrzne odstępy, opcjonalne */
                                                      font-size: 20px;  /* Rozmiar czcionki */
                                                      font-family: Arial, sans-serif;  /* Czcionka */
                                                  }
                                                  QPushButton:hover {
                                                      background-color: #ac97e2; /* Ustawia kolor tła po najechaniu */
                                                  }
                                                  QPushButton:pressed {
                                                      background-color: #927fbf;  /* Kolor tła po kliknięciu */
                                                  }""")
        self.button_raport.setObjectName("button_magazyn_raport")
        self.button_raport.clicked.connect(self.show_raport_frame)

        # Położenie Poziome dla przycisków
        self.horizontalLayout_bottom_buttons = QtWidgets.QHBoxLayout(self.widget_bottom_buttons)
        self.horizontalLayout_bottom_buttons.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_bottom_buttons.setSpacing(50)  # Ustawia odstęp między przyciskami na 20 pikseli
        self.horizontalLayout_bottom_buttons.setObjectName("horizontalLayout_bottom")

        self.horizontalLayout_bottom_buttons.addWidget(self.button_dodaj)
        self.horizontalLayout_bottom_buttons.addWidget(self.button_raport)

        """
        Przyciski górne
        """
        self.widget_choice_buttons = QtWidgets.QWidget(self)
        self.widget_choice_buttons.setGeometry(QtCore.QRect(int(self.width/2-1000/2), 70, 1000, 60))
        self.widget_choice_buttons.setObjectName("widget_choice_buttons")
        self.widget_choice_buttons.setStyleSheet("""
            QPushButton {
                height: 60px;
                color: #333333;
                background-color: #B0C4DE; /* Ustawia przezroczyste tło */
                border: 2px solid #5d5d5d; /* Ustawia kolor ramki (czarny) */
                border-radius: 15px; /* Zaokrąglone rogi ramki */
                padding: 5px; /* Wewnętrzne odstępy, opcjonalne */
                font-size: 20px;  /* Rozmiar czcionki */
                font-family: Arial, sans-serif;  /* Czcionka */
            }
            QPushButton:hover {
                background-color: #93a5ba; /* Ustawia kolor tła po najechaniu */
            }
            QPushButton:pressed {
                background-color: #768495;  /* Kolor tła po kliknięciu */
            }
            QPushButton:checked {
                background-color: #77b7dc;  /* Kolor przycisku w stanie 'selected' */
                color: white;  /* Zmiana koloru tekstu w stanie 'selected' */
            }
            QPushButton:disabled {
                background-color: #bdc3c7;  /* Kolor tła dla nieaktywnych przycisków */
                color: #7f8c8d;  /* Kolor tekstu dla nieaktywnych przycisków */
                border: 2px solid #95a5a6;  /* Obramowanie dla nieaktywnych przycisków
            """)

        # Położenie Poziome dla przycisków
        self.horizontalLayout_buttons = QtWidgets.QHBoxLayout(self.widget_choice_buttons)
        self.horizontalLayout_buttons.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_buttons.setSpacing(20)  # Ustawia odstęp między przyciskami na 20 pikseli
        self.horizontalLayout_buttons.setObjectName("horizontalLayout")

        self.button_flota_ciagniki = QtWidgets.QPushButton(self.widget_choice_buttons)
        self.button_flota_ciagniki.setText("Ciągniki siodłowe")
        self.button_flota_ciagniki.setObjectName("button_flota_ciagniki")
        self.button_flota_ciagniki.setCheckable(True)

        self.button_flota_naczepy = QtWidgets.QPushButton(self.widget_choice_buttons)
        self.button_flota_naczepy.setText("Naczepy ciężarowe")
        self.button_flota_naczepy.setObjectName("button_flota_naczepy")
        self.button_flota_naczepy.setCheckable(True)

        self.button_flota_kierowcy = QtWidgets.QPushButton(self.widget_choice_buttons)
        self.button_flota_kierowcy.setText("Kierowcy")
        self.button_flota_kierowcy.setObjectName("button_flota_kierowcy")
        self.button_flota_kierowcy.setCheckable(True)

        self.horizontalLayout_buttons.addWidget(self.button_flota_ciagniki)
        self.horizontalLayout_buttons.addWidget(self.button_flota_naczepy)
        self.horizontalLayout_buttons.addWidget(self.button_flota_kierowcy)

        # Dodanie przycisków do grupy
        self.button_group = QButtonGroup(self)
        self.button_group.addButton(self.button_flota_ciagniki, ScreenType.CIAGNIKI.value)
        self.button_group.addButton(self.button_flota_naczepy, ScreenType.NACZEPY.value)
        self.button_group.addButton(self.button_flota_kierowcy, ScreenType.KIEROWCY.value)

        # Tworzenie przycisku button_filtruj
        self.button_filtruj = QtWidgets.QPushButton(self.widget_choice_buttons)
        self.button_filtruj.setFixedWidth(70)
        self.button_filtruj.setObjectName("button_filtruj")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(f"{self.icon_path}/filter_white.png"), QIcon.Normal, QIcon.Off)
        self.button_filtruj.setCheckable(False)  # Opcjonalnie, jeśli ma być przyciskiem przełączającym
        self.button_filtruj.setIcon(icon)
        self.button_filtruj.setIconSize(QtCore.QSize(30, 30))

        self.horizontalLayout_buttons.addWidget(self.button_filtruj)
        self.button_filtruj.clicked.connect(self.show_filter_dialog)

        # Ustawienie stylu dla przycisku button_filtruj
        self.button_filtruj.setStyleSheet("""
                    QPushButton {
                        background-color: #c4bbf0; /* kolor */
                        border: 2px solid #5d5d5d;
                        border-radius: 15px;
                        padding: 5px;
                    }
                    QPushButton:hover {
                        background-color: #ac97e2;
                    }
                    QPushButton:pressed {
                        background-color: #927fbf;
                    }
                """)

        # Tworzenie przycisku button_filtruj
        self.button_wyczysc_filtry = QtWidgets.QPushButton(self.widget_choice_buttons)
        self.button_wyczysc_filtry.setFixedWidth(70)
        self.button_wyczysc_filtry.setObjectName("button_wyczysc_filtry")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(f"{self.icon_path}/clear_filter_white.png"), QIcon.Normal, QIcon.Off)
        self.button_wyczysc_filtry.setCheckable(False)  # Opcjonalnie, jeśli ma być przyciskiem przełączającym
        self.button_wyczysc_filtry.setIcon(icon)
        self.button_wyczysc_filtry.setIconSize(QtCore.QSize(30, 30))
        self.horizontalLayout_buttons.addWidget(self.button_wyczysc_filtry)

        self.button_wyczysc_filtry.clicked.connect(self.erase_filters)

        # Ustawienie stylu dla przycisku button_wyczysc_filtry
        self.button_wyczysc_filtry.setStyleSheet("""
                        QPushButton {
                        background-color: #c4bbf0; /* Złoty kolor */
                        border: 2px solid #5d5d5d;
                        border-radius: 15px;
                        padding: 5px;
                        }
                        QPushButton:hover {
                            background-color: #ac97e2;
                        }
                        QPushButton:pressed {
                            background-color: #927fbf;
                        }
                        """)

        # Podłączenie sygnału dla grupy przycisków
        self.button_group.buttonClicked[int].connect(self.update_screen_type)

        # Ustawienie stylów przycisków i początkowego stanu
        self.button_flota_ciagniki.setChecked(True)
        self.update_screen_type(ScreenType.CIAGNIKI.value)  # Ustawienie początkowej wartości zmiennej


    def erase_filters(self):
        if self.screen_type == ScreenType.KIEROWCY:
            self.filtr_parameteres_kierowca = {}
        elif self.screen_type == ScreenType.CIAGNIKI:
            self.filtr_parameteres_ciagnik = {'Typ pojazdu': TypPojazdu.Ciągnik.value}
        else:
            self.filtr_parameteres_naczepa = {'Typ pojazdu': TypPojazdu.Naczepa.value}

        self.load_data()


    def sort_by_column(self, column_index):
        column_name = self.tableView_flota.model().headerData(column_index, Qt.Horizontal)

        if self.screen_type == ScreenType.KIEROWCY:
            if self.current_sorted_column_kierowca == column_index:
                # Przełączamy pomiędzy 'asc' a 'desc'
                order = 'desc' if self.sort_parameteres_kierowca['order'] == 'asc' else 'asc'
            else:
                order = 'asc'
            self.current_sorted_column_kierowca = column_index
            self.sort_parameteres_kierowca = {'sort_by': column_name, 'order': order}  # 'asc' lub 'desc'

        else:
            if self.current_sorted_column_pojazd == column_index:
                # Przełączamy pomiędzy 'asc' a 'desc'
                order = 'desc' if self.sort_parameteres_pojazd['order'] == 'asc' else 'asc'
            else:
                order = 'asc'
            self.current_sorted_column_pojazd = column_index
            self.sort_parameteres_pojazd = {'sort_by': column_name, 'order': order}  # 'asc' lub 'desc'

        self.load_data()


    def update_screen_type(self, screen_value):
        # Zmiana wartości zmiennej na podstawie ID przycisku
        self.screen_type = ScreenType(screen_value)
        print(f"Aktualna wartość zmiennej: {self.screen_type.name}")

        self.load_data()


    def update_fleet_size(self):
        # Aktualizacja szerokości i wysokości floty na podstawie dostępnego miejsca na ekranie
        available_rect = self.parent().screen().availableGeometry()
        self.width = available_rect.width()
        self.height = available_rect.height()

        # Ustawienie rozmiaru floty na nowo obliczony
        self.setFixedSize(self.width, self.height)  # Odejmujemy 100 jako margines


    def show_flota(self):
        self.update_fleet_size()  # Zaktualizowanie rozmiaru przed pokazaniem ramki
        self.raise_()  # Przesunięcie ramki floty na wierzch
        self.show()
        self.setEnabled(True)
        # Animacja przesuwania ramki w dół
        self.animation = QtCore.QPropertyAnimation(self, b"pos")
        self.animation.setDuration(800)  # Czas trwania animacji w milisekundach
        self.animation.setStartValue(QtCore.QPoint(0, 1000))  # Zaczynamy z góry
        self.animation.setEndValue(QtCore.QPoint(0, 50))  # Kończymy na odpowiedniej pozycji
        self.animation.start()
        self.load_data()


    def hide_flota(self):
        # Animacja przesuwania ramki w górę
        self.animation = QtCore.QPropertyAnimation(self, b"pos")
        self.animation.setDuration(800)  # Czas trwania animacji w milisekundach
        self.animation.setStartValue(QtCore.QPoint(0, 50))  # Zaczynamy na odpowiedniej pozycji
        self.animation.setEndValue(QtCore.QPoint(0, 1000))  # Kończymy z góry
        self.animation.start()
        self.animation.finished.connect(self.hide)  # Ukryj po zakończeniu animacji
        self.setEnabled(False)



    def add_new_line(self):
        # Tworzymy nakładkę, która zablokuje interakcje w FleetFrame
        self.overlay = OverlayWidget(self)
        self.overlay.show()

        if self.screen_type == ScreenType.KIEROWCY:
            self.add_frame = AddFrame(class_name="kierowca", api_url=f"{self.api_url}/kierowca",
                                      parent=self, header_title="Dodawanie kierowcy", refresh_callback=self.load_data)
            self.add_frame.show()
        else:
            self.add_frame = AddFrame(class_name="pojazd", api_url=f"{self.api_url}/pojazd",
                                      parent=self, header_title="Dodawanie pojazdu", refresh_callback=self.load_data)
            self.add_frame.show()

        # Po zamknięciu okna dialogowego, przywrócenie interakcji
        self.add_frame.finished.connect(self.remove_overlay)


    def on_table_double_click(self, index):
        # Tworzymy nakładkę, która zablokuje interakcje w FleetFrame
        self.overlay = OverlayWidget(self)
        self.overlay.show()

        row = index.row()

        if self.screen_type == ScreenType.KIEROWCY:
            kierowca_id = self.model_kierowca.data(
                self.model_kierowca.index(row, self.primary_key_index_kierowca))

            # Wykonanie żądania GET do API, aby pobrać dane kierowcy
            try:
                response = requests.get(f"{self.api_url}/kierowca/show/{kierowca_id}")
                if response.status_code == 200:
                    kierowca_data = response.json()
                    # Przekazanie danych do okna edycji
                    self.edit_frame = EditFrame(class_name="kierowca", data=kierowca_data,
                                                api_url=f"{self.api_url}/kierowca",
                                                parent=self, header_title="Edycja kierowcy",
                                                refresh_callback=self.load_data)
                    self.edit_frame.show()
                else:
                    QMessageBox.warning(self, "Błąd",
                                        f"Nie udało się pobrać danych kierowcy. Status: {response.status_code}")
            except Exception as e:
                QMessageBox.critical(self, "Błąd", f"Wystąpił błąd podczas połączenia z API: {str(e)}")

        else:
            pojazd_id = self.model_pojazd.data(
                self.model_pojazd.index(row, self.primary_key_index_pojazd))

            # Wykonanie żądania GET do API, aby pobrać dane kierowcy
            try:
                response = requests.get(f"{self.api_url}/pojazd/show/{pojazd_id}")
                if response.status_code == 200:
                    pojazd_data = response.json()
                    # Przekazanie danych do okna edycji
                    self.edit_frame = EditFrame(class_name="pojazd", data=pojazd_data,
                                                api_url=f"{self.api_url}/pojazd",
                                                parent=self, header_title="Edycja pojazdu",
                                                refresh_callback=self.load_data)
                    self.edit_frame.show()
                else:
                    QMessageBox.warning(self, "Błąd",
                                        f"Nie udało się pobrać danych pojazdu. Status: {response.status_code}")
            except Exception as e:
                QMessageBox.critical(self, "Błąd", f"Wystąpił błąd podczas połączenia z API: {str(e)}")

        # Po zamknięciu okna dialogowego, przywrócenie interakcji
        self.edit_frame.finished.connect(self.remove_overlay)

    def adjust_column_widths(self):
        """
        Dostosowanie szerokości kolumn do zawartości nagłówków (+20 szerokości) z ustawieniem minimalnej szerokości.
        """
        model = self.tableView_flota.model()
        if not model:
            return

        for i in range(model.columnCount()):
            # Dopasuj szerokość kolumny do zawartości
            self.tableView_flota.resizeColumnToContents(i)

            # Uzyskaj szerokości zawartości i nagłówka
            content_width = self.tableView_flota.columnWidth(i)+20
            header_width = self.tableView_flota.horizontalHeader().sectionSize(i)

            # Wybierz większą szerokość, ale ustaw minimum na 100 pikseli
            new_width = max(content_width, header_width, 100)
            self.tableView_flota.setColumnWidth(i, new_width)

        # Ustaw szerokość kolumny klucza głównego na 0, jeśli jest dostępna
        if self.primary_key_index is not None:
            self.tableView_flota.setColumnWidth(self.primary_key_index, 0)

        # Ustaw szerokość kolumn kluczy obcych na 0
        print(f"foreign_keys: {self.foreign_key_index}")
        if self.foreign_key_index:
            for foreign_key in self.foreign_key_index:
                print(f"foreign_key: {foreign_key}")
                self.tableView_flota.setColumnWidth(foreign_key, 0)



    def load_data(self):
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)

        if self.screen_type == ScreenType.KIEROWCY:
            self.primary_key_index = self.primary_key_index_kierowca
            self.foreign_key_index = self.foreign_key_index_kierowca
            self.tableView_flota.setModel(self.model_kierowca)
            # Budowanie parametrów wyświetlania danych
            params = {
                "filter_by": json.dumps(self.filtr_parameteres_kierowca),  # Przekształcamy filtr na JSON
                "sort_by": self.sort_parameteres_kierowca['sort_by'],  # Dodajemy wartość sortowania
                "order": self.sort_parameteres_kierowca['order'],  # Dodajemy wartość kierunku sortowania
            }
            try:
                # Wykonanie żądania HTTP GET do API
                response = requests.get(f"{self.api_url}/kierowca/show", params=params)
                if response.status_code == 200:
                    kierowcy_data = response.json()  # Pobranie danych w formacie JSON

                    # Dodanie danych do modelu
                    self.model_kierowca.removeRows(0, self.model_kierowca.rowCount())  # Usuwamy poprzednie dane z modelu
                    for kierowca in kierowcy_data:
                        self.model_kierowca.appendRow([QStandardItem(str(kierowca['ID kierowcy'])),
                                              QStandardItem(kierowca['Imię']),
                                              QStandardItem(kierowca['Nazwisko']),
                                              QStandardItem(kierowca['Nr telefonu'])])
                else:
                    print(f"Błąd API: {response.status_code}")
            except Exception as e:
                print(f"Błąd przy ładowaniu danych: {str(e)}")

            # Użycie QTimer dla opóźnienia wywołania adjust_column_widths z kluczem głównym dla pojazdu
            QTimer.singleShot(0, self.adjust_column_widths)

        elif self.screen_type == ScreenType.CIAGNIKI:
            self.primary_key_index = self.primary_key_index_pojazd
            self.foreign_key_index = self.foreign_key_index_pojazd

            self.tableView_flota.setModel(self.model_pojazd)

            params = {
                "filter_by": json.dumps(self.filtr_parameteres_ciagnik),  # Przekształcamy filtr na JSON
                "sort_by": self.sort_parameteres_pojazd['sort_by'],  # Dodajemy wartość sortowania
                "order": self.sort_parameteres_pojazd['order'],  # Dodajemy wartość kierunku sortowania
            }
            print(f"Słownik dla load_data CIĄGNIK: {params}")

            try:
                # Wykonanie żądania HTTP GET do API
                response = requests.get(f"{self.api_url}/pojazd/show", params=params)
                if response.status_code == 200:
                    pojazd_data = response.json()  # Pobranie danych w formacie JSON

                    # Dodanie danych do modelu
                    self.model_pojazd.removeRows(0, self.model_pojazd.rowCount())  # Usuwamy poprzednie dane z modelu
                    for pojazd in pojazd_data:
                        self.model_pojazd.appendRow([QStandardItem(str(pojazd['ID pojazdu'])),
                                              QStandardItem(str(pojazd['ID kierowca'])),
                                              QStandardItem(pojazd['Dane kierowcy']),
                                              QStandardItem(pojazd['Typ pojazdu']),
                                              QStandardItem(pojazd['Marka']),
                                              QStandardItem(pojazd['Model']),
                                              QStandardItem(pojazd['Numer rejestracyjny']),
                                              QStandardItem(pojazd['Dodatkowe informacje'])
                                                       ])
                else:
                    print(f"Błąd API: {response.status_code}")
            except Exception as e:
                print(f"Błąd przy ładowaniu danych: {str(e)}")

            # Użycie QTimer dla opóźnienia wywołania adjust_column_widths z kluczem głównym dla pojazdu
            QTimer.singleShot(0, self.adjust_column_widths)

        elif self.screen_type == ScreenType.NACZEPY:
            self.primary_key_index = self.primary_key_index_pojazd
            self.foreign_key_index = self.foreign_key_index_pojazd

            self.tableView_flota.setModel(self.model_pojazd)

            params = {
                "filter_by": json.dumps(self.filtr_parameteres_naczepa),  # Przekształcamy filtr na JSON
                "sort_by": self.sort_parameteres_pojazd['sort_by'],  # Dodajemy wartość sortowania
                "order": self.sort_parameteres_pojazd['order'],  # Dodajemy wartość kierunku sortowania
            }
            print(f"Słownik dla load_data CIĄGNIK: {params}")

            try:
                # Wykonanie żądania HTTP GET do API
                response = requests.get(f"{self.api_url}/pojazd/show", params=params)
                if response.status_code == 200:
                    pojazd_data = response.json()  # Pobranie danych w formacie JSON

                    # Dodanie danych do modelu
                    self.model_pojazd.removeRows(0, self.model_pojazd.rowCount())  # Usuwamy poprzednie dane z modelu
                    for pojazd in pojazd_data:
                        self.model_pojazd.appendRow([QStandardItem(str(pojazd['ID pojazdu'])),
                                                     QStandardItem(str(pojazd['ID kierowca'])),
                                                     QStandardItem(pojazd['Dane kierowcy']),
                                                     QStandardItem(pojazd['Typ pojazdu']),
                                                     QStandardItem(pojazd['Marka']),
                                                     QStandardItem(pojazd['Model']),
                                                     QStandardItem(pojazd['Numer rejestracyjny']),
                                                     QStandardItem(pojazd['Dodatkowe informacje'])
                                                     ])
                else:
                    print(f"Błąd API: {response.status_code}")
            except Exception as e:
                print(f"Błąd przy ładowaniu danych: {str(e)}")

            # Użycie QTimer dla opóźnienia wywołania adjust_column_widths z kluczem głównym dla pojazdu
            QTimer.singleShot(0, self.adjust_column_widths)

    def load_column_headers(self, model_class, model):
        # Wykonanie zapytania GET do API, aby pobrać nagłówki kolumn
        try:
            response = requests.get(f"{self.api_url}/api/columns/{model_class}")
            response.raise_for_status()  # Wyrzuca wyjątek dla statusów 4xx i 5xx

            if response.status_code == 200:
                model_columns_info = response.json()  # Odpowiedź z listą kolumn
                primary_key = None
                foreign_key = []
                headers = []
                for i, column in enumerate(model_columns_info):
                    headers.append(column["friendly_name"])  # Dodaj nazwę kolumny do nagłówków
                    if column["primary_key"]:
                        primary_key = i  # Zapisz indeks kolumny będącej kluczem głównym
                    if column["foreign_key"]:
                        foreign_key.append(i)  # Zapisz indeks kolumny będącej kluczem głównym

                # Ustaw nagłówki w modelu
                model.setHorizontalHeaderLabels(headers)

                return model_columns_info, primary_key, foreign_key

        except requests.exceptions.RequestException as e:
            print(f"Error while fetching columns: {str(e)}")

        return None, None


    # tutaj beda filtry

    #########################################################################################################
    ########################################################################################################
    ########################################################################################################
    ########################################################################################################

    def on_filters_updated(self, filters):
        """
        Slot, który zostanie wywołany po zaktualizowaniu filtrów.
        """
        print(f"Filtry zostały zaktualizowane: {filters}")

        if self.screen_type == ScreenType.KIEROWCY:

            self.filtr_parameteres_kierowca = {}
            # Mapowanie kluczy `filters` do wartości w `self.filtr_parameteres_pojazd`
            for key, value in filters.items():
                self.filtr_parameteres_kierowca[key] = value

            # Potwierdzenie zaktualizowanego słownika
            print(f"Zaktualizowany słownik filtrów: {self.filtr_parameteres_kierowca}")

        if self.screen_type == ScreenType.CIAGNIKI:

            self.filtr_parameteres_ciagnik = {}
            # Mapowanie kluczy `filters` do wartości w `self.filtr_parameteres_pojazd`
            for key, value in filters.items():
                if key == 'Typ pojazdu' and value in TypPojazdu.__members__:
                    # Konwersja z nazwy na wartość wyliczenia
                    self.filtr_parameteres_ciagnik[key] = TypPojazdu[value].value
                else:
                    # Jeśli inne klucze/filtry mają być dodane bez zmian
                    self.filtr_parameteres_ciagnik[key] = value

            self.filtr_parameteres_ciagnik['Typ pojazdu'] = TypPojazdu.Ciągnik.value

            # Potwierdzenie zaktualizowanego słownika
            print(f"Zaktualizowany słownik filtrów: {self.filtr_parameteres_ciagnik}")

        if self.screen_type == ScreenType.NACZEPY:

            self.filtr_parameteres_naczepa = {}
            # Mapowanie kluczy `filters` do wartości w `self.filtr_parameteres_pojazd`
            for key, value in filters.items():
                if key == 'Typ pojazdu' and value in TypPojazdu.__members__:
                    # Konwersja z nazwy na wartość wyliczenia
                    self.filtr_parameteres_naczepa[key] = TypPojazdu[value].value
                else:
                    # Jeśli inne klucze/filtry mają być dodane bez zmian
                    self.filtr_parameteres_naczepa[key] = value

            self.filtr_parameteres_naczepa['Typ pojazdu'] = TypPojazdu.Naczepa.value

            # Potwierdzenie zaktualizowanego słownika
            print(f"Zaktualizowany słownik filtrów: {self.filtr_parameteres_naczepa}")

        self.load_data()

    def show_filter_dialog(self):
        """
        Wyświetla okno dialogowe filtrów i przekazuje dane do funkcji filtrującej.
        """
        # Tworzymy nakładkę, która zablokuje interakcje w FleetFrame
        self.overlay = OverlayWidget(self)
        self.overlay.show()

        if self.screen_type == ScreenType.KIEROWCY:
            # Przekazujemy referencję do funkcji filtrujFlote jako callback
            self.filter_dialog = FilterFrame(columns_info=self.model_kierowca_columns_info,
                                             filters=self.filtr_parameteres_kierowca,
                                             api_url=f"{self.api_url}/kierowca",
                                             parent=self, header_title="Filtrowanie kierowców",
                                             refresh_callback=self.load_data())
        elif self.screen_type == ScreenType.CIAGNIKI:
            # Przekazujemy referencję do funkcji filtrujFlote jako callback
            self.filter_dialog = FilterFrame(screen_type=self.filtr_parameteres_ciagnik['Typ pojazdu'],
                                             columns_info=self.model_pojazd_columns_info,
                                             filters=self.filtr_parameteres_ciagnik,
                                             api_url=f"{self.api_url}/pojazd",
                                             parent=self, header_title="Filtrowanie ciągników",
                                             refresh_callback=self.load_data())
        elif self.screen_type == ScreenType.NACZEPY:
            # Przekazujemy referencję do funkcji filtrujFlote jako callback
            self.filter_dialog = FilterFrame(screen_type=self.filtr_parameteres_naczepa['Typ pojazdu'],
                                             columns_info=self.model_pojazd_columns_info,
                                             filters=self.filtr_parameteres_naczepa,
                                             api_url=f"{self.api_url}/pojazd",
                                             parent=self, header_title="Filtrowanie naczep",
                                             refresh_callback=self.load_data())

        self.filter_dialog.filtersUpdated.connect(self.on_filters_updated)

        # Zamykanie kursora oczekiwania, aby użytkownik widział normalny kursor po zakończeniu
        self.filter_dialog.show()

        # Po zamknięciu okna dialogowego, przywrócenie interakcji
        self.filter_dialog.finished.connect(self.remove_overlay)

    def remove_overlay(self):
        # Usuwamy nakładkę po zamknięciu FilterFrame
        self.overlay.deleteLater()


    def show_raport_frame(self):
        """
        Wyświetla ramkę do wyboru folderu i nazwy pliku.
        """
        # Tworzymy nakładkę, która zablokuje interakcje w frame
        self.overlay = OverlayWidget(self)
        self.overlay.show()

        if self.screen_type == ScreenType.KIEROWCY:
            header = "Raport kierowców"
        if self.screen_type == ScreenType.CIAGNIKI:
            header = "Raport ciągników"
        if self.screen_type == ScreenType.NACZEPY:
            header = "Raport naczep"
        self.raport_dialog = SimpleGenerateRaport(parent=self, save_callback=self.generate_raport, header_title=header)
        self.raport_dialog.show()

        # Po zamknięciu okna dialogowego, przywrócenie interakcji
        self.raport_dialog.finished.connect(self.remove_overlay)

    def generate_raport(self, pdf_file):
        self.remove_overlay()
        print("Rozpoczęcie generowania raportu...")
        try:
            # Sprawdź katalog wyjściowy
            output_dir = os.path.dirname(pdf_file)
            print(f"Ścieżka katalogu wyjściowego: {output_dir}")
            if not os.path.exists(output_dir):
                print("Katalog nie istnieje. Tworzę...")
                os.makedirs(output_dir)

            # Rejestracja czcionki
            font_path = "./frontend/fonts/dejavu-sans-ttf-2.37/ttf/DejaVuSans.ttf"
            print(f"Ścieżka czcionki: {font_path}")
            if not os.path.exists(font_path):
                QMessageBox.critical(self, "Błąd", "Nie znaleziono pliku czcionki.")
                print("Błąd: Nie znaleziono pliku czcionki.")
                return
            pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))
            print("Czcionka została załadowana pomyślnie.")

            # Tworzenie PDF
            print(f"Tworzenie pliku PDF: {pdf_file}")
            pdf = canvas.Canvas(pdf_file, pagesize=A4)
            pdf.setTitle("Raport")

            current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"Aktualna data i czas: {current_datetime}")

            def draw_header():
                print("Rysowanie nagłówka...")
                pdf.setFont("DejaVuSans", 7)
                pdf.drawRightString(550, 830, current_datetime)

            # Nagłówek raportu
            pdf.setFont("DejaVuSans", 10)
            pdf.drawString(50, 800, "Raport")
            draw_header()

            # Wybór modelu danych na podstawie screen_type
            print(f"Typ ekranu: {self.screen_type}")
            if self.screen_type == ScreenType.KIEROWCY:
                headers = ["ID Kierowcy", "Imię", "Nazwisko", "Nr telefonu"]
                column_widths = [50, 100, 100, 80]
                model = self.model_kierowca
            elif self.screen_type in {ScreenType.CIAGNIKI, ScreenType.NACZEPY}:
                headers = ["ID Pojazdu", "ID Kierowcy", "Dane Kierowcy", "Typ Pojazdu", "Marka", "Model",
                           "Numer Rejestracyjny", "Dodatkowe Informacje"]
                column_widths = [50, 50, 90, 50, 60, 60, 90, 150]
                model = self.model_pojazd
            else:
                QMessageBox.critical(self, "Błąd", "Nieobsługiwany typ ekranu")
                print("Błąd: Nieobsługiwany typ ekranu.")
                return
            print(f"Nagłówki tabeli: {headers}")

            x_offsets = [50]
            for width in column_widths[:-1]:
                x_offsets.append(x_offsets[-1] + width)
            print(f"X-offsets kolumn: {x_offsets}")

            y_position = 770
            line_height = 12
            wrapped_line_spacing = 8

            # Nagłówki tabeli
            print("Rysowanie nagłówków tabeli...")
            pdf.setFont("DejaVuSans", 7)
            for i, header in enumerate(headers):
                pdf.drawString(x_offsets[i], y_position, header)
            y_position -= line_height

            # Dane tabeli
            print("Dodawanie danych tabeli...")
            pdf.setFont("DejaVuSans", 6)
            for row in range(model.rowCount()):
                print(f"Przetwarzanie wiersza: {row}")
                if y_position < 30:
                    print("Brak miejsca na stronie. Tworzenie nowej strony...")
                    pdf.showPage()
                    draw_header()
                    y_position = 770
                    pdf.setFont("DejaVuSans", 7)
                    for i, header in enumerate(headers):
                        pdf.drawString(x_offsets[i], y_position, header)
                    y_position -= line_height
                    pdf.setFont("DejaVuSans", 6)

                # Pobranie danych wiersza
                values = []
                for col in range(len(headers)):
                    item = model.item(row, col)
                    value = item.text() if item and item.text() else "Brak danych"
                    values.append(value)
                print(f"Wartości wiersza: {values}")

                # Rysowanie wierszy
                max_wrapped_lines = 1
                for i, value in enumerate(values):
                    wrapped_value = textwrap.wrap(value, width=int(column_widths[i] / 6))
                    for line_idx, line in enumerate(wrapped_value):
                        y_offset = y_position - (line_idx * wrapped_line_spacing)
                        pdf.drawString(x_offsets[i], y_offset, line)
                    max_wrapped_lines = max(max_wrapped_lines, len(wrapped_value))

                # Przesunięcie pozycji Y po zakończeniu rysowania całego wiersza
                y_position -= (max_wrapped_lines - 1) * wrapped_line_spacing + line_height

            # Zapisanie PDF
            print("Zapisywanie pliku PDF...")
            pdf.save()
            QMessageBox.information(self, "Sukces", f"Raport został wygenerowany i zapisany jako {pdf_file}")
            print("Raport wygenerowany pomyślnie.")

        except PermissionError:
            QMessageBox.critical(self, "Błąd", "Brak uprawnień do zapisu pliku.")
            print("Błąd: Brak uprawnień do zapisu pliku.")
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nie udało się wygenerować raportu: {str(e)}")
            print(f"Nie udało się wygenerować raportu: {str(e)}")

    # def highlight_sorted_column(self, column_index, order):
    #     """
    #     Podświetlenie nagłówka dla danej kolumny.
    #     Dodanie strzałki sortowania.
    #     """
    #     header = self.tableView_flota.horizontalHeader()
    #
    #     # Resetowanie stylu nagłówków przed ustawieniem podświetlenia dla nowej kolumny
    #     for i in range(header.count()):
    #         file_path = os.path.join(os.path.dirname(__file__), '..', 'qss', 'FleetFrame_QTableView.qss')
    #         with open(file_path, "r") as file:
    #             stylesheet = file.read()
    #         self.tableView_flota.setStyleSheet(stylesheet)
    #
    #     # Styl dla aktualnie posortowanej kolumny
    #     if order == "asc":
    #         sort_icon = "↑"  # Ikona strzałki w górę
    #     else:
    #         sort_icon = "↓"  # Ikona strzałki w dół
    #
    #     file_path = os.path.join(os.path.dirname(__file__), '..', 'qss', 'FleetFrame_QTableView_sorted.qss')
    #     with open(file_path, "r") as file:
    #         stylesheet = file.read()
    #     self.tableView_flota.setStyleSheet(stylesheet)
    #
    #     # Dodanie stylu do nagłówka do wczytanego stylesheet
    #     header_style = f"""
    #         QHeaderView::section:nth-child({column_index + 1}) {{
    #             background-color: #ADD8E6;
    #             color: darkblue;
    #             font-weight: bold;
    #             padding-left: 20px;
    #             background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text x="10" y="40" font-size="30" fill="black">{sort_icon}</text></svg>');
    #             background-repeat: no-repeat;
    #             background-position: right center;
    #         }}
    #     """
    #
    #     # Połączenie stylu z pliku z dodatkowym stylem dla nagłówka
    #     final_stylesheet = stylesheet + header_style
    #
    #     # Ustawienie połączonego stylu na tableView
    #     self.tableView_flota.setStyleSheet(final_stylesheet)
