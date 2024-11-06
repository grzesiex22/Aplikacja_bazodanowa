from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QTableView, QFrame, QLineEdit, QVBoxLayout, QScrollArea, QGridLayout, QLabel, QPushButton, QAbstractItemView

class EditFrame(QFrame):
    def __init__(self, model, row, parent=None, header_title="title"):
        super().__init__(parent)

        self.app_width = 0
        self.app_height = 0
        available_rect = self.parent().screen().availableGeometry()
        self.app_width = available_rect.width()
        self.app_height = available_rect.height()

        self.model = model
        self.row = row
        self.is_moving = False  # For tracking if the frame is being moved
        self.mouse_press_pos = None  # To store the initial position of the mouse press
        self.row_count = self.model.columnCount()
        self.row_height = 50

        self.setWindowTitle("Edycja Wiersza")
        height = self.row_count*self.row_height+120
        width = 500
        self.setGeometry(int(self.app_width/2-width/2), int(self.app_height/2-height/2), width, height)
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

        # Dodawanie etykiet i pól edycyjnych
        for column in range(self.model.columnCount()):
            header_item = self.model.horizontalHeaderItem(column)  # Pobierz nagłówek kolumny
            if header_item:
                header_text = header_item.text()  # Tekst nagłówka
                item = self.model.item(self.row, column)  # Element tabeli

                # Etykieta dla nagłówka
                label = QLabel(header_text)
                label.setFixedHeight(40)  # Ustawienie stałej wysokości
                self.gridLayout_edit.addWidget(label, column, 0)  # Pierwsza kolumna

                # Pole edycyjne
                line_edit = QLineEdit(item.text())
                line_edit.setObjectName(f"line_edit_{self.row}_{column}")  # Umożliwia późniejszy dostęp
                self.gridLayout_edit.addWidget(line_edit, column, 1)  # Druga kolumna
                self.gridLayout_edit.setRowMinimumHeight(column, 100)


        self.widget_header = QtWidgets.QWidget(self)
        self.widget_header.setGeometry(QtCore.QRect(0, 0, self.width(), 40))
        self.widget_header.setObjectName("widget_header_frame_edit")
        self.widget_header.setStyleSheet("""
                                        QWidget {
                                            background: #cfb796;
                                            border-radius: 10px;
                                            
                                        }""")

        self.label_header = QtWidgets.QLabel(self.widget_header)
        self.label_header.setGeometry(QtCore.QRect(int(self.widget_header.width()/2-50), 10, 100, 20))
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
        self.button_clear.setGeometry(QtCore.QRect(int(self.width()/2)-120-60-20, self.height()-50, 120, 40))
        self.button_clear.setText("Wyczyść")
        self.button_clear.setObjectName("button_clear")

        self.button_delete = QtWidgets.QPushButton(self)
        self.button_delete.setGeometry(QtCore.QRect(int(self.width()/2)-60, self.button_clear.pos().y(), 120, 40))
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

        self.button_save = QtWidgets.QPushButton(self)
        self.button_save.setGeometry(QtCore.QRect(int(self.width()/2)+60+20, self.button_clear.pos().y(), 120, 40))
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
    

    def save_changes(self):
        for column in range(self.model.columnCount()):
            line_edit = self.findChild(QLineEdit, f"line_edit_{self.row}_{column}")
            if line_edit:
                # Zaktualizuj model danych z wartościami z linii edycyjnej
                self.model.item(self.row, column).setText(line_edit.text())

        self.close()  # Zamknij QFrame po zapisaniu

    def close_window(self):
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