from PyQt5.QtGui import QRegion
from PyQt5.QtWidgets import QApplication, QMainWindow, QComboBox, QListWidget, QListWidgetItem, QWidget, QVBoxLayout, \
    QHBoxLayout, QLabel, QWidgetAction, QMenu, QAbstractItemView, QPushButton, QSizePolicy
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
import sys


# # MultiSelectComboBox.qss QSS
# combo_qss = """
#
# QWidget {    /* wokół pasków przewijania */
#     border: 0px solid #fccccb;
#     border-radius: 10px;
#     background-color: transparent;
# }
#
# /* Styl dla QComboBox */
# QComboBox {
#     border: 2px solid #ac97e2;
#     border-radius: 5px;
#     padding: 2px;
#     background-color: #c4bbf0;
#     color: #333333;
# }
#
# QComboBox QAbstractItemView {
#     selection-background-color: #d7d1f0;  /* Kolor zaznaczonego elementu */
#     background-color: #d7d1f0;
#     color: #333333;
#     border: 2px solid #ac97e2;
#     border-radius: 10px;
#     margin: 2px 0px 0px 0px; /* top right bottom left */
# }
#
# QComboBox::drop-down {
#     subcontrol-origin: margin;
#     subcontrol-position: top right;
#     width: 30px;
#     border-left: 1px solid #ac97e2;
# }
#
# QComboBox::down-arrow {
#     image: url("../icons/angle-down.png");  /* Możesz podać swoją ikonę */
#     subcontrol-origin: margin;
#     subcontrol-position: center;
#     width: 20px;  /* Możesz zmienić rozmiar */
#     height: 20px; /* Możesz dostosować wysokość */
# }
#
# /* Styl dla QListWidget */
# QListWidget {
#     background-color: #transparent;
#     border: none;
#     color: #dff0ef;
#     border-radius: 10px;
#     outline: none;
# }
# QListWidget::item {
#     padding: 5px;
#     background-color: transparent;  /* Ustawienie przezroczystego tła dla elementów */
#     border-radius: 10px;
#     border: none;
#     margin: 0px 25px 0px 0px; /* top right bottom left */
#
# }
# QListWidget::item:selected:active {
#     background-color: transparent;
#     color: green;
#     border: none;
# }
#
# QListWidget::item:focus {
#     outline: none;
# }
#
#
#
# /* PASKI PRZEWIJANIA */
# QAbstractScrollArea::corner {
#     border-radius: 10px;
#     background-color: #ac97e2;
#     margin: 2px;
# }
#
# /* PASEK PRZEWIJANIA PIONOWY */
# QScrollBar:vertical {
#     border: 2px solid #ac97e2;
#     background: #c4bbf0;
#     width: 30px;
#     margin: 28px 2px 28px 4px; /* top right bottom left */
#     border-radius: None;
# }
# QScrollBar::handle:vertical {
#     background: #c4bbf0;
#     border: 1px solid #ac97e2;
#     min-height: 10px;
#     border-radius: None;
# }
# QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {     /* Przewijanie */
#     background: #ac97e2;
#     height: 24px;
#     width: 24px;
#     border-radius: 8px;
# }
# QScrollBar::add-line:vertical {     /* Przewijanie w dół */
#     subcontrol-origin: margin;
#     subcontrol-position: bottom;
#     margin: 0px 2px 2px 4px; /* top right bottom left */
# }
# QScrollBar::sub-line:vertical {     /* Przewijanie w górę */
#     subcontrol-origin: margin;
#     subcontrol-position: top;
#     margin: 2px 2px 0px 4px; /* top right bottom left */
# }
#
# QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
#     background: transparent;
#     width: 20px;
#     height: 20px; /* Ustaw wysokość strzałek */
#     border-radius: 6px;
#     margin: 0; /* Środkowanie strzałki */
#     padding: 2px;  /* Dodajemy mały padding, by wyrównać pozycję */
# }
#
# QScrollBar::up-arrow:vertical {
#     image: url("icons/angle-up.png");
#     subcontrol-origin: padding;
#     subcontrol-position: center;
#
# }
# QScrollBar::down-arrow:vertical {
#     image: url("icons/angle-down.png");
#     subcontrol-origin: padding;
#     subcontrol-position: center;
#
# }
#
# /* PASEK PRZEWIJANIA POZIOMY */
# QScrollBar:horizontal  {
#     border: 2px solid #ac97e2;
#     background: #c4bbf0;
#     height: 30px;
#     margin: 4px 28px 2px 28px; /* top right bottom left */
#     border-radius: 0px;
# }
# QScrollBar::handle:horizontal {
#     background: #c4bbf0;
#     border: 1px solid #ac97e2;
#     min-width: 10px;
#
# }
# QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
#     background: #ac97e2;
#     height: 24px;
#     width: 24px;
#     border-radius: 6px;
# }
# QScrollBar::add-line:horizontal { /* Przewijanie w lewo */
#     subcontrol-origin: margin;
#     subcontrol-position: right;
#     margin: 4px 2px 2px 0px;  /* top right bottom left */
# }
# QScrollBar::sub-line:horizontal { /* Przewijanie w prawo */
#     subcontrol-origin: margin;
#     subcontrol-position: left;
#     margin: 4px 0px 2px 2px; /* top right bottom left */
# }
# QScrollBar::left-arrow:horizontal, QScrollBar::right-arrow:horizontal {
#     background: transparent;
#     width: 20px;
#     height: 20px;
#     border-radius: 6px;
#     margin: 0; /* Środkowanie strzałki */
#     padding: 2px;  /* Dodajemy mały padding, by wyrównać pozycję */
# }
# QScrollBar::left-arrow:horizontal {
#     image: url(icons/angle-left.png);
#     subcontrol-origin: padding;
#     subcontrol-position: center;
# }
# QScrollBar::right-arrow:horizontal {
#     image: url(../icons/angle-right.png);
#     subcontrol-origin: padding;
#     subcontrol-position: center;
# }
#
# """
#


class MultiSelectComboBox(QComboBox):
    def __init__(self, items=None, width=100, height = 20):
        super().__init__()
        self.items = items
        # Ustawienie QSS
        # self.setStyleSheet(combo_qss)

        # Inicjalizacja rozmiarów
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumWidth(width)  # Minimalna szerokość
        self.setMinimumHeight(height)  # Minimalna wysokość

        # Ustawienia pola wyboru
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)  # Pole tylko do odczytu
        self.lineEdit().installEventFilter(self)  # Nasłuchujemy kliknięcia na polu tekstowym

        # Tworzymy listę z możliwością wielokrotnego wyboru
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.NoSelection)

        # Dodajemy elementy z obsługą słowników
        self.items_data = {}  # Słownik przechowujący oryginalne dane elementów
        self.data_to_id = {}  # Odwrotny słownik, przechowuje mapowanie 'data' -> 'ID'

        if self.items:
            for item in self.items:
                if isinstance(item, dict) and 'ID' in item and 'data' in item:
                    # Obsługa słownika {'ID': ..., 'data': ...}
                    key = item['ID']
                    value = item['data']
                    list_item = QListWidgetItem(value)  # Wyświetlamy tylko 'data'
                    self.items_data[key] = item  # Przechowujemy cały słownik
                    self.data_to_id[value] = key  # Przechowujemy odwrotną mapę (data -> ID)
                    # print(f"Dodano słownik: {key} -> {item}")  # Logowanie danych
                elif isinstance(item, dict):
                    key, value = next(iter(item.items()))
                    list_item = QListWidgetItem(value)  # Wyświetlamy tylko wartość
                    self.items_data[key] = value
                    self.data_to_id[value] = key  # Mapowanie 'data' -> 'ID'
                    # print(f"Dodano słownik: {key} -> {value}")  # Logowanie danych
                else:
                    list_item = QListWidgetItem(item)
                    self.items_data[item] = item  # Przechowujemy tekst jako klucz i wartość
                    self.data_to_id[item] = item  # Mapowanie 'data' -> 'ID'
                    # print(f"Dodano tekst: {item}")  # Logowanie danych

                list_item.setFlags(list_item.flags() | Qt.ItemIsUserCheckable)
                list_item.setCheckState(Qt.Unchecked)
                self.list_widget.addItem(list_item)


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
        self.list_widget.itemPressed.connect(self.toggleItemCheckState)
        self.list_widget.itemChanged.connect(self.toggleCheckboxCheckState)

        # Obsługa zmiany stanu elementów
        self.list_widget.itemChanged.connect(self.updateLineEdit)



        self.width_box = self.width()

    def showPopup(self):
        """
        Funkcja wyświetlająca menu rozwijane.
        Ustawia szerokość menu rozwijanego na szerokość QComboBox
        i wyświetla menu w lokalizacji QComboBox.
        """
        # Ustaw szerokość menu na szerokość QComboBox
        self.width_box = self.width()
        self.menu.setFixedWidth(self.width_box)  # Ustaw szerokość menu
        self.list_widget.setFixedWidth(self.width_box)  # Szerokość dopasowana do QComboBox

        self.menu.exec_(self.mapToGlobal(self.rect().bottomLeft()))

    def hidePopup(self):
        """
        Przesłonięcie funkcji hidePopup, aby zapobiec domyślnemu
        chowaniu menu, dzięki czemu można ręcznie kontrolować
        zamykanie menu rozwijanego.
        """
        pass

    def eventFilter(self, source, event):
        """
        Nasłuchiwanie kliknięcia na polu tekstowym.
        Jeśli użytkownik kliknie pole tekstowe QComboBox, wyświetlane
        jest menu rozwijane.
        """
        if event.type() == event.MouseButtonPress and source == self.lineEdit():
            self.showPopup()
        return super().eventFilter(source, event)

    def toggleItemCheckState(self, item):
        """
        Zmiana stanu checkboxa elementu.
        Jeśli checkbox elementu jest zaznaczony, odznacz go, i odwrotnie.
        """
        if item.checkState() == Qt.Checked:
            item.setCheckState(Qt.Unchecked)
        else:
            item.setCheckState(Qt.Checked)

    def toggleCheckboxCheckState(self, item):
        """
        Synchronizacja stanu zaznaczenia elementu z jego checkboxem.
        Jeśli element jest zaznaczony w checkboxie, ustawia stan selected
        na True i odwrotnie.
        """
        if item.checkState() == Qt.Checked:
            item.setSelected(True)
        else:
            item.setSelected(False)

    def updateLineEdit(self):
        """
        Aktualizowanie pola tekstowego QComboBox, aby wyświetlić
        wybrane elementy. Wybiera teksty elementów, które są zaznaczone,
        i ustawia je jako tekst w polu tekstowym.
        """
        selected_items = [item.text() for item in self.list_widget.findItems("", Qt.MatchContains)
                          if item.checkState() == Qt.Checked]
        self.lineEdit().setText(', '.join(selected_items))

    def selectedItems(self):
        """
        Zwraca listę wybranych elementów w oryginalnej strukturze (słownik 'ID': 'data').

        Returns:
            List[dict]: Lista słowników z wybranymi elementami.
        """
        selected_items = []
        for index in range(self.list_widget.count()):
            item = self.list_widget.item(index)
            if item.checkState() == Qt.Checked:
                data = item.text()  # Pobieramy 'data' (czyli tekst elementu)
                if data in self.data_to_id:
                    key = self.data_to_id[data]  # Uzyskujemy 'ID' na podstawie 'data'
                    original_item = self.items_data[key]  # Pobieramy oryginalny słownik
                    selected_items.append(original_item)  # Dodajemy oryginalny element
                else:
                    print(f"Błąd: Nie znaleziono 'data' w mapie: {data}")

        print(f"Wybrane elementy: {selected_items}")
        return selected_items

    def setSelectedItems(self, selected_items):
        """
         Ustawia zaznaczone elementy na podstawie podanej listy kluczy (ID) lub tekstów.
         Obsługuje przypadki, gdy elementy są zarówno pojedynczymi tekstami, jak i słownikami.
         """
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item_text = item.text()

            # Sprawdzamy, czy item_text jest częścią selected_items
            if item_text in selected_items:
                item.setCheckState(Qt.Checked)
            else:
                # Dla elementów, które są słownikami
                for selected_item in selected_items:
                    if isinstance(selected_item, dict):
                        # Jeśli element jest słownikiem, porównujemy 'data' z selected_item['data']
                        if 'data' in selected_item and selected_item['data'] == item_text:
                            item.setCheckState(Qt.Checked)
                            break  # Zakończ przetwarzanie, bo znaleźliśmy pasujący element
                    else:
                        # Jeśli selected_item to zwykły tekst, porównujemy z item_text
                        if selected_item == item_text:
                            item.setCheckState(Qt.Checked)
                            break

                # Jeżeli nie znaleziono dopasowania, ustawiamy stan na odznaczony
                if item.checkState() != Qt.Checked:
                    item.setCheckState(Qt.Unchecked)

        self.updateLineEdit()

    def clearItems(self):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item.setCheckState(Qt.Unchecked)
            item.setSelected(False)

        # Aktualizujemy widok
        self.updateLineEdit()



# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("Aplikacja z Polem Wielokrotnego Wyboru")
#         self.setGeometry(QtCore.QRect(100, 100, 500, 500))
#
#         # Tworzymy centralny widget i layout
#         central_widget = QWidget(self)
#         central_widget.setGeometry(QtCore.QRect(25, 50, 450, 100))
#         central_widget.setStyleSheet("""
#         QWidget {    /* Cała tabela */
#             border: 2px solid #fccccb;
#             border-radius: 15px;
#             background-color: #fff0ef;
#         }""")
#         # Tworzymy layout poziomy do umieszczenia dwóch MultiSelectComboBox.qss obok siebie
#         combo_layout = QHBoxLayout(central_widget)
#
#         items1 = []
#         # Tworzymy i dodajemy dwa MultiSelectComboBox.qss do layoutu poziomego
#         for i in range (10):
#             if i % 2:
#                 items1.append(f"Eleeeeeeeeeeeeeeeement {i}")
#             else:
#                 items1.append(f"Eleeeeeeeeement {i}")
#
#         self.multi_select_combo1 = MultiSelectComboBox.qss(items1, 200)
#         combo_layout.addWidget(self.multi_select_combo1)
#
#         items2 = ["Opcja A", "Opcja B", "Opcja C", "Opcja D", "Opcja E", "Opcja F", "Opcja G"]
#         multi_select_combo2 = MultiSelectComboBox.qss(items2, 200)
#         combo_layout.addWidget(multi_select_combo2)
#
#         button = QPushButton(self)
#         button.setGeometry(QtCore.QRect(250, 300, 100, 50))
#         button.clicked.connect(self.print_combo)
#
#
#     def print_combo(self):
#         selected_items = self.multi_select_combo1.getSelectedItems()
#
#         # Wydrukowanie zaznaczonych elementów
#         print(selected_items)  # Na przykład: ["Opcja 1", "Opcja 3"]
#
#
#
# # Uruchomienie aplikacji
# app = QApplication(sys.argv)
# window = MainWindow()
# window.show()
# sys.exit(app.exec_())