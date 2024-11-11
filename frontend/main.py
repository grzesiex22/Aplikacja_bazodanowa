import sys
from PyQt5 import QtWidgets, QtGui
from Aplikacja_bazodanowa.frontend.ui.MainWindow import MainWindow

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    api_url = "http://127.0.0.1:5000"
    window = MainWindow(api_url=api_url)  # Tworzymy instancję MainWindow
    window.show()  # Pokazujemy główne okno
    sys.exit(app.exec_())
