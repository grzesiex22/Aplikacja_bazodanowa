import subprocess
import sys
import os
import signal
import time

def run_django_server():
    """Uruchamia serwer Django jako proces w tle."""
    return subprocess.Popen(
        [sys.executable, "manage.py", "runserver"],
        cwd="backend",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

def run_pyqt_frontend():
    """Uruchamia frontend PyQt5 jako proces."""
    return subprocess.Popen(
        [sys.executable, "main.py"],
        cwd="frontend",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

def main():

    try:
        # Uruchom serwer Django
        django_process = run_django_server()
        print("Django server started...")

        # Czekamy chwilę, aby upewnić się, że serwer Django działa
        time.sleep(2)

        # Uruchom frontend PyQt5
        pyqt_process = run_pyqt_frontend()
        print("PyQt5 frontend started...")

        # Czekamy na zakończenie procesu PyQt (zamknięcie GUI)
        pyqt_process.wait()

    finally:
        # Zamykanie serwera Django po zamknięciu PyQt5
        print("Shutting down Django server...")
        django_process.terminate()
        django_process.wait()
        print("Application closed.")

if __name__ == "__main__":
    main()
