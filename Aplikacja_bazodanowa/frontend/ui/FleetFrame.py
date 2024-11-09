from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QTableView, QHeaderView, QAbstractItemView, QLineEdit, QButtonGroup, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon  # Poprawny import
from PyQt5.QtCore import Qt
from Aplikacja_bazodanowa.frontend.ui.EditFrame import EditFrame
from Aplikacja_bazodanowa.frontend.ui.AddFrame import AddFrame
from Aplikacja_bazodanowa.backend.models import Kierowca, Pojazd

from enum import Enum, auto
import requests

class ScreenType(Enum):
    CIAGNIKI = 1
    NACZEPY = 2
    KIEROWCY = 3


class FleetFrame(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(FleetFrame, self).__init__(parent)

        # początkowy ekran floty
        self.screen_type = ScreenType.CIAGNIKI

        # Ustawienie rozmiaru floty
        self.width = 0
        self.height = 0
        available_rect = self.parent().screen().availableGeometry()
        self.width = available_rect.width()
        self.height = available_rect.height()
        self.setFixedSize(self.width, self.height)

        self.setup_fleet()  # Ustawienie ramki flot
        self.hide()

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

        # Tworzenie modelu danych
        self.model_pojazd = QStandardItemModel()
        self.model_pojazd.setHorizontalHeaderLabels(['ID', 'Nazwa', 'Typ', 'Status', 'data', 'kierowca'])

        self.model_kierowca = QStandardItemModel()
        self.model_kierowca.setHorizontalHeaderLabels(['ID', 'Imię', 'Nazwisko', 'Nr telefonu'])

        # Dodawanie przykładowych danych
        for i in range(25):
            self.model_pojazd.appendRow([QStandardItem(str(i + 1)),
                                           QStandardItem("Ciągnik A"),
                                           QStandardItem("Transport"),
                                           QStandardItem("Aktywny"),
                                           QStandardItem("kiedys"),
                                           QStandardItem("kierowca jannek mega kot")])

        # Tworzenie QScrollArea
        table_fleet_width = self.width-500
        table_fleet_height = self.height - 50 - 150 - 100
        table_fleet_side_margin = int(self.width/2-table_fleet_width/2)
        table_fleet_top_margin = 150

        self.scroll_area = QtWidgets.QScrollArea(self)
        self.scroll_area.setGeometry(QtCore.QRect(
            table_fleet_side_margin, table_fleet_top_margin, table_fleet_width, table_fleet_height))
        self.scroll_area.setWidgetResizable(False)  # Rozciąganie zawartości
        self.scroll_area.setStyleSheet("""
            QAbstractScrollArea { 
                background-color: transparent; 
            }
            QAbstractScrollArea::corner { 
                background-color: transparent; 
            }
            
            /* Styl dla pionowego paska przewijania */
            QScrollBar:vertical {
                border: 2px solid #accccb;
                background: #b9dcdb;
                width: 30px;
                margin: 78px 0px 37px 5px; /* top right bottom left */
            }
            QScrollBar::handle:vertical {
                background: #b9dcdb;
                border: 1px solid #accccb;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {     /* Przewijanie */
                background: #accccb; 
                height: 30px; 
                width: 25px; 
                border-radius: 8px; 
            }
            QScrollBar::add-line:vertical {     /* Przewijanie w dół */
                subcontrol-origin: margin; 
                subcontrol-position: bottom; 
                margin: 0px 0px 5px 5px; /* top right bottom left */
            }
            QScrollBar::sub-line:vertical {     /* Przewijanie w górę */
                subcontrol-origin: margin; 
                subcontrol-position: top; 
                margin: 46px 0px 0px 5px; /* top right bottom left */
            }

            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                background: transparent; 
                width: 19px; 
                height: 30px; /* Ustaw wysokość strzałek */
                border-radius: 8px;
            }

            QScrollBar::up-arrow:vertical {
                image: url(icons/angle-up.png);                 
                subcontrol-origin: margin; 
                subcontrol-position: top; 
                margin: 46px 3px 0px 8px; /* top right bottom left */
            }
            QScrollBar::down-arrow:vertical {
                image: url(icons/angle-down.png);                 
                subcontrol-origin: margin; 
                subcontrol-position: bottom; 
                margin: 0px 3px 5px 8px; /* top right bottom left */
            }
            
            /* Styl dla poziomego paska przewijania */
            QScrollBar:horizontal  {
                border: 2px solid #accccb;
                background: #b9dcdb;
                height: 30px;
                margin: 5px 37px 0px 78px; /* top right bottom left */
            }
            QScrollBar::handle:horizontal {
                background: #b9dcdb;
                border: 1px solid #accccb;
                min-width: 20px;              
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                background: #accccb; 
                height: 25px;
                width: 30px; 
                border-radius: 8px; 
            }
            QScrollBar::add-line:horizontal {
                subcontrol-origin: margin; 
                subcontrol-position: right; 
                margin: 5px 5px 0px 0px;  /* top right bottom left */
            }
            QScrollBar::sub-line:horizontal {
                subcontrol-origin: margin; 
                subcontrol-position: left; 
                margin: 5px 0px 0px 46px; /* top right bottom left */
            }
            QScrollBar::left-arrow:horizontal, QScrollBar::right-arrow:horizontal {
                background: transparent; 
                width: 30px; 
                height: 19px;
                border-radius: 8px;
            }
            QScrollBar::left-arrow:horizontal {
                image: url(icons/angle-left.png);
                subcontrol-origin: margin;
                subcontrol-position: left;
                margin: 8px 0px 3px 46px; /* top right bottom left */
            }
            QScrollBar::right-arrow:horizontal {
                image: url(icons/angle-right.png);
                subcontrol-origin: margin;
                subcontrol-position: right;
                margin: 8px 5px 3px 0px; /* top right bottom left */
            }
        """)
        self.scroll_area.viewport().update()

        # Ustawienie tabeli
        self.tableView_flota = QTableView(self.scroll_area)
        self.tableView_flota.setGeometry(QtCore.QRect(0, 0, table_fleet_width, table_fleet_height))
        self.tableView_flota.setStyleSheet("""
                                        QTableView {    /* Cała tabela */
                                            border: 2px solid #accccb;
                                            border-radius: 15px;
                                            background-color: #dff0ef;
                                            gridline-color: transparent;
                                            alternate-background-color: #dff0ef; /* Kolor tła dla co drugiego wiersza */                                            
                                            padding: 0px 5px 5px 0px;  /* Dodanie marginesu dolnego (15px) */
                                        }
                                        QTableView::item {    /* Element tabeli */
                                            border: 1px solid #accccb;
                                            border-radius: 10px;
                                            background-color: #caf0ef;
                                            padding: 5px;
                                            margin: 2px;
                                            text-align: left;   
                                        }
                                        
                                        QTableView::item:alternate {    /* Element altenatywny tabeli */
                                            background-color: #c0e1e2; /* Kolor co drugiego wiersza */
                                            border-radius: 10px;
                                        }
                                        QTableView::item:selected {    /* Element tabeli - wybrany rząd */
                                            background-color: #82b3ba;
                                            color: white;
                                            border: 2px solid #accccb;
                                        }
                                        QTableView::item:selected:focus {   /* Element tabeli - wybrany element */
                                            background-color: #92c9d1;
                                            outline: none; /* Usunięcie ramki focusa */
                                            border: 2px solid #7baab0; /* Ramka dla aktywnego elementu */
                                        }
                                        QTableView::item:hover {    /* Element tabeli - po najechnaiu na niego */
                                            background-color: #8dc2ca;
                                            border: 2px solid #accccb;
                                        }
                                        QAbstractItemView:focus{
                                            outline: none;
                                        }
                                        QHeaderView {   /* Tło nagłówków */
                                            background-color: #dff0ef; /* Kolor tła dla całego nagłówka */
                                        }
                                        QHeaderView::section {   /* Nagłówki */
                                            background-color: #b9dcdb; /* Półprzezroczyste */
                                            color: #5d5d5d;
                                            border-radius: 10px; 
                                            padding: 4px;
                                            border: 2px solid #accccb;
                                            margin: 2px;
                                            text-align: center;
                                        }
                                        QTableCornerButton::section {   /* Lewy górny narożnik */
                                            background-color: transparent; /* Kolor tła w rogu */
                                            border-radius: 10px; /* Zmniejszyłem na 10px */
                                            border: none; /* Obramowanie w rogu */
                                        }
                                    """)

        self.tableView_flota.setObjectName("tableView_flota")
        self.tableView_flota.setModel(self.model_kierowca)
        self.tableView_flota.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableView_flota.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableView_flota.setAlternatingRowColors(True)
        self.tableView_flota.resizeColumnsToContents()
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

        # Dodanie naddatku do każdej kolumny
        additional_width = 20  # naddatek w pikselach dla każdej kolumny
        for i in range(self.tableView_flota.model().columnCount()):
            original_width = self.tableView_flota.columnWidth(i)
            self.tableView_flota.setColumnWidth(i, original_width + additional_width)

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
        self.widget_choice_buttons.setGeometry(QtCore.QRect(int(self.width/2-800/2), 70, 800, 60))
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

        # Podłączenie sygnału dla grupy przycisków
        self.button_group.buttonClicked[int].connect(self.update_screen_type)

        # Ustawienie stylów przycisków i początkowego stanu
        self.button_flota_kierowcy.setChecked(True)
        self.update_screen_type(ScreenType.KIEROWCY.value)  # Ustawienie początkowej wartości zmiennej


    def update_screen_type(self, screen_value):
        # Zmiana wartości zmiennej na podstawie ID przycisku
        self.screen_type = ScreenType(screen_value)
        print(f"Aktualna wartość zmiennej: {self.screen_type.name}")
        self.load_data()


    def on_table_double_click(self, index):
        row = index.row()  # Indeks wiersza
        # Utworzenie nowego obiektu EditFrame
        self.edit_frame = EditFrame(self.model_kierowca, row, self, "Edycja floty")
        self.edit_frame.show()

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


    def load_data(self):
        # API URL - endpoint, który zwraca listę kierowców
        if self.screen_type == ScreenType.KIEROWCY:
            self.tableView_flota.setModel(self.model_kierowca)
            url = "http://127.0.0.1:5000/kierowcy"
            try:
                # Wykonanie żądania HTTP GET do API
                response = requests.get(url)
                if response.status_code == 200:
                    kierowcy_data = response.json()  # Pobranie danych w formacie JSON

                    # Dodanie danych do modelu
                    self.model_kierowca.removeRows(0, self.model_kierowca.rowCount())  # Usuwamy poprzednie dane z modelu
                    for kierowca in kierowcy_data:
                        self.model_kierowca.appendRow([QStandardItem(str(kierowca['id'])),
                                              QStandardItem(kierowca['imie']),
                                              QStandardItem(kierowca['nazwisko']),
                                              QStandardItem(kierowca['nrTel'])])
                else:
                    print(f"Błąd API: {response.status_code}")
            except Exception as e:
                print(f"Błąd przy ładowaniu danych: {str(e)}")
        elif self.screen_type == ScreenType.CIAGNIKI:
            self.tableView_flota.setModel(self.model_pojazd)

    def add_new_line(self):
        if self.screen_type == ScreenType.KIEROWCY:
            self.add_frame = AddFrame(model_class=Kierowca, api_url= "http://127.0.0.1:5000/kierowca",
                                      parent= self, header_title="Dodawanie kierowcy", )
            # self.add_frame = AddFrame(model_class=Kierowca,
            #                           parent= self, header_title="Dodawanie kierowcy", )
            self.add_frame.show()
        # else:
        #     self.add_frame = AddFrame(model_class=Pojzad, api_url= "http://127.0.0.1:5000/api/pojazdy", header_title="Dodawanie pojazdu", )
        #     self.add_frame.show()