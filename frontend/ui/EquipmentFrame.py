from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QTableView, QHeaderView, QAbstractItemView, QLineEdit, QButtonGroup, QVBoxLayout, QHBoxLayout, QMessageBox
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon, QFont  # Poprawny import
from PyQt5.QtCore import Qt, QTimer
from sqlalchemy import inspect

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import fonts
from PyQt5.QtGui import QStandardItem
from datetime import datetime
import textwrap

from Aplikacja_bazodanowa.frontend.ui.EditFrameWyposazenie import EditFrameWyposazenie
from Aplikacja_bazodanowa.frontend.ui.AddFrame import AddFrame
from Aplikacja_bazodanowa.frontend.ui.FilterFrameMagazine import FilterFrameMagazine
from Aplikacja_bazodanowa.frontend.ui.RaportFrame import RaportFrame
from Aplikacja_bazodanowa.backend.models import TypPojazdu

import os
from enum import Enum, auto
import requests
#
# class ScreenType(Enum):
#     CZESCI = 1
#     WYPOSAZENIE = 2

class OverlayWidget(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setGeometry(parent.rect())
        self.setStyleSheet("background-color: rgba(0, 0, 0, 120);")  # Semi-transparent black
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)  # To block mouse events
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setCursor(Qt.WaitCursor)  # Ustawienie kursora oczekiwania na czas blokad

