class Config:
    # Konfiguracja bazy danych MySQL bez użycia pliku .env
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:bazydanych123@localhost:3306/TransportManagerDB'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
