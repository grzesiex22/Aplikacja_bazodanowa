from database import create_app, db
from models import Kierowca, Pojzad, TypSerwisu, Serwis, Czesc
from routes import bp

app = create_app()
app.register_blueprint(bp)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
