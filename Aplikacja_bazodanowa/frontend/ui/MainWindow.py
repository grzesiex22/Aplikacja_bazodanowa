from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer, QDateTime, Qt
from PyQt5.QtWidgets import QMainWindow
from Aplikacja_bazodanowa.frontend.ui.FleetFrame import FleetFrame


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow(self)  # Inicjalizacja instancji Ui_MainWindow
        self.ui.setupUi(self)  # Wywołanie metody setupUi
        # Ustawienie flag okna

        self.setWindowFlags(Qt.FramelessWindowHint)
class Ui_MainWindow(object):
    def __init__(self, main_window):
        self.main_window = main_window  # Przechowaj referencję do głównego okna
        self.screen_width = 0  # Zmienna na szerokość ekranu
        self.screen_height = 0  # Zmienna na wysokość ekranu

        self.update_window_size()  # Ustawienie początkowego rozmiaru okna

        # Timer do cyklicznego sprawdzania wysokości
        self.timer = QTimer(main_window)
        self.timer.timeout.connect(self.update_window_size)
        self.timer.start(1000)  # Co 1 sekundę

    def update_window_size(self):
        # Uzyskaj dostępny obszar
        available_rect = self.main_window.screen().availableGeometry()  # Użycie self.main_window
        self.screen_height = available_rect.height()
        self.screen_width = available_rect.width()

        self.main_window.setFixedSize(self.screen_width, self.screen_height)  # 80% szerokości i wysokości ekranu


    def setupUi(self, MainWindow):

        # Konfiguracja głównego okna
        MainWindow.setObjectName("MainWindow")
        MainWindow.setEnabled(True)

        # Ustawienie palety kolorów
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(131, 165, 240))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        MainWindow.setPalette(palette)

        # Inicjalizacja ramki floty
        self.flota_window = FleetFrame(MainWindow)

        # Ustawienie głównego widgetu
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.centralwidget.setFont(font)
        self.centralwidget.setAcceptDrops(False)
        self.centralwidget.setObjectName("centralwidget")

        # Tworzenie ramki głównej
        self.frame_main = QtWidgets.QFrame(self.centralwidget)
        self.frame_main.setGeometry(QtCore.QRect(0, 50, self.screen_width, self.screen_height))
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
        self.widget_buttons.setGeometry(QtCore.QRect(int(self.screen_width/2-300/2), int((self.screen_height-50)/2-400/2), 300, 400))
        self.widget_buttons.setStyleSheet("QPushButton {"
                                           "    background-color: #3498db;  /* Kolor tła */"
                                           "    color: white;  /* Kolor tekstu */"
                                           "    border-radius: 10px;  /* Zaokrąglone rogi */"
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
                                           "    border: 2px solid #95a5a6;  /* Obramowanie dla nieaktywnych przycisków */"
                                           "}")
        self.widget_buttons.setObjectName("widget_buttons")

        # Przyciski
        self.button_flota = QtWidgets.QPushButton(self.widget_buttons)
        self.button_flota.setGeometry(QtCore.QRect(0, 0, 300, 100))
        self.button_flota.setObjectName("button_flota")
        # Połączenie przycisku flota z wywołaniem metody show_flota
        self.button_flota.clicked.connect(self.flota_window.show_flota)


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
        self.widget_datetime.setGeometry(QtCore.QRect(int(self.screen_width/2-250/2), 10, 250, 30))
        self.widget_datetime.setStyleSheet("QLabel {"
                                            "    color: #ffffff;  /* Kolor tekstu dla etykiet */"
                                            "    background-color: transparent;  /* Przezroczyste tło dla etykiet */"
                                            "    border: none;  /* Brak ramki dla etykiet */"
                                            "    font-size: 14px;"
                                            "    font-weight: bold;  /* Ustawienie pogrubienia tekstu */"
                                            "}")

        self.widget_datetime.setObjectName("widget_datetime")

        self.label_time = QtWidgets.QLabel(self.widget_datetime)
        self.label_time.setGeometry(QtCore.QRect(160, 0, 80, 30))
        self.label_time.setMaximumSize(QtCore.QSize(150, 40))
        self.label_time.setObjectName("label_time")

        self.label_date = QtWidgets.QLabel(self.widget_datetime)
        self.label_date.setGeometry(QtCore.QRect(0, 0, 100, 30))
        self.label_date.setMaximumSize(QtCore.QSize(150, 40))
        self.label_date.setObjectName("label_date")

        # Linia pionowa
        self.linia_pionowa = QtWidgets.QFrame(self.widget_datetime)
        self.linia_pionowa.setGeometry(QtCore.QRect(124, 0, 3, 30))
        self.linia_pionowa.setStyleSheet("QFrame {"
                                          "    background-color: #ffffff;  /* Kolor linii */"
                                          "    max-width: 1px;  /* Grubość linii */"
                                          "}")
        self.linia_pionowa.setFrameShape(QtWidgets.QFrame.VLine)
        self.linia_pionowa.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.linia_pionowa.setLineWidth(2)
        self.linia_pionowa.setObjectName("linia_pionowa")

        # Timer do aktualizacji daty i czasu
        self.timer = QTimer(MainWindow)
        self.timer.timeout.connect(self.update_datetime)
        self.timer.start(1000)  # Aktualizacja co sekundę

        # Przyciski systemowe
        self.widget_system = QtWidgets.QWidget(self.centralwidget)
        self.widget_system.setGeometry(QtCore.QRect(self.screen_width-85-10, 5, 85, 40))
        self.widget_system.setObjectName("widget_system")
        self.button_exit = QtWidgets.QPushButton(self.widget_system)
        self.button_exit.setEnabled(True)
        self.button_exit.setGeometry(QtCore.QRect(45, 0, 40, 40))
        self.button_exit.setStyleSheet("QPushButton {"
                                       "    background-color: #c84043; /* Ustawia przezroczyste tło */"
                                       "    border: 2px solid white; /* Ustawia kolor ramki (czarny) */"
                                       "    border-radius: 15px; /* Zaokrąglone rogi ramki */"
                                       "    padding: 5px; /* Wewnętrzne odstępy, opcjonalne */"
                                       "    opacity: 0.5;"
                                       "}"
                                       ""
                                       "QPushButton:hover {"
                                       "    background-color: #a73639; /* Ustawia kolor tła po najechaniu */"
                                       "}")
        self.button_exit.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("icons/cross_white.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_exit.setIcon(icon1)
        self.button_exit.setIconSize(QtCore.QSize(25, 25))
        self.button_exit.setObjectName("button_exit")
        self.button_exit.clicked.connect(self.main_window.close)  # Połączenie z metodą zamykającą okno


        self.button_minimize = QtWidgets.QPushButton(self.widget_system)
        self.button_minimize.setEnabled(True)
        self.button_minimize.setGeometry(QtCore.QRect(0, 0, 40, 40))
        self.button_minimize.setStyleSheet("QPushButton {"
                                           "    background-color: #7e95b9; /* Ustawia przezroczyste tło */"
                                           "    border: 2px solid white; /* Ustawia kolor ramki (czarny) */"
                                           "    border-radius: 15px; /* Zaokrąglone rogi ramki */"
                                           "    padding: 5px; /* Wewnętrzne odstępy, opcjonalne */"
                                           "    opacity: 0.5;"
                                           "}"
                                           ""
                                           "QPushButton:hover {"
                                           "    background-color: #627590; /* Ustawia kolor tła po najechaniu */"
                                           "}")
        self.button_minimize.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("icons/minus_white.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_minimize.setIcon(icon2)
        self.button_minimize.setIconSize(QtCore.QSize(25, 25))
        self.button_minimize.setObjectName("button_minimize")
        self.button_minimize.clicked.connect(self.main_window.showMinimized)  # Połączenie z metodą zamykającą okno

        # Nazwa aplikacji
        self.title = QtWidgets.QLabel(self.centralwidget)
        self.title.setGeometry(QtCore.QRect(20, 10, 250, 30))
        self.title.setStyleSheet("QLabel {\n"
                                 "    color: #ffffff;  /* Kolor tekstu dla etykiet (przykład: pomarańczowy) */\n"
                                 "    background-color: transparent;  /* Przezroczyste tło dla etykiet */\n"
                                 "    border: none;  /* Brak ramki dla etykiet */\n"
                                 "    font-size: 16px;\n"
                                 "    font-weight: bold;  /* Ustawienie pogrubienia tekstu */\n"
                                 "}")
        self.title.setObjectName("title")

        # Ustawienia dla MainWindow
        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)
        self.update_datetime()  # Początkowa aktualizacja daty i czasu


    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Baza danych firmy transportowej"))
        self.button_flota.setText(_translate("MainWindow", "Flota"))
        self.button_serwis.setText(_translate("MainWindow", "Serwis"))
        self.button_magazyn.setText(_translate("MainWindow", "Magazyn"))
        self.label_date.setText(_translate("MainWindow", "Data"))
        self.label_time.setText(_translate("MainWindow", "Czas"))
        self.title.setText(_translate("MainWindow", "Aplikacja transportowa"))

    # Funkcja aktualizująca datę i czas
    def update_datetime(self):
        current_datetime = QDateTime.currentDateTime()
        current_date = current_datetime.toString('yyyy-MM-dd')  # Format daty
        current_time = current_datetime.toString('HH:mm:ss')    # Format czasu
        self.label_date.setText(current_date)
        self.label_time.setText(current_time)
