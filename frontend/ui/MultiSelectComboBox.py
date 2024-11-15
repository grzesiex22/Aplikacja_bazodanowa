from PyQt5.QtGui import QRegion
from PyQt5.QtWidgets import QApplication, QMainWindow, QComboBox, QListWidget, QListWidgetItem, QWidget, QVBoxLayout, \
    QHBoxLayout, QLabel, QWidgetAction, QMenu, QAbstractItemView, QPushButton
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
import sys


# MultiSelectComboBox QSS
combo_qss = """

QWidget {    /* wokół pasków przewijania */
    border: 0px solid #fccccb;
    border-radius: 10px;
    background-color: transparent;
}

/* Styl dla QComboBox */
QComboBox {
    border: 2px solid #927fbf;
    border-radius: 5px;
    padding: 10px;
    background-color: #c4bbf0;
    color: #333333;
}

QComboBox QAbstractItemView {
    selection-background-color: #d7d1f0;  /* Kolor zaznaczonego elementu */
    background-color: #d7d1f0;
    color: #333333;
    border: 2px solid #927fbf;
    border-radius: 10px;
    margin: 2px 0px 0px 0px; /* top right bottom left */
}

QComboBox::drop-down {
    subcontrol-origin: margin;
    subcontrol-position: top right;
    width: 30px;
    border-left: 1px solid #927fbf;
}

QComboBox::down-arrow {
    image: url("../icons/angle-down.png");  /* Możesz podać swoją ikonę */
    subcontrol-origin: margin;
    subcontrol-position: center;
    width: 20px;  /* Możesz zmienić rozmiar */
    height: 20px; /* Możesz dostosować wysokość */
}

/* Styl dla QListWidget */
QListWidget {
    background-color: #transparent;
    border: none;
    color: #dff0ef;
    border-radius: 10px;
    outline: none;
}
QListWidget::item {
    padding: 5px;
    background-color: transparent;  /* Ustawienie przezroczystego tła dla elementów */
    border-radius: 10px;
    border: none;
    margin: 0px 25px 0px 0px; /* top right bottom left */
    
}
QListWidget::item:selected:active {
    background-color: transparent;
    color: green;
    border: none;
}

QListWidget::item:focus {
    outline: none;
}



/* PASKI PRZEWIJANIA */
QAbstractScrollArea::corner {
    border-radius: 10px;
    background-color: #927fbf;
    margin: 2px;
}

/* PASEK PRZEWIJANIA PIONOWY */
QScrollBar:vertical {
    border: 2px solid #927fbf;
    background: #c4bbf0;
    width: 30px;
    margin: 28px 2px 28px 4px; /* top right bottom left */
    border-radius: None;
}
QScrollBar::handle:vertical {
    background: #c4bbf0;
    border: 1px solid #927fbf;
    min-height: 10px;
    border-radius: None;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {     /* Przewijanie */
    background: #927fbf;
    height: 24px;
    width: 24px;
    border-radius: 8px;
}
QScrollBar::add-line:vertical {     /* Przewijanie w dół */
    subcontrol-origin: margin;
    subcontrol-position: bottom;
    margin: 0px 2px 2px 4px; /* top right bottom left */
}
QScrollBar::sub-line:vertical {     /* Przewijanie w górę */
    subcontrol-origin: margin;
    subcontrol-position: top;
    margin: 2px 2px 0px 4px; /* top right bottom left */
}

QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
    background: transparent;
    width: 20px;
    height: 20px; /* Ustaw wysokość strzałek */
    border-radius: 6px;
    margin: 0; /* Środkowanie strzałki */
    padding: 2px;  /* Dodajemy mały padding, by wyrównać pozycję */
}

QScrollBar::up-arrow:vertical {
    image: url("../icons/angle-up.png");
    subcontrol-origin: padding;
    subcontrol-position: center;
  
}
QScrollBar::down-arrow:vertical {
    image: url("../icons/angle-down.png");
    subcontrol-origin: padding;
    subcontrol-position: center;
   
}

/* PASEK PRZEWIJANIA POZIOMY */
QScrollBar:horizontal  {
    border: 2px solid #927fbf;
    background: #c4bbf0;
    height: 30px;
    margin: 4px 28px 2px 28px; /* top right bottom left */
    border-radius: 0px;
}
QScrollBar::handle:horizontal {
    background: #c4bbf0;
    border: 1px solid #927fbf;
    min-width: 10px;
    
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    background: #927fbf;
    height: 24px;
    width: 24px;
    border-radius: 6px;
}
QScrollBar::add-line:horizontal { /* Przewijanie w lewo */
    subcontrol-origin: margin;
    subcontrol-position: right;
    margin: 4px 2px 2px 0px;  /* top right bottom left */
}
QScrollBar::sub-line:horizontal { /* Przewijanie w prawo */
    subcontrol-origin: margin;
    subcontrol-position: left;
    margin: 4px 0px 2px 2px; /* top right bottom left */
}
QScrollBar::left-arrow:horizontal, QScrollBar::right-arrow:horizontal {
    background: transparent;
    width: 20px;
    height: 20px;
    border-radius: 6px;
    margin: 0; /* Środkowanie strzałki */
    padding: 2px;  /* Dodajemy mały padding, by wyrównać pozycję */
}
QScrollBar::left-arrow:horizontal {
    image: url(../icons/angle-left.png);
    subcontrol-origin: padding;
    subcontrol-position: center;
}
QScrollBar::right-arrow:horizontal {
    image: url(../icons/angle-right.png);
    subcontrol-origin: padding;
    subcontrol-position: center;
}

"""

