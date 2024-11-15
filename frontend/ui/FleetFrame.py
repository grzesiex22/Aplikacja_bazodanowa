from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QTableView, QHeaderView, QAbstractItemView, QLineEdit, QButtonGroup, QVBoxLayout, QHBoxLayout, QMessageBox
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon, QFont  # Poprawny import
from PyQt5.QtCore import Qt, QTimer
from Aplikacja_bazodanowa.frontend.ui.EditFrame import EditFrame
from Aplikacja_bazodanowa.frontend.ui.AddFrame import AddFrame
from Aplikacja_bazodanowa.frontend.ui.FilterFleetFrame import FilterFleetFrame
from Aplikacja_bazodanowa.backend.models import TypPojazdu
import os
from enum import Enum, auto
import requests


class ScreenType(Enum):
    CIAGNIKI = 1
    NACZEPY = 2
    KIEROWCY = 3


class FleetFrame(QtWidgets.QFrame):
    def __init__(self, parent=None, api_url=None):
        super(FleetFrame, self).__init__(parent)

        # Inicjalizacja
        self.screen_type = ScreenType.CIAGNIKI
        self.api_url = api_url

        # Inicjalizacja flagi
        self.is_filtering = False

        # Informacje dla tabeli pojazdy
        self.model_pojazd = QStandardItemModel()
        self.model_pojazd_columns_info, self.primary_key_index_pojazd, self.foreign_key_index_pojazd \
            = self.load_column_headers("pojazd", model=self.model_pojazd)
        self.sort_parameteres_pojazd = {}  # przechowuje aktualne parametry sortowania pojazdu
        self.filtr_parameteres_pojazd = {}  # przechowuje aktualne parametry sortowania pojazdu
        self.current_sorted_column_pojazd = None  # potrzebne do zmiany sortowania asc/desc

        # Informacje dla tabeli kierowcy
        self.model_kierowca = QStandardItemModel()
        self.model_kierowca_columns_info, self.primary_key_index_kierowca, self.foreign_key_index_kierowca \
            = self.load_column_headers("kierowca", model=self.model_kierowca)
        self.sort_parameteres_kierowca = {}  # przechowuje aktualne parametry sortowania kierowcy
        self.filtr_parameteres_pojazd['Typ pojazdu'] = TypPojazdu.Ciągnik.value   # przechowuje aktualne parametry sortowania pojazdu
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
        self.widget_flota_header = QtWidgets.QWidget(self)
        self.widget_flota_header.setGeometry(QtCore.QRect(0, 0, self.width, 50))
        self.widget_flota_header.setStyleSheet("QWidget {"
                                                "    background-color: #accccb;"
                                                "    border: 0px solid #e67e22;"
                                                "    border-radius: 15px;"
                                                "}"
                                               "QLabel {"
                                               "    color: #5d5d5d;  /* Kolor tekstu dla etykiet */"
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
        self.label_flota_header.setText("Flota")

        self.button_exit_flota = QtWidgets.QPushButton(self.widget_flota_header)
        self.button_exit_flota.setGeometry(QtCore.QRect(self.width-40-10, 5, 40, 40))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icons/undo_white.png"), QIcon.Normal, QIcon.Off)
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
        Przyciski
        """
        self.button_flota_dodaj = QtWidgets.QPushButton(self)
        self.button_flota_dodaj.setGeometry(QtCore.QRect(
            int(table_fleet_side_margin + table_fleet_width / 2 - 500 / 2),
            table_fleet_top_margin + table_fleet_height + 20, 500, 60))
        self.button_flota_dodaj.setText("DODAJ")
        self.button_flota_dodaj.setStyleSheet("QPushButton {"
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
        self.button_flota_dodaj.setObjectName("button_flota_dodaj")
        self.button_flota_dodaj.clicked.connect(self.add_new_line)


        self.widget_choice_buttons = QtWidgets.QWidget(self)
        self.widget_choice_buttons.setGeometry(QtCore.QRect(int(self.width/2-1000/2), 70, 1000, 60))
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
        icon.addPixmap(QtGui.QPixmap("icons/filter_white.png"), QIcon.Normal, QIcon.Off)
        self.button_filtruj.setCheckable(False)  # Opcjonalnie, jeśli ma być przyciskiem przełączającym
        self.button_filtruj.setIcon(icon)
        self.button_filtruj.setIconSize(QtCore.QSize(30, 30))

        self.horizontalLayout_buttons.addWidget(self.button_filtruj)
        self.button_filtruj.clicked.connect(self.show_filter_dialog)

        # Ustawienie stylu dla przycisku button_filtruj
        self.button_filtruj.setStyleSheet("""
                    QPushButton {
                        color: #5d5d5d;
                        background-color: #D8B7DD; /* Złoty kolor */
                        border: 2px solid #5d5d5d;
                        border-radius: 15px;
                        padding: 5px;
                        font-size: 20px;
                        font-family: Arial, sans-serif;
                    }
                    QPushButton:hover {
                        background-color: #E1C6EB;
                    }
                    QPushButton:pressed {
                        background-color: #C8A1D1;
                    }
                """)

        ######przycisk wyczyść filtry####################
        # Tworzenie przycisku button_filtruj
        self.button_wyczysc_filtry = QtWidgets.QPushButton(self.widget_choice_buttons)
        self.button_wyczysc_filtry.setFixedWidth(70)
        self.button_wyczysc_filtry.setObjectName("button_wyczysc_filtry")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icons/clear_filter_white.png"), QIcon.Normal, QIcon.Off)
        self.button_wyczysc_filtry.setCheckable(False)  # Opcjonalnie, jeśli ma być przyciskiem przełączającym
        self.button_wyczysc_filtry.setIcon(icon)
        self.button_wyczysc_filtry.setIconSize(QtCore.QSize(30, 30))
        self.horizontalLayout_buttons.addWidget(self.button_wyczysc_filtry)

        self.button_wyczysc_filtry.clicked.connect(self.erase_filters)

        # Ustawienie stylu dla przycisku button_wyczysc_filtry
        self.button_wyczysc_filtry.setStyleSheet("""
                        QPushButton {
                        color: #5d5d5d;
                        background-color: #D8B7DD; /* Złoty kolor */
                        border: 2px solid #5d5d5d;
                        border-radius: 15px;
                        padding: 5px;
                        font-size: 20px;
                        font-family: Arial, sans-serif;
                    }
                    QPushButton:hover {
                        background-color: #E1C6EB;
                    }
                    QPushButton:pressed {
                        background-color: #C8A1D1;
                    }
                """)

        # Podłączenie sygnału dla grupy przycisków
        self.button_group.buttonClicked[int].connect(self.update_screen_type)

        # Ustawienie stylów przycisków i początkowego stanu
        self.button_flota_ciagniki.setChecked(True)
        self.update_screen_type(ScreenType.CIAGNIKI.value)  # Ustawienie początkowej wartości zmiennej

    def erase_filters(self):
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
        # self.highlight_sorted_column(column_index, 'asc')


    def update_screen_type(self, screen_value):
        # Zmiana wartości zmiennej na podstawie ID przycisku
        self.screen_type = ScreenType(screen_value)
        print(f"Aktualna wartość zmiennej: {self.screen_type.name}")

        self.is_filtering = False

        if self.screen_type == ScreenType.KIEROWCY:
            self.button_filtruj.setVisible(False)
            self.button_wyczysc_filtry.setVisible(False)
            print("schowałem filtruj")
        else:
            self.button_filtruj.setVisible(True)
            self.button_wyczysc_filtry.setVisible(True)

        self.load_data()


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
        if self.screen_type == ScreenType.KIEROWCY:
            self.add_frame = AddFrame(class_name="kierowca", api_url=f"{self.api_url}/kierowca",
                                      parent=self, header_title="Dodawanie kierowcy", refresh_callback=self.load_data)
            self.add_frame.show()
        else:
            self.add_frame = AddFrame(class_name="pojazd", api_url=f"{self.api_url}/pojazd",
                                      parent=self, header_title="Dodawanie pojazdu", refresh_callback=self.load_data)
            self.add_frame.show()


    def on_table_double_click(self, index):
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

        if self.screen_type == ScreenType.KIEROWCY:
            self.primary_key_index = self.primary_key_index_kierowca
            self.foreign_key_index = self.foreign_key_index_kierowca
            self.tableView_flota.setModel(self.model_kierowca)

            try:
                # Wykonanie żądania HTTP GET do API
                response = requests.get(f"{self.api_url}/kierowca/show", params=self.sort_parameteres_kierowca)
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

            self.filtr_parameteres_pojazd['typPojazdu'] = TypPojazdu.Ciągnik.value
            combined_parameters = {**self.filtr_parameteres_pojazd, **self.sort_parameteres_pojazd}
            print(f"Combined_param: {combined_parameters}")

            try:
                # Wykonanie żądania HTTP GET do API
                response = requests.get(f"{self.api_url}/pojazd/show", params=combined_parameters)
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
            self.tableView_flota.setModel(self.model_pojazd)

            self.filtr_parameteres_pojazd['typPojazdu'] = TypPojazdu.Naczepa.value
            combined_parameters = {**self.filtr_parameteres_pojazd, **self.sort_parameteres_pojazd}
            print(f"Combined_param: {combined_parameters}")

            try:
                # Wykonanie żądania HTTP GET do API
                response = requests.get(f"{self.api_url}/pojazd/show", params=combined_parameters)
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


    #########################################################################################################
    ########################################################################################################
    ########################################################################################################
    ########################################################################################################

    #tutaj beda filtry
    def show_filter_dialog(self):
        """
        Wyświetla okno dialogowe filtrów i przekazuje dane do funkcji filtrującej.
        """
        # Przekazujemy referencję do funkcji filtrujFlote jako callback
        self.filter_dialog = FilterFleetFrame(class_name="pojazd", api_url=f"{self.api_url}/pojazd",
                                               parent=self, header_title="Filtrowanie pojazdów",
                                               refresh_callback=self.load_data_filtered)

        self.filter_dialog.show()

    def load_data_filtered(self, filtr_parameteres_pojazd=None):
        # Jeżeli filtry zostały przekazane, ustawiamy je lokalnie
        if filtr_parameteres_pojazd is not None:
            self.filtr_parameteres_pojazd = filtr_parameteres_pojazd

        print("Wywołano load_data_filtered z filtrami:", self.filtr_parameteres_pojazd)

        # Ustawienie domyślnych filtrów
        default_filters = {
            'Typ Pojazdu': None,
            'marka': None,
            'model': None,
            'nrRejestracyjny': None,
            'dodatkoweInf': None
        }

        # Łączenie filtrów z domyślnymi, aby zapewnić, że odpowiednie filtry zawsze będą w zapytaniu
        combined_parameters = {**default_filters, **self.filtr_parameteres_pojazd, **self.sort_parameteres_pojazd}
        print(f"Combined_param: {combined_parameters}")

        # Przekonwertowanie kluczy na małe litery
        combined_parameters_lower = {key.lower(): value for key, value in combined_parameters.items() if
                                     value is not None}
        print(f"Final Combined_param (with lowercase keys): {combined_parameters_lower}")

        # Usuń 'Dane kierowcy' z parametrów, aby nie pojawił się w URL
        if 'dane kierowcy' in combined_parameters_lower:
            combined_parameters_lower.pop('dane kierowcy')

        # Jeśli 'numer rejestracyjny' jest obecny, zmień na 'nrRejestracyjny'
        if 'numer rejestracyjny' in combined_parameters_lower:
            combined_parameters_lower['nrRejestracyjny'] = combined_parameters_lower.pop('numer rejestracyjny')

        # Jeśli 'numer rejestracyjny' jest obecny, zmień na 'nrRejestracyjny'
        if 'dodatkowe informacje' in combined_parameters_lower:
            combined_parameters_lower['dodatkoweInf'] = combined_parameters_lower.pop('dodatkowe informacje')

        if 'id kierowca' in combined_parameters_lower:
            combined_parameters_lower['idKierowca'] = combined_parameters_lower.pop('id kierowca')

        if self.screen_type == ScreenType.CIAGNIKI:
            # Budowanie URL z parametrami w wymaganym formacie
            query_string = '&'.join([f"{key}={value}" for key, value in combined_parameters_lower.items()])
            full_url = f"{self.api_url}/pojazd/show?typPojazdu=Ciągnik&{query_string}"
            print(f"Final URL: {full_url}")

        if self.screen_type == ScreenType.NACZEPY:
            # Budowanie URL z parametrami w wymaganym formacie
            query_string = '&'.join([f"{key}={value}" for key, value in combined_parameters_lower.items()])
            full_url = f"{self.api_url}/pojazd/show?typPojazdu=Naczepa&{query_string}"
            print(f"Final URL: {full_url}")

        try:
            # Wykonanie żądania HTTP GET z pełnym URL
            response = requests.get(full_url)
            if response.status_code == 200:
                pojazd_data = response.json()

                # Aktualizacja modelu pojazdów na podstawie danych z API
                self.model_pojazd.removeRows(0, self.model_pojazd.rowCount())
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

        # Ustawienie opóźnienia dla adjust_column_widths
        QTimer.singleShot(0, self.adjust_column_widths)

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
