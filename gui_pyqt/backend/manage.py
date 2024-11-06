import os
import sys

def main():
    # Ustawienie zmiennej środowiskowej DJANGO_SETTINGS_MODULE
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "manager.settings")

    try:
        # Importowanie i uruchamianie komend Django
        from django.core.management import execute_from_command_line
    except ImportError:
        # W przypadku błędów z importem, zapisz informację o błędzie
        try:
            import django
        except ImportError:
            raise ImportError(
                "Nie można zaimportować Django. Upewnij się, że masz zainstalowane Django w swoim środowisku."
            )
        raise
    # Wykonanie komendy z linii poleceń
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()