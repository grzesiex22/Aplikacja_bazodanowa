import os
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QPushButton, QLabel, QFileDialog, QVBoxLayout, QHBoxLayout, QLineEdit

class SimpleGenerateRaport(QFrame):
    def __init__(self, parent=None, header_title="title", save_callback=None):
        super().__init__(parent)

        # Ścieżka do ikon
        self.icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'icons')).replace('\\', '/')

        self.save_callback = save_callback  # Funkcja wywołania zwrotnego do zapisywania raportu

        # Do przesuwania oknem
        self.is_moving = False
        self.mouse_press_pos = None

        # Wymiary okna
        screen = QtWidgets.QApplication.primaryScreen()
        available_rect = screen.availableGeometry() if screen else QtCore.QRect(0, 0, 800, 600)
        self.app_width = available_rect.width()
        self.app_height = available_rect.height()
        self.height = 250
        self.width = 500

        # Ustawienia interfejsu
        self.setup_ui(header_title)

        self.selected_path = None  # Zmienna do przechowywania wybranego folderu

    def setup_ui(self, title):
        self.setGeometry(int(self.app_width / 2 - self.width / 2), int(self.app_height / 2 - self.height / 2),
                         self.width, self.height)
        self.setStyleSheet("""
                                            QFrame {
                                                background-color: #c4bbf0;
                                                border: 2px solid #ac97e2 ; 
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

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 50, 10, 10)  # Dodaj górny margines (np. 50 px)
        layout.setSpacing(10)  # Odstęp między elementami

        # Nagłówek okna
        self.widget_header = QtWidgets.QWidget(self)
        self.widget_header.setGeometry(QtCore.QRect(0, 0, self.width, 40))
        self.widget_header.setObjectName("widget_header_frame_edit")
        self.widget_header.setStyleSheet("""
                                                    QWidget {
                                                        background: #ac97e2;
                                                        border-radius: 10px;
                                                    }""")

        # Nazwa okna
        self.label_header = QtWidgets.QLabel(self.widget_header)
        self.label_header.setGeometry(QtCore.QRect(int(self.widget_header.width() / 2 - 100), 10, 200, 20))
        self.label_header.setAlignment(Qt.AlignCenter)
        self.label_header.setText(title)
        self.label_header.setStyleSheet("""
                                                    QLabel {
                                                        font-size: 16px;
                                                        font-weight: bold;  /* Ustawienie pogrubienia tekstu */
                                                    }""")
        self.label_header.setObjectName("label_frame_edit")

        # Zamknięcie okna
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
        icon1.addPixmap(QtGui.QPixmap(f"{self.icon_path}/cross_white.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_exit.setIcon(icon1)
        self.button_exit.setIconSize(QtCore.QSize(15, 15))
        self.button_exit.setObjectName("button_exit_frame_edit")
        self.button_exit.clicked.connect(self.close_window)

        # Pole do wpisania nazwy pliku
        self.file_name_input = QtWidgets.QLineEdit(self)
        self.file_name_input.setPlaceholderText("Wprowadź nazwę pliku")
        self.file_name_input.textChanged.connect(self.check_inputs)  # Nasłuchiwanie zmian w nazwie pliku

        self.file_name_input.setStyleSheet("""
                                        QLineEdit {
                                            border: 2px solid #ac97e2;
                                            border-radius: 5px;
                                            padding: 2px;
                                            background-color: #c4bbf0;
                                            color: #333333;
                                        }
                                    """)

        # Pole wyświetlania ścieżki do wybranego folderu
        self.path_display = QtWidgets.QLineEdit(self)
        self.path_display.setPlaceholderText("Ścieżka folderu")
        self.path_display.setReadOnly(True)  # Tylko do odczytu
        self.path_display.setStyleSheet("""
                                        QLineEdit {
                                            border: 2px solid #ac97e2;
                                            border-radius: 5px;
                                            padding: 2px;
                                            background-color: #c4bbf0;
                                            color: #333333;
                                        }
                                    """)

        # Przycisk wyboru folderu
        self.button_choose_folder = QtWidgets.QPushButton("Wybierz folder", self)
        self.button_choose_folder.clicked.connect(self.choose_folder)

        # Tworzymy layout dla przycisków na dole i wyśrodkowanie ich
        button_layout = QHBoxLayout()

        # Przycisk zapisania raportu
        self.button_save = QtWidgets.QPushButton("Zapisz raport", self)
        self.button_save.setEnabled(False)
        self.button_save.clicked.connect(self.save_report)
        button_layout.addWidget(self.button_choose_folder)
        button_layout.addWidget(self.button_save)

        # Dodajemy wszystkie elementy do głównego layoutu
        layout.addWidget(self.file_name_input)
        layout.addWidget(self.path_display)
        layout.addLayout(button_layout)

    def close_window(self):
        self.close()  # Zamykamy okno

    def choose_folder(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Wybierz folder")
        if path:
            self.selected_path = path
            self.path_display.setText(self.selected_path)  # Ustawiamy ścieżkę w polu
        self.check_inputs()  # Sprawdzamy warunki po wybraniu folderu

    def check_inputs(self):
        # Sprawdzamy, czy zarówno folder jak i nazwa pliku są podane
        if self.selected_path and self.file_name_input.text().strip():
            self.button_save.setEnabled(True)
        else:
            self.button_save.setEnabled(False)

    def save_report(self):
        file_name = self.file_name_input.text().strip()
        if not file_name:
            QtWidgets.QMessageBox.warning(self, "Błąd", "Proszę podać nazwę pliku.")
            return
        if not file_name.endswith(".pdf"):
            file_name += ".pdf"
        if self.selected_path:
            full_file_path = os.path.join(self.selected_path, file_name)
            if self.save_callback:
                self.save_callback(full_file_path)
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
