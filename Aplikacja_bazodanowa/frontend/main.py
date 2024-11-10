import sys
from PyQt5 import QtWidgets, QtGui
from Aplikacja_bazodanowa.frontend.ui.MainWindow import MainWindow

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()  # Tworzymy instancję MainWindow
    window.show()  # Pokazujemy główne okno
    sys.exit(app.exec_())
