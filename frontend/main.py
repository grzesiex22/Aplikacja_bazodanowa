import sys
from PyQt5 import QtWidgets
from frontend.ui.main_window import MainWindow

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()  # Tworzymy instancję MainWindow
    window.show()  # Pokazujemy główne okno
    sys.exit(app.exec_())
