import sys
import time
import multiprocessing
import requests
from Aplikacja_bazodanowa.backend.app import run_backend
from Aplikacja_bazodanowa.frontend.ui.MainWindow import MainWindow
from PyQt5 import QtWidgets
import os
import signal


# Funkcja uruchamiająca frontend (aplikację PyQt5)
def run_frontend():
    print("Waiting for backend...")
    while True:
        try:
            response = requests.get("http://127.0.0.1:5000/")  # Sprawdzanie dostępności backendu
            print(f"Server response: {response.status_code}")
            if response.status_code == 200:
                print("Backend is available, starting frontend.")
                break
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)  # Czekamy sekundę przed kolejną próbą

    # Tworzenie i uruchamianie aplikacji PyQt5
    app = QtWidgets.QApplication(sys.argv)
    api_url = "http://127.0.0.1:5000"
    window = MainWindow(api_url=api_url)

    # Dodajemy callback, aby zakończyć serwer Flask po zamknięciu GUI
    window.closeEvent = lambda event: shutdown_backend(backend_process)  # Zakończenie backendu przy zamknięciu GUI

    window.show()
    sys.exit(app.exec_())  # Uruchamiamy główną pętlę aplikacji PyQt5


# Funkcja do zamknięcia procesu backendowego Flask
def shutdown_backend(backend_process):
    print("Shutting down backend...")
    backend_process.terminate()  # Zakończenie procesu backendowego bez wysyłania sygnałów
    backend_process.join()  # Czekamy na zakończenie procesu backendowego


if __name__ == "__main__":
    print("Starting main process...")

    # Tworzymy procesy dla backendu i frontend
    backend_process = multiprocessing.Process(target=run_backend)
    frontend_process = multiprocessing.Process(target=run_frontend)

    # Uruchamiamy oba procesy
    backend_process.start()
    frontend_process.start()

    # Czekamy na zakończenie frontendowego procesu
    frontend_process.join()

    # Backend powinien zostać zamknięty, gdy frontend się zakończy
    shutdown_backend(backend_process)  # Kończymy backend po zamknięciu frontendowego okna
