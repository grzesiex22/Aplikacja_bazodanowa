from Aplikacja_bazodanowa.backend.database import create_app, db
from Aplikacja_bazodanowa.backend.routes import bp

app = create_app()  # Tworzenie aplikacji
app.register_blueprint(bp)  # Rejestrowanie blueprintu

with app.app_context():
    db.create_all()  # Tworzenie tabel w bazie danych

if __name__ == '__main__':
    app.run(debug=True)  # Uruchomienie aplikacji