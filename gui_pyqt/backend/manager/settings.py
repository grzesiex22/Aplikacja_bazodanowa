# Ustawienia Django, w tym baza danych
import pymysql

pymysql.install_as_MySQLdb()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # Używamy MySQL
        'NAME': 'TransportManagerDB',          # Nazwa bazy danych
        'USER': 'root',                        # Użytkownik bazy danych
        'PASSWORD': 'hophop_123',                # Hasło użytkownika
        'HOST': 'localhost',                   # Host bazy danych (może być inny, jeśli jest zdalna)
        'PORT': '3306',                        # Port bazy danych (domyślnie 3306)
    }
}
