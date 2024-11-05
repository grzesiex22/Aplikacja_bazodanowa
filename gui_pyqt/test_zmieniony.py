# -*- coding: utf-8 -*-

# Importowanie niezbędnych modułów z PyQt5
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QPoint, QPropertyAnimation
from PyQt5.QtWidgets import QTableView, QHeaderView, QAbstractItemView, QMessageBox
from PyQt5.QtGui import QStandardItemModel, QStandardItem  # Poprawny import
import sys

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        # Konfiguracja głównego okna
        MainWindow.setObjectName("MainWindow")
        MainWindow.setEnabled(True)
        MainWindow.resize(800, 950)

        # Ustawienie palety kolorów
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(131, 165, 240))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        MainWindow.setPalette(palette)

        # Ustawienie głównego widgetu
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.centralwidget.setFont(font)
        self.centralwidget.setAcceptDrops(False)
        self.centralwidget.setObjectName("centralwidget")

        # Tworzenie ramki głównej
        self.frame_main = QtWidgets.QFrame(self.centralwidget)
        self.frame_main.setGeometry(QtCore.QRect(0, 50, 800, 930))
        self.frame_main.setStyleSheet("QFrame {"
                                       "    background-color: #e4eeff; /* Kolor tła prostokąta */"
                                       "    color: rgb(228, 238, 255);"
                                       "    border: 0px solid #e67e22; /* Obramowanie prostokąta */"
                                       "    border-radius: 15px; /* Zaokrąglone rogi prostokąta */"
                                       "}")
        self.frame_main.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_main.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_main.setObjectName("frame_main")

        # Tworzenie widgetu przycisków
        self.widget_buttons = QtWidgets.QWidget(self.frame_main)
        self.widget_buttons.setGeometry(QtCore.QRect(250, 250, 300, 400))
        self.widget_buttons.setStyleSheet("QPushButton {"
                                           "    background-color: #3498db;  /* Kolor tła */"
                                           "    color: white;  /* Kolor tekstu */"
                                           "    border-radius: 10px;  /* Zaokrąlenie rogów */"
                                           "    padding: 10px 20px;  /* Wewnętrzne marginesy */"
                                           "    font-size: 24px;  /* Rozmiar czcionki */"
                                           "    font-family: Arial, sans-serif;  /* Czcionka */"
                                           "    border: 2px solid #2980b9;  /* Obramowanie */"
                                           "}"
                                           "QPushButton:hover {"
                                           "    background-color: #2980b9;  /* Kolor tła po najechaniu */"
                                           "}"
                                           "QPushButton:pressed {"
                                           "    background-color: #1f618d;  /* Kolor tła po kliknięciu */"
                                           "}"
                                           "QPushButton:disabled {"
                                           "    background-color: #bdc3c7;  /* Kolor tła dla nieaktywnych przycisków */"
                                           "    color: #7f8c8d;  /* Kolor tekstu dla nieaktywnych przycisków */"
                                           "  border: 2px solid #95a5a6;  /* Obramowanie dla nieaktywnych przycisków */"
                                           "}")
        self.widget_buttons.setObjectName("widget_buttons")

        # Przyciski
        self.button_flota = QtWidgets.QPushButton(self.widget_buttons)
        self.button_flota.setGeometry(QtCore.QRect(0, 0, 300, 100))
        self.button_flota.setObjectName("button_flota")
        # Połączenie przycisku flota z wywołaniem metody show_flota
        self.button_flota.clicked.connect(self.show_flota)

        self.button_serwis = QtWidgets.QPushButton(self.widget_buttons)
        self.button_serwis.setEnabled(True)
        self.button_serwis.setGeometry(QtCore.QRect(0, 150, 300, 100))
        self.button_serwis.setObjectName("button_serwis")

        self.button_magazyn = QtWidgets.QPushButton(self.widget_buttons)
        self.button_magazyn.setEnabled(True)
        self.button_magazyn.setGeometry(QtCore.QRect(0, 300, 300, 100))
        self.button_magazyn.setObjectName("button_magazyn")

        # Widget daty i czasu
        self.widget_datetime = QtWidgets.QWidget(self.centralwidget)
        self.widget_datetime.setEnabled(True)
        self.widget_datetime.setGeometry(QtCore.QRect(20, 10, 250, 30))
        self.widget_datetime.setStyleSheet("QLabel {"
                                            "    color: #ffffff;  /* Kolor tekstu dla etykiet */"
                                            "    background-color: transparent;  /* Przezroczyste tło dla etykiet */"
                                            "    border: none;  /* Brak ramki dla etykiet */"
                                            "    font-size: 14px;"
                                            "    font-weight: bold;  /* Ustawienie pogrubienia tekstu */"
                                            "}")

        self.widget_datetime.setObjectName("widget_datetime")

        self.label_time = QtWidgets.QLabel(self.widget_datetime)
        self.label_time.setGeometry(QtCore.QRect(140, 0, 100, 30))
        self.label_time.setMaximumSize(QtCore.QSize(150, 40))
        self.label_time.setObjectName("label_time")

        self.label_date = QtWidgets.QLabel(self.widget_datetime)
        self.label_date.setGeometry(QtCore.QRect(0, 0, 100, 30))
        self.label_date.setMaximumSize(QtCore.QSize(150, 40))
        self.label_date.setObjectName("label_date")

        # Linia pionowa
        self.linia_pionowa = QtWidgets.QFrame(self.widget_datetime)
        self.linia_pionowa.setGeometry(QtCore.QRect(110, 0, 3, 30))
        self.linia_pionowa.setStyleSheet("QFrame {"
                                          "    background-color: #ffffff;  /* Kolor linii */"
                                          "    max-width: 1px;  /* Grubość linii */"
                                          "}")
        self.linia_pionowa.setFrameShape(QtWidgets.QFrame.VLine)
        self.linia_pionowa.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.linia_pionowa.setLineWidth(2)
        self.linia_pionowa.setObjectName("linia_pionowa")



        # Tworzenie ramki floty
        self.frame_flota = QtWidgets.QFrame(self.centralwidget)
        self.frame_flota.setEnabled(False)
        self.frame_flota.setGeometry(QtCore.QRect(0, 50, 800, 930))
        self.frame_flota.setStyleSheet("QFrame {"
                                        "    background-color: #caf0ef; /* Kolor tła prostokąta */"
                                        "    border: 0px solid #e67e22; /* Obramowanie prostokąta */"
                                        "    border-radius: 15px; /* Zaokrąglone rogi prostokąta */"
                                        "    font-family: Arial, sans-serif;"
                                        "    font-size: 14px;"
                                        "}"
                                        "QPushButton {"
                                        "    color: #5d5d5d;"
                                        "    background-color: #b9bece; /* Ustawia przezroczyste tło */"
                                        "    border: 2px solid #5d5d5d; /* Ustawia kolor ramki (czarny) */"
                                        "    border-radius: 15px; /* Zaokrąglone rogi ramki */"
                                        "    padding: 5px; /* Wewnętrzne odstępy, opcjonalne */"
                                        "    font-size: 20px;  /* Rozmiar czcionki */"
                                        "    font-family: Arial, sans-serif;  /* Czcionka */"
                                        "}"
                                        "QPushButton:hover {"
                                        "    background-color: #a2a6b4; /* Ustawia kolor tła po najechaniu */"
                                        "}"
                                        "QPushButton:pressed {"
                                        "    background-color: #8a8e9a;  /* Kolor tła po kliknięciu */"
                                        "}"
                                        "QPushButton:disabled {"
                                        "    background-color: #bdc3c7;  /* Kolor tła dla nieaktywnych przycisków */"
                                        "    color: #7f8c8d;  /* Kolor tekstu dla nieaktywnych przycisków */"
                                        "    border: 2px solid #95a5a6;  /* Obramowanie dla nieaktywnych przycisków */"
                                        "}")
        self.frame_flota.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_flota.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_flota.setObjectName("frame_flota")

        # Ustawienie początkowej pozycji ramki floty
        self.frame_flota.move(0, MainWindow.height())  # Ustawienie poniżej ekranu

        # Widget dla tytułu floty
        self.widget_flota_header = QtWidgets.QWidget(self.frame_flota)
        self.widget_flota_header.setGeometry(QtCore.QRect(0, 0, 800, 50))
        self.widget_flota_header.setStyleSheet("QWidget {"
                                   "    background-color: #accccb; /* Kolor tła prostokąta */"
                                   "    border: 0px solid #e67e22; /* Obramowanie prostokąta */"
                                   "    border-radius: 15px; /* Zaokrąglone rogi prostokąta */"
                                   "}"
                                   "QLabel {"
                                   "    color: #5d5d5d;  /* Kolor tekstu dla etykiet */"
                                   "    background-color: transparent;  /* Przezroczyste tło dla etykiet */"
                                   "    border: none;  /* Brak ramki dla etykiet */"
                                   "    font-size: 20px;  /* Rozmiar czcionki */"
                                   "    font-weight: bold;  /* Ustawienie pogrubienia tekstu */"
                                   "}"
                                   "QPushButton {"
                                    "    background-color: transparent;"  # Kolor przycisku
                                    "    border: 2px solid #5d5d5d; /* Ustawia kolor ramki (czarny) */"
                                    "    border-radius: 15px; /* Zaokrąglone rogi ramki */"
                                    "    padding: 5px; /* Wewnętrzne odstępy, opcjonalne */"
                                   "}"
                                    "QPushButton:hover {"
                                    "    background-color: #a2a6b4; /* Ustawia kolor tła po najechaniu */"
                                    "}")

        self.widget_flota_header.setObjectName("widget_flota_header")

        self.label_flota_header = QtWidgets.QLabel(self.widget_flota_header)
        self.label_flota_header.setGeometry(QtCore.QRect(300, 10, 200, 30))
        self.label_flota_header.setAlignment(QtCore.Qt.AlignCenter)
        self.label_flota_header.setObjectName("label_flota_header")

        self.button_exit_flota = QtWidgets.QPushButton(self.widget_flota_header)
        self.button_exit_flota.setGeometry(QtCore.QRect(755, 5, 40, 40))
        self.button_exit_flota.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("undo.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_exit_flota.setIcon(icon)
        self.button_exit_flota.setIconSize(QtCore.QSize(30, 30))
        self.button_exit_flota.setObjectName("button_exit_flota")

        # Tworzenie modelu danych
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['ID', 'Nazwa', 'Typ', 'Status'])  # Nagłówki kolumn

        # Dodawanie przykładowych danych
        self.model.appendRow([QStandardItem("1"),
                              QStandardItem("Samolot A"),
                              QStandardItem("Transport"),
                              QStandardItem("Aktywny")])
        self.model.appendRow([QStandardItem("2"),
                              QStandardItem("Samolot B"),
                              QStandardItem("Transport"),
                              QStandardItem("Nieaktywny")])

        self.tableView_flota = QtWidgets.QTableView(self.frame_flota)
        self.tableView_flota.setGeometry(QtCore.QRect(50, 150, 700, 650))
        self.tableView_flota.setStyleSheet("QTableView {"
                                           "    border: 2px solid #accccb;"
                                           "    border-radius: 15px;"
                                           "    background-color: #dff0ef;"
                                           "    gridline-color: #95a5a6;"
                                           "}"
                                           "QTableView::item {"
                                           "    border-bottom: 1px solid #bdc3c7;"
                                           "    padding: 10px;"
                                           "}"
                                           "QTableView::item:selected {"
                                           "    background-color: #3498db;"
                                           "    color: white;"
                                           "}"
                                           ""
                                           "QTableView::item:hover {"
                                           "    background-color: #2980b9;"
                                           "}")

        self.tableView_flota.setObjectName("tableView_flota")
        # Tworzenie tabeli w oknie
        self.tableView_flota = QtWidgets.QTableView(self.frame_flota)
        self.tableView_flota.setModel(self.model)
        # self.setCentralWidget(self.tableView_flota)
        # Połączenie sygnału kliknięcia w wiersz
        self.tableView_flota.clicked.connect(self.on_row_clicked)

        # Ustawienia nagłówków
        header = self.tableView_flota.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)  # Ustawienie na rozciąganie

        # Ustawienia wyboru
        self.tableView_flota.setSelectionBehavior(QAbstractItemView.SelectRows)  # Wybór całych wierszy
        self.tableView_flota.setEditTriggers(QAbstractItemView.NoEditTriggers)  # Wyłączenie edycji w komórkach
        self.tableView_flota.setAlternatingRowColors(True)  # Alternatywne kolory wierszy

        self.button_flota_ciagniki = QtWidgets.QPushButton(self.frame_flota)
        self.button_flota_ciagniki.setGeometry(QtCore.QRect(50, 70, 220, 60))
        self.button_flota_ciagniki.setObjectName("button_flota_ciagniki")

        self.button_flota_naczepy = QtWidgets.QPushButton(self.frame_flota)
        self.button_flota_naczepy.setGeometry(QtCore.QRect(290, 70, 220, 60))
        self.button_flota_naczepy.setObjectName("button_flota_naczepy")

        self.button_flota_kierowcy = QtWidgets.QPushButton(self.frame_flota)
        self.button_flota_kierowcy.setGeometry(QtCore.QRect(530, 70, 220, 60))
        self.button_flota_kierowcy.setObjectName("button_flota_kierowcy")

        self.button_flota_dodaj = QtWidgets.QPushButton(self.frame_flota)
        self.button_flota_dodaj.setGeometry(QtCore.QRect(50, 820, 700, 60))
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

        # Konfiguracja zamykania ramki floty
        self.button_exit_flota.clicked.connect(self.hide_flota)

        # Dodanie ramki floty do głównego widgetu
        self.verticalLayout = QtWidgets.QVBoxLayout(self.frame_flota)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)

        # Ustawienie centralnego widżetu
        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # Animacja dla ramki floty
        self.anim_flota = QPropertyAnimation(self.frame_flota, b"pos")
        self.anim_flota.setDuration(500)
        self.anim_flota.setStartValue(QPoint(0, MainWindow.height()))  # Start na dole ekranu
        self.anim_flota.setEndValue(QPoint(0, 50))  # Przejdź do pozycji (0, 50)

        self.anim_flota_back = QPropertyAnimation(self.frame_flota, b"pos")
        self.anim_flota_back.setDuration(500)
        self.anim_flota_back.setStartValue(QPoint(0, 50))  # Start na dole ekranu
        self.anim_flota_back.setEndValue(QPoint(0, MainWindow.height()))  # Przejdź do pozycji (0, 50)

    def retranslateUi(self, MainWindow):
        # Ustawienie tekstu w przyciskach
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Window Title"))
        self.button_flota.setText(_translate("MainWindow", "Flota"))
        self.button_serwis.setText(_translate("MainWindow", "Serwis"))
        self.button_magazyn.setText(_translate("MainWindow", "Magazyn"))
        self.label_time.setText(_translate("MainWindow", "23:55"))
        self.label_date.setText(_translate("MainWindow", "22.10.2024"))
        self.label_flota_header.setText(_translate("MainWindow", "FLOTA"))
        self.button_flota_ciagniki.setText(_translate("MainWindow", "Ciągniki siodłowe"))
        self.button_flota_naczepy.setText(_translate("MainWindow", "Naczepy ciężarowe"))
        self.button_flota_kierowcy.setText(_translate("MainWindow", "Kierowcy"))
        self.button_flota_dodaj.setText(_translate("MainWindow", "DODAJ"))

    def show_flota(self):
        # Ustawienie ramki floty w pozycji początkowej
        print("Wywołano show_flota: ramka floty będzie widoczna.")  # Komunikat w terminalu
        self.frame_flota.setEnabled(True)
        self.frame_flota.show()  # Pokaż ramkę
        self.anim_flota.start()  # Uruchom animację

    def hide_flota(self):
        print("Wywołano hide_flota: ramka floty zostanie ukryta.")  # Komunikat w terminalu
        # Ustawienie kierunku animacji wstecz
        self.anim_flota_back.start() # Uruchom animację
        # Po zakończeniu animacji ukryj ramkę
        self.anim_flota_back.finished.connect(lambda: self.frame_flota.setEnabled(False))

    def on_row_clicked(self, index):
        row = index.row()  # Indeks wiersza
        item = self.model.item(row)  # Przykładowe uzyskanie danych
        id_item = self.model.item(row, 0).text()  # ID z pierwszej kolumny
        name_item = self.model.item(row, 1).text()  # Nazwa z drugiej kolumny

        # Wyświetlenie informacji o kliknięciu
        QMessageBox.information(None, "Wiersz kliknięty",
                                f"Kliknięto w wiersz {row + 1}:\nID: {id_item}\nNazwa: {name_item}")


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