class EquipmentFrame(QtWidgets.QFrame):
    def __init__(self, parent=None, api_url=None):
        super(EquipmentFrame, self).__init__(parent)

        # Pełna ścieżka do folderu z ikonami
        self.icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'icons')).replace('\\', '/')

        # # Inicjalizacja
        # self.screen_type = ScreenType.CZESCI
        self.api_url = api_url

        # Inicjalizacja flagi
        self.is_filtering = False

        # Flaga, która będzie informować, czy filtry zostały ustawione
        self.filters_set = False

        # Informacje dla tabeli pojazdy
        self.model_pojazd = QStandardItemModel()
        self.model_pojazd_columns_info, self.primary_key_index_czesc = self.load_column_headers("WyposazeniePojazdu", self.model_pojazd)
        self.sort_parameteres_czesci_order = 'asc'  # przechowuje aktualne parametry sortowania pojazdu
        self.sort_parameteres_czesci_sort_by = ''
        self.sort_parameteres_wyposazenie = {}  # przechowuje aktualne parametry sortowania pojazdu
        self.filtr_parameteres_czesci = {}  # przechowuje aktualne parametry sortowania pojazdu
        self.current_sorted_column_czesci = None  # potrzebne do zmiany sortowania asc/desc
        self.current_sorted_column_wyposazenie = None  # potrzebne do zmiany sortowania asc/desc



        self.primary_key_index = None  # aktualne pole z kluczem głównym (potrzebne by było wiadomow skąd pobrać ID i aby ukryć kolumne)

        # Ustawienie rozmiaru magazynu
        self.width = 0
        self.height = 0
        available_rect = self.parent().screen().availableGeometry()
        self.width = available_rect.width()
        self.height = available_rect.height()
        self.setFixedSize(self.width, self.height)

        self.setup_frame()  # Ustawienie ramki magazynu

        self.hide()  # schowanie się

    def load_column_headers(self, model_name, model):
        """
        Wczytuje nagłówki kolumn dla danego modelu.
        """
        try:
            # Przykład statycznych nagłówków, dostosuj do swojej logiki
            headers = {
                "WyposazeniePojazdu": ["IDWyposażeniaPojazdu", "Pojazd", "Opis", "Ilość"],
                # Możesz dodać więcej modeli z odpowiednimi nagłówkami
            }

            if model_name not in headers:
                raise ValueError(f"Nie znaleziono nagłówków dla modelu: {model_name}")

            column_headers = headers[model_name]
            primary_key_index = 0  # Zakładamy, że klucz główny to pierwsza kolumna

            # Dodawanie nagłówków do modelu
            model.setHorizontalHeaderLabels(column_headers)

            return column_headers, primary_key_index

        except Exception as e:
            print(f"Błąd podczas wczytywania nagłówków kolumn: {e}")
            return [], None

    def setup_frame(self):

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
        self.widget_flota_header = QtWidgets.QWidget(self)
        self.widget_flota_header.setGeometry(QtCore.QRect(0, 0, self.width, 50))
        self.widget_flota_header.setStyleSheet("QWidget {"
                                                "    background-color: #accccb;"
                                                "    border: 0px solid #e67e22;"
                                                "    border-radius: 15px;"
                                                "}"
                                               "QLabel {"
                                               "    color: #333333;"
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

        self.widget_flota_header.setObjectName("widget_flota_header")

        self.label_flota_header = QtWidgets.QLabel(self.widget_flota_header)
        self.label_flota_header.setGeometry(QtCore.QRect(int(self.width / 2 - 200 / 2), 10, 200, 30))
        self.label_flota_header.setAlignment(Qt.AlignCenter)
        self.label_flota_header.setObjectName("label_flota_header")
        self.label_flota_header.setText("Wyposażenie")

        self.button_exit_flota = QtWidgets.QPushButton(self.widget_flota_header)
        self.button_exit_flota.setGeometry(QtCore.QRect(self.width-40-10, 5, 40, 40))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(f"{self.icon_path}/undo_white.png"), QIcon.Normal, QIcon.Off)
        self.button_exit_flota.setIcon(icon)
        self.button_exit_flota.setIconSize(QtCore.QSize(30, 30))
        self.button_exit_flota.setObjectName("button_exit_flota")
        # Połączenie przycisku zamykania
        self.button_exit_flota.clicked.connect(self.hide_flota)


        # Tworzenie QScrollArea
        table_fleet_width = self.width-500
        table_fleet_height = self.height - 50 - 150 - 100
        table_fleet_side_margin = int(self.width/2-table_fleet_width/2)
        table_fleet_top_margin = 150

        self.scroll_area = QtWidgets.QScrollArea(self)
        self.scroll_area.setGeometry(QtCore.QRect(
            table_fleet_side_margin, table_fleet_top_margin, table_fleet_width, table_fleet_height))
        self.scroll_area.setWidgetResizable(False)  # Rozciąganie zawartości
        # Wczytanie stylu z pliku
        file_path = os.path.join(os.path.dirname(__file__), '..', 'qss', 'FleetFrame_QScrollArea.qss')
        with open(file_path, "r") as file:
            stylesheet = file.read()
        stylesheet = stylesheet.replace('url(icons/', f'url({self.icon_path}/')
        self.scroll_area.setStyleSheet(stylesheet)
        self.scroll_area.viewport().update()

        # Ustawienie tabeli
        self.tableView_flota = QTableView(self.scroll_area)
        self.tableView_flota.setGeometry(QtCore.QRect(0, 0, table_fleet_width, table_fleet_height))
        # Wczytanie stylu z pliku
        file_path = os.path.join(os.path.dirname(__file__), '..', 'qss', 'FleetFrame_QTableView.qss')
        with open(file_path, "r") as file:
            stylesheet = file.read()
        self.tableView_flota.setStyleSheet(stylesheet)

        self.tableView_flota.setObjectName("tableView_flota")
        self.tableView_flota.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableView_flota.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableView_flota.setAlternatingRowColors(True)

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
                                                            table_fleet_top_margin + table_fleet_height + 20,
                                                            1000, 60))
        self.widget_bottom_buttons.setObjectName("widget_bottom_buttons")

        self.button_dodaj = QtWidgets.QPushButton(self.widget_bottom_buttons)
        self.button_dodaj.setFixedHeight(60)

        # self.button_dodaj.setGeometry(QtCore.QRect
        #     int(table_fleet_side_margin + table_fleet_width / 2 - 500 / 2),
        #     table_fleet_top_margin + table_fleet_height + 20, 500, 60))
        self.button_dodaj.setText("DODAJ")
        self.button_dodaj.setStyleSheet("QPushButton {"
                                              "     color: #333333;"
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

        self.button_magazyn_raport = QtWidgets.QPushButton(self.widget_bottom_buttons)
        self.button_magazyn_raport.setFixedHeight(60)
        self.button_magazyn_raport.setText("GENERUJ RAPORT")
        self.button_magazyn_raport.setStyleSheet("""QPushButton {
                                                      color: #333333;
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
        self.button_magazyn_raport.setObjectName("button_magazyn_raport")
        self.button_magazyn_raport.clicked.connect(self.show_raport_frame)

        # Położenie Poziome dla przycisków
        self.horizontalLayout_bottom_buttons = QtWidgets.QHBoxLayout(self.widget_bottom_buttons)
        self.horizontalLayout_bottom_buttons.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_bottom_buttons.setSpacing(50)  # Ustawia odstęp między przyciskami na 20 pikseli
        self.horizontalLayout_bottom_buttons.setObjectName("horizontalLayout_bottom")

        self.horizontalLayout_bottom_buttons.addWidget(self.button_dodaj)
        self.horizontalLayout_bottom_buttons.addWidget(self.button_magazyn_raport)

        """
        Przyciski górne
        """
        self.widget_choice_buttons = QtWidgets.QWidget(self)
        self.widget_choice_buttons.setGeometry(QtCore.QRect(int(self.width/2-200/2), 70, 200, 60))
        self.widget_choice_buttons.setObjectName("widget_choice_buttons")
        self.widget_choice_buttons.setStyleSheet("""
            QPushButton {
                height: 60px;
                color: #5d5d5d;
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

        # self.button_magazyn_czesci = QtWidgets.QPushButton(self.widget_choice_buttons)
        # self.button_magazyn_czesci.setText("Części")
        # self.button_magazyn_czesci.setObjectName("button_magazyn_czesci")
        # self.button_magazyn_czesci.setCheckable(True)
        #
        # self.button_magazyn_wyposazenie = QtWidgets.QPushButton(self.widget_choice_buttons)
        # self.button_magazyn_wyposazenie.setText("Wyposażenie")
        # self.button_magazyn_wyposazenie.setObjectName("button_magazyn_wyposazenie")
        # self.button_magazyn_wyposazenie.setCheckable(True)



        # self.horizontalLayout_buttons.addWidget(self.button_magazyn_czesci)
        # self.horizontalLayout_buttons.addWidget(self.button_magazyn_wyposazenie)

        # Dodanie przycisków do grupy
        self.button_group = QButtonGroup(self)
        # self.button_group.addButton(self.button_magazyn_czesci, ScreenType.CZESCI.value)
        # self.button_group.addButton(self.button_magazyn_wyposazenie, ScreenType.WYPOSAZENIE.value)

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

        ######przycisk wyczyść filtry####################
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

        # Podłączenie sygnału dla grupy przycisków
        self.button_group.buttonClicked[int].connect(self.update_screen_type)

        # Ustawienie stylów przycisków i początkowego stanu
        # self.button_magazyn_czesci.setChecked(True)
        # self.update_screen_type(ScreenType.CZESCI.value)  # Ustawienie początkowej wartości zmiennej

    def erase_filters(self):
        self.filters_set = False
        self.load_data()

    def sort_by_column(self, column_index):
        column_name = self.tableView_flota.model().headerData(column_index, Qt.Horizontal)
        print(f"Sorting by {column_name}...")

        # if column_name == 'Pojazd':
        #     return

        # Jeśli ta sama kolumna była wcześniej posortowana
        if self.current_sorted_column_czesci == column_index:
            # Przełącz pomiędzy 'asc' i 'desc' tylko wtedy, gdy kolumna była wcześniej posortowana
            if self.sort_parameteres_czesci_order == 'asc':
                order = 'desc'
            else:
                order = 'asc'
        else:
            if self.sort_parameteres_czesci_order == 'asc':
                order = 'desc'
            else:
                order = 'asc'

        # Aktualizowanie stanu sortowania i kolumny
        self.current_sorted_column_czesci = column_index
        self.sort_parameteres_czesci_order = order
        self.sort_parameteres_czesci_sort_by = column_name

        # Dopasowanie nazw kolumn do tych używanych w API
        if column_name == 'Opis':
            column_name = 'opis'
        if column_name == 'Ilość':
            column_name = 'ilosc'
        if column_name == 'Pojazd':
            column_name = 'pojazd'

        print(self.sort_parameteres_czesci_order, self.sort_parameteres_czesci_sort_by)

        # Załaduj dane po sortowaniu
        if self.filters_set:
            self.load_data_filtered(sort_by=column_name, order=order)
        else:
            self.load_data(sort_by=column_name, order=order)

    def update_screen_type(self, screen_value):
        # Zmiana wartości zmiennej na podstawie ID przycisku
        # self.screen_type = ScreenType(screen_value)
        print(f"Aktualna wartość zmiennej: {self.screen_type.name}")

        self.erase_filters()

        # if self.filters_set:
        #     self.load_data_filtered()
        # else:
        #     self.load_data()



    def save_changes(self, row):
        for column in range(self.model_kierowca.columnCount()):
            line_edit = self.edit_frame.findChild(QLineEdit, f"line_edit_{row}_{column}")
            if line_edit:
                # Zaktualizuj model danych z wartościami z linii edycyjnej
                self.model_kierowca.item(row, column).setText(line_edit.text())

        self.edit_frame.close()  # Zamknij QFrame po zapisaniu


    def update_fleet_size(self):
        # Aktualizacja szerokości i wysokości floty na podstawie dostępnego miejsca na ekranie
        available_rect = self.parent().screen().availableGeometry()
        self.width = available_rect.width()
        self.height = available_rect.height()

        # Ustawienie rozmiaru floty na nowo obliczony
        self.setFixedSize(self.width, self.height)  # Odejmujemy 100 jako margines


    def show_magazyn(self):
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

        if self.filters_set:
            self.add_frame = AddFrame(class_name="WyposazeniePojazdu", api_url=f"{self.api_url}/wyposazenie",
                                      parent=self, header_title="Dodawanie wyposażenia", refresh_callback=self.load_data_filtered)
        else:
            self.add_frame = AddFrame(class_name="WyposazeniePojazdu", api_url=f"{self.api_url}/wyposazenie",
                                  parent=self, header_title="Dodawanie wyposażenia", refresh_callback=self.load_data)
        self.add_frame.show()

        # Po zamknięciu okna dialogowego, przywrócenie interakcji
        self.add_frame.finished.connect(self.remove_overlay)

    def on_table_double_click(self, index):
        # Tworzymy nakładkę, która zablokuje interakcje w FleetFrame
        self.overlay = OverlayWidget(self)
        self.overlay.show()

        row = index.row()
        czesc_id = self.model_pojazd.data(
            self.model_pojazd.index(row, self.primary_key_index_czesc))

            # Wykonanie żądania GET do API, aby pobrać dane kierowcy
        try:
            response = requests.get(f"{self.api_url}/wyposazenie/show/{czesc_id}")
            if response.status_code == 200:
                czesc_data = response.json()
                print(czesc_data)
                # Przekazanie danych do okna edycji
                if self.filters_set:
                    self.edit_frame = EditFrameWyposazenie(class_name="WyposazeniePojazdu", data=czesc_data,
                                                api_url=f"{self.api_url}/wyposazenie",
                                                parent=self, header_title="Edycja wyposażenia",
                                                refresh_callback=self.load_data_filtered)
                else:
                    self.edit_frame = EditFrameWyposazenie(class_name="WyposazeniePojazdu", data=czesc_data,
                                            api_url=f"{self.api_url}/wyposazenie",
                                            parent=self, header_title="Edycja wyposażenia",
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

        # # Ustaw szerokość kolumn kluczy obcych na 0
        # print(f"foreign_keys: {self.foreign_key_index}")
        # if self.foreign_key_index:
        #     for foreign_key in self.foreign_key_index:
        #         print(f"foreign_key: {foreign_key}")
        #         self.tableView_flota.setColumnWidth(foreign_key, 0)

    def load_data(self, nazwa_elementu='', id_typ_serwisu=None, sort_by='', order=''):
        """
        Pobiera dane części z API i wyświetla je w tabeli.
        """
        self.primary_key_index = self.primary_key_index_czesc
        self.tableView_flota.setModel(self.model_pojazd)

        # Przygotowanie parametrów zapytania
        params = {}
        if nazwa_elementu:
            params['nazwaElementu'] = nazwa_elementu
        if id_typ_serwisu:
            params['idTypSerwisu'] = id_typ_serwisu
        if sort_by:
            params['sort_by'] = sort_by
        if order:
            params['order'] = order


        try:
            # Wykonanie żądania HTTP GET do API z parametrami
            # response = requests.get(f"{self.api_url}/czesci?excludeIdTypSerwisu=4", params=params)
            response = requests.get(f"{self.api_url}/wyposazenie/show/all", params=params)

            if response.status_code == 200:
                czesci_data = response.json()  # Pobranie danych w formacie JSON

                # Czyszczenie poprzednich danych
                self.model_pojazd.removeRows(0, self.model_pojazd.rowCount())

                for wyposazeniepojazdu in czesci_data:
                    self.model_pojazd.appendRow([
                        QStandardItem(str(wyposazeniepojazdu['ID Wyposażenia Pojazdu'])),
                        QStandardItem(str(wyposazeniepojazdu['Pojazd'])),  # Zmieniono na 'Pojazd'
                        QStandardItem(str(wyposazeniepojazdu['Opis'])),
                        QStandardItem(str(wyposazeniepojazdu['Ilość']))
                    ])
            else:
                QMessageBox.warning(self, "Błąd API",
                                    f"Nie udało się pobrać danych części. Kod błędu: {response.status_code}")
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Wystąpił błąd podczas połączenia z API: {str(e)}")

        # Użycie QTimer dla opóźnienia wywołania adjust_column_widths
        QTimer.singleShot(0, self.adjust_column_widths)

    def get_column_headers(model_class):
        """Pobiera dane o kolumnach z modelu."""
        mapper = inspect(model_class)
        columns_info = []

        for column in mapper.columns:
            columns_info.append({
                "name": column.name,
                "friendly_name": model_class.COLUMN_NAME_MAP.get(column.name, column.name),
                "primary_key": column.primary_key,
                "nullable": column.nullable,
                "type": str(column.type)
            })

        return columns_info


    ########################################################################################################
    ########################################################################################################
    ########################################################################################################
    ########################################################################################################

    #tutaj beda filtry
    def show_filter_dialog(self):
        """
        Wyświetla okno dialogowe filtrów i przekazuje dane do funkcji filtrującej.
        """

        self.overlay = OverlayWidget(self)
        self.overlay.show()

        # Jeśli filter_dialog już istnieje, upewniamy się, że jest na wierzchu
        if hasattr(self, 'filter_dialog') and self.filter_dialog is not None:
            self.filter_dialog.raise_()  # Podnosimy istniejące okno na wierzch
            self.filter_dialog.activateWindow()  # Ustawiamy fokus na okno dialogowe

        if self.filters_set == False:
            # Tworzymy nowy dialog tylko jeśli nie istnieje lub flaga wskazuje na brak ustawionych filtrów
            self.filter_dialog = FilterFrameMagazine(
                class_name="WyposazeniePojazdu",
                api_url=f"{self.api_url}/wyposazenie",
                parent=self,
                header_title="Filtrowanie wyposażenia",
                # Przekazujemy istniejące filtry
                refresh_callback=self.load_data_filtered
            )
            # Pokazujemy istniejący dialog (nowy lub już wcześniej utworzony)
        self.filter_dialog.show()
        # Po zamknięciu okna dialogowego, przywrócenie interakcji
        self.filter_dialog.finished.connect(self.remove_overlay)

    def load_data_filtered(self, filtr_parameteres_czesci=None, sort_by='', order=''):
        # Jeżeli filtry zostały przekazane, ustawiamy je lokalnie
        if filtr_parameteres_czesci is not None:
            self.filtr_parameteres_czesci = filtr_parameteres_czesci
            self.filters_set = True

        print("Wywołano load_data_filtered z filtrami:", self.filtr_parameteres_czesci)

        sort_parameters = {
            'sort_by': self.sort_parameteres_czesci_sort_by,
            'order': self.sort_parameteres_czesci_order
        }

        # Łączenie filtrów z sortowaniem
        combined_parameters = {**self.filtr_parameteres_czesci, **sort_parameters}
        print(f"Combined_param: {combined_parameters}")

        # Przekonwertowanie kluczy na małe litery
        combined_parameters_lower = {key.lower(): value for key, value in combined_parameters.items() if
                                     value is not None}
        print(f"Final Combined_param (with lowercase keys): {combined_parameters_lower}")

        # Dodanie sort_by i order do combined_parameters jeśli są przekazane
        if sort_by:
            combined_parameters['sort_by'] = sort_by
        if order:
            combined_parameters['order'] = order


        # Usuń 'Dane kierowcy' z parametrów, aby nie pojawił się w URL
        if 'pojazd' in combined_parameters_lower:
            combined_parameters_lower.pop('pojazd')

        # Jeśli 'numer rejestracyjny' jest obecny, zmień na 'nrRejestracyjny'
        if 'id pojazdu' in combined_parameters_lower:
            combined_parameters_lower['idPojazd'] = combined_parameters_lower.pop('id pojazdu')

        query_string = '&'.join([f"{key}={value}" for key, value in combined_parameters_lower.items()])
        full_url = f"{self.api_url}/wyposazenie/show/all?{query_string}&"
        print(f"Final URL: {full_url}")

        try:
            # Wykonanie żądania HTTP GET do API z parametrami
            response = requests.get(full_url)
            if response.status_code == 200:
                czesci_data = response.json()  # Pobranie danych w formacie JSON

                # Czyszczenie poprzednich danych
                self.model_pojazd.removeRows(0, self.model_pojazd.rowCount())

                for wyposazeniepojazdu in czesci_data:
                    self.model_pojazd.appendRow([
                        QStandardItem(str(wyposazeniepojazdu['ID Wyposażenia Pojazdu'])),
                        QStandardItem(str(wyposazeniepojazdu['Pojazd'])),
                        QStandardItem(str(wyposazeniepojazdu['Opis'])),
                        QStandardItem(str(wyposazeniepojazdu['Ilość']))
                    ])
            else:
                QMessageBox.warning(self, "Błąd API",
                                    f"Nie udało się pobrać danych części. Kod błędu: {response.status_code}")
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Wystąpił błąd podczas połączenia z API: {str(e)}")

            # Użycie QTimer dla opóźnienia wywołania adjust_column_widths
        QTimer.singleShot(0, self.adjust_column_widths)

    def show_raport_frame(self):
        """
        Wyświetla ramkę do wyboru folderu i nazwy pliku.
        """
        # Tworzymy nakładkę, która zablokuje interakcje w FleetFrame
        self.overlay = OverlayWidget(self)
        self.overlay.show()

        self.raport_dialog = RaportFrame(parent=self, save_callback=self.generate_raport, header_title="Raport wyposażenia")
        self.raport_dialog.show()

        # Po zamknięciu okna dialogowego, przywrócenie interakcji
        self.raport_dialog.finished.connect(self.remove_overlay)

    def generate_raport(self, pdf_file):
        self.remove_overlay()

        # Upewnij się, że ścieżka katalogu istnieje
        output_dir = os.path.dirname(pdf_file)
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except Exception as e:
                QMessageBox.critical(self, "Błąd", f"Nie udało się utworzyć katalogu: {str(e)}")
                return

        # Ścieżka do czcionki
        font_path = "./frontend/fonts/dejavu-sans-ttf-2.37/ttf/DejaVuSans.ttf"

        try:
            # Rejestracja czcionki
            pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nie udało się załadować czcionki: {str(e)}")
            return

        try:
            # Utwórz dokument PDF
            pdf = canvas.Canvas(pdf_file, pagesize=A4)
            pdf.setTitle("Raport Wyposażenia pojazdu")

            # Aktualna data i godzina
            current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            def draw_header():
                """Rysowanie nagłówka z datą i godziną."""
                pdf.setFont("DejaVuSans", 6)  # Zmniejszona czcionka nagłówka strony
                pdf.drawRightString(550, 830, current_datetime)  # Pozycja: prawy górny róg

            # Ustawienie czcionki na DejaVuSans
            pdf.setFont("DejaVuSans", 16)  # Tytuł raportu, nieco mniejsza czcionka
            pdf.drawString(50, 800, "Raport Cześci")
            pdf.setFont("DejaVuSans", 8)  # Ogólny tekst

            draw_header()  # Rysowanie nagłówka na pierwszej stronie

            # Przygotowanie nagłówków tabeli
            headers = ["Nr", "Pojazd", "Opis", "Ilość"]
            column_widths = [30, 140, 200, 60]  # Poprawiona szerokość kolumn

            column_spacing = 35  # Dodaj odstęp między kolumnami

            # Oblicz przesunięcia X kolumn, uwzględniając odstępy
            x_offsets = [50]  # Start od X=50
            for width in column_widths[:-1]:
                x_offsets.append(x_offsets[-1] + width + column_spacing)

            y_position = 750  # Pozycja Y początkowa
            line_height = 12  # Zmniejszona wysokość wierszy

            # Dodaj nagłówki do tabeli
            pdf.setFont("DejaVuSans", 10)  # Zmniejszona czcionka nagłówków tabeli
            for i, header in enumerate(headers):
                pdf.drawString(x_offsets[i], y_position, header)
            y_position -= line_height

            # Dodaj dane do tabeli
            pdf.setFont("DejaVuSans", 6)  # Zmniejszona czcionka danych tabeli
            for row in range(self.model_pojazd.rowCount()):
                # Numer wiersza
                row_number = str(row + 1)

                # Pobierz dane z modelu
                typ_serwisu = self.model_pojazd.item(row, 1).text()
                nazwa_elementu = self.model_pojazd.item(row, 2).text()
                ilosc = self.model_pojazd.item(row, 3).text()

                # Podziel zawartość kolumn na linie, jeśli tekst jest za długi
                wrapped_data = [
                    [row_number],  # Numer wiersza nie wymaga łamania tekstu
                    textwrap.wrap(typ_serwisu, width=int(column_widths[1] / 5)),
                    textwrap.wrap(nazwa_elementu, width=int(column_widths[2] / 5)),
                    textwrap.wrap(ilosc, width=int(column_widths[3] / 5))
                ]

                # Oblicz maksymalną liczbę linii w tym wierszu
                max_lines = max(len(data) for data in wrapped_data)
                row_height = line_height * max_lines

                # Sprawdź miejsce na stronie
                if y_position - row_height < 50:
                    pdf.showPage()
                    draw_header()  # Nagłówek na nowej stronie
                    y_position = 800
                    pdf.setFont("DejaVuSans", 6)  # Zmniejszona czcionka nagłówków
                    for i, header in enumerate(headers):
                        pdf.drawString(x_offsets[i], y_position, header)
                    y_position -= line_height
                    pdf.setFont("DejaVuSans", 6)

                # Rysuj dane w tabeli
                for line_idx in range(max_lines):
                    for col_idx, data in enumerate(wrapped_data):
                        if line_idx < len(data):
                            pdf.drawString(x_offsets[col_idx], y_position, data[line_idx])
                    y_position -= line_height

            # Zapisz plik PDF
            pdf.save()

            QMessageBox.information(self, "Sukces", f"Raport został wygenerowany i zapisany jako {pdf_file}")

        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nie udało się wygenerować raportu: {str(e)}")

    def remove_overlay(self):
        """
        Usuwa nakładkę, jeśli istnieje.
        """

        self.overlay.deleteLater()