class MultiSelectComboBox(QComboBox):
    def __init__(self, items=None, width=100):
        super().__init__()
        # Ustawienie QSS
        self.width = width
        self.setFixedWidth(self.width)
        self.setStyleSheet(combo_qss)

        # Ustawienia pola wyboru
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)  # Pole tylko do odczytu
        self.lineEdit().installEventFilter(self)  # Nasłuchujemy kliknięcia na polu tekstowym

        # Tworzymy listę z możliwością wielokrotnego wyboru
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.NoSelection)


        # Dodajemy przekazane elementy (jeśli są) jako opcje do wyboru
        if items:
            for item_text in items:
                item = QListWidgetItem(item_text)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Unchecked)
                self.list_widget.addItem(item)

        # Dodanie listy do rozwijanego menu
        widget_action = QWidgetAction(self)
        self.list_widget.setDragEnabled(False)
        widget_action.setDefaultWidget(self.list_widget)

        self.menu = QMenu(self)
        self.menu.addAction(widget_action)

        # Usuwanie obramowania i tła w QMenu
        self.menu.setWindowFlags(self.menu.windowFlags() | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        self.menu.setAttribute(Qt.WA_TranslucentBackground)

        # # Obsługa kliknięcia elementu na liście (przełączanie stanu checkboxa)
        self.list_widget.itemPressed.connect(self.toggle_item_check_state)
        self.list_widget.itemChanged.connect(self.toggle_checkbox_check_state)

        # Obsługa zmiany stanu elementów
        self.list_widget.itemChanged.connect(self.update_line_edit)

    def showPopup(self):
        # Wyświetlanie menu
        # Ustawiamy szerokość menu rozwijanego na szerokość QComboBox
        self.list_widget.setFixedWidth(self.width)
        self.menu.setFixedWidth(self.width)
        self.menu.exec_(self.mapToGlobal(self.rect().bottomLeft()))

    def hidePopup(self):
        pass  # Zapobiega domyślnemu chowaniu menu

    def eventFilter(self, source, event):
        if event.type() == event.MouseButtonPress and source == self.lineEdit():
            self.showPopup()
        return super().eventFilter(source, event)

    def toggle_item_check_state(self, item):
        # Przełącza stan checkboxa przy kliknięciu elementu
        if item.checkState() == Qt.Checked:
            item.setCheckState(Qt.Unchecked)
        else:
            item.setCheckState(Qt.Checked)

    def toggle_checkbox_check_state(self, item):
        if item.checkState() == Qt.Checked:
            item.setSelected(True)
        else:
            item.setSelected(False)


    def update_line_edit(self):
        # Aktualizowanie pola tekstowego, aby wyświetlić wybrane elementy
        selected_items = [item.text() for item in self.list_widget.findItems("", Qt.MatchContains) if
                          item.checkState() == Qt.Checked]
        self.lineEdit().setText(', '.join(selected_items))

    def get_selected_items(self):
        """Zwraca listę zaznaczonych elementów."""
        return [item.text() for item in self.list_widget.findItems("", Qt.MatchContains) if
                item.checkState() == Qt.Checked]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aplikacja z Polem Wielokrotnego Wyboru")
        self.setGeometry(QtCore.QRect(100, 100, 500, 500))

        # Tworzymy centralny widget i layout
        central_widget = QWidget(self)
        central_widget.setGeometry(QtCore.QRect(25, 50, 450, 100))
        central_widget.setStyleSheet("""
        QWidget {    /* Cała tabela */
            border: 2px solid #fccccb;
            border-radius: 15px;
            background-color: #fff0ef;
        }""")
        # Tworzymy layout poziomy do umieszczenia dwóch MultiSelectComboBox obok siebie
        combo_layout = QHBoxLayout(central_widget)

        items1 = []
        # Tworzymy i dodajemy dwa MultiSelectComboBox do layoutu poziomego
        for i in range (10):
            if i % 2:
                items1.append(f"Eleeeeeeeeeeeeeeeement {i}")
            else:
                items1.append(f"Eleeeeeeeeement {i}")

        self.multi_select_combo1 = MultiSelectComboBox(items1, 200)
        combo_layout.addWidget(self.multi_select_combo1)

        items2 = ["Opcja A", "Opcja B", "Opcja C", "Opcja D", "Opcja E", "Opcja F", "Opcja G"]
        multi_select_combo2 = MultiSelectComboBox(items2, 200)
        combo_layout.addWidget(multi_select_combo2)

        button = QPushButton(self)
        button.setGeometry(QtCore.QRect(250, 300, 100, 50))
        button.clicked.connect(self.print_combo)


    def print_combo(self):
        selected_items = self.multi_select_combo1.get_selected_items()

        # Wydrukowanie zaznaczonych elementów
        print(selected_items)  # Na przykład: ["Opcja 1", "Opcja 3"]



# Uruchomienie aplikacji
app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())