from PyQt5.QtWidgets import QLineEdit

class DateLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("Wprowadź datę (dd-mm-yyyy)")

        # Zmienna pomocnicza do śledzenia stanu maski
        self.mask_set = False

        # Łączymy sygnał zmiany tekstu z metodą
        self.textChanged.connect(self.on_date_changed)

    def on_date_changed(self, text):
        """
        Metoda wywoływana za każdym razem, gdy tekst w QLineEdit się zmienia.
        Ustawia maskę na '00-00-0000', gdy zaczynasz wpisywać datę, i usuwa ją, gdy pole jest puste.
        """
        if len(text) > 0 and not self.mask_set:
            self.setInputMask("00-00-0000")  # Ustawienie maski na 'dd-mm-yyyy'
            self.mask_set = True  # Zmieniamy stan maski na aktywowany
        elif len(text) == 0 and self.mask_set:
            self.setInputMask("")  # Usuwamy maskę, jeśli pole jest puste
            self.mask_set = False  # Zmieniamy stan maski na usunięty
            self.setPlaceholderText("Wprowadź datę (dd-mm-yyyy)")  # Przywracamy placeholder

    def focusInEvent(self, event):
        """
        Metoda, która jest wywoływana, kiedy pole staje się aktywne.
        Jeśli pole było puste i zaczynasz wpisywać dane, maska jest ustawiana.
        """
        if not self.mask_set and self.text() == "":
            self.setInputMask("00-00-0000")  # Ustawienie maski, jeśli pole jest puste
            self.mask_set = True
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        """
        Metoda, która jest wywoływana, kiedy pole przestaje być aktywne.
        Jeśli pole jest puste, maska jest usuwana.
        """
        if self.text().strip() == "--":  # Sprawdzamy, czy pole jest puste
            self.setInputMask("")  # Usuwamy maskę, jeśli pole jest puste
            self.mask_set = False
            self.setPlaceholderText("Wprowadź datę (dd-mm-yyyy)")  # Przywracamy placeholder
        super().focusOutEvent(event)

    def clear(self):
        self.setInputMask("")  # Usuwamy maskę, jeśli pole jest puste
        self.setText("")

