from Aplikacja_bazodanowa.backend.database import create_app, db
from Aplikacja_bazodanowa.backend.routes import bp
from flask import Flask
import os
import signal


app = create_app()  # Tworzenie aplikacji
app.register_blueprint(bp)  # Rejestrowanie blueprintu

with app.app_context():
    db.create_all()  # Tworzenie tabel w bazie danych


# def shutdown():
#     os.kill(os.getpid(), signal.SIGINT)

def run_backend():
    print("Starting backend...")
    app = create_app()
    app.register_blueprint(bp)

    # Tworzenie tabel w bazie danych w kontekście aplikacji
    with app.app_context():
        print("Creating database tables...")
        db.create_all()

    # Uruchomienie serwera Flask na porcie 5000
    print("Flask server should now be running on port 5000...")
    app.run(debug=False, port=5000)




if __name__ == '__main__':
    # app.run(debug=True)  # Uruchomienie aplikacji
    run_backend()