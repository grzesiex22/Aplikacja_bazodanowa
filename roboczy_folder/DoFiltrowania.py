from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QComboBox, QListWidget, QDialog, QDialogButtonBox, QVBoxLayout

class MultiSelectComboBox(QComboBox):
    def __init__(self):
        super().__init__()
        self.setEditable(True)

        # Tworzymy niestandardowy widżet rozwijany
        self.popup = QDialog(self)
        self.popup.setWindowTitle("Wybierz elementy")
        self.popup.setLayout(QVBoxLayout())

        # Utwórz QListWidget w popupie
        self.list_widget = QListWidget(self.popup)
        self.list_widget.setSelectionMode(QListWidget.MultiSelection)

        # Dodaj elementy do listy
        for i in range(10):
            self.list_widget.addItem(f"Element {i+1}")

        self.popup.layout().addWidget(self.list_widget)

        # Przyciski w oknie popup
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self.popup)
        button_box.accepted.connect(self.accept_selection)
        button_box.rejected.connect(self.popup.reject)
        self.popup.layout().addWidget(button_box)

        self.setModel(self.list_widget.model())

    def showPopup(self):
        # Pokazujemy popup zamiast standardowego rozwinięcia
        self.popup.exec_()

    def accept_selection(self):
        # Pobierz zaznaczone elementy i ustaw je w QComboBox
        selected_items = [item.text() for item in self.list_widget.selectedItems()]
        self.setCurrentText(", ".join(selected_items))
        self.popup.accept()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        # Utwórz niestandardowy QComboBox
        self.combo = MultiSelectComboBox()
        layout.addWidget(self.combo)

        self.setLayout(layout)
        self.setWindowTitle("Multi-Select ComboBox")
        self.show()


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    app.exec_()
