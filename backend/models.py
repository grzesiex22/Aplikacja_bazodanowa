from Aplikacja_bazodanowa.backend.database import db

class Kierowca(db.Model):
    __tablename__ = 'Kierowca'
    idKierowca = db.Column(db.Integer, primary_key=True, autoincrement=True)
    imie = db.Column(db.String(45), nullable=False)
    nazwisko = db.Column(db.String(45), nullable=False)
    nrTel = db.Column(db.String(12), nullable=False)
    pojazdy = db.relationship('Pojzad', backref='kierowca', lazy=True)

class Pojzad(db.Model):
    __tablename__ = 'Pojzad'
    idPojazd = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idKierowca = db.Column(db.Integer, db.ForeignKey('Kierowca.idKierowca'), nullable=True)
    typPojazdu = db.Column(db.Enum('Ciągnik', 'Naczepa'), nullable=False)
    marka = db.Column(db.String(20), nullable=False)
    model = db.Column(db.String(45), nullable=False)
    nrRejestracyjny = db.Column(db.String(8), nullable=False)
    dodatkoweInf = db.Column(db.String(100), nullable=True)

class TypSerwisu(db.Model):
    __tablename__ = 'TypSerwisu'
    idTypSerwisu = db.Column(db.Integer, primary_key=True, autoincrement=True)
    rodzajSerwisu = db.Column(db.String(100), nullable=False)
    typPojazdu = db.Column(db.Enum('Ciągnik', 'Naczepa'), nullable=False)

class Serwis(db.Model):
    __tablename__ = 'Serwis'
    idSerwis = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idPojazd = db.Column(db.Integer, db.ForeignKey('Pojzad.idPojazd'), nullable=False)
    idTypSerwisu = db.Column(db.Integer, db.ForeignKey('TypSerwisu.idTypSerwisu'), nullable=False)
    data = db.Column(db.Date, nullable=False)
    cenaCzesciNetto = db.Column(db.Integer, nullable=True)
    robocizna = db.Column(db.Integer, nullable=True)
    kosztCalkowityNetto = db.Column(db.Integer, nullable=False)
    przebieg = db.Column(db.Integer, nullable=True)
    infoDodatkowe = db.Column(db.String(200), nullable=True)

class Czesc(db.Model):
    __tablename__ = 'Część'
    idCzesc = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idTypSerwisu = db.Column(db.Integer, db.ForeignKey('TypSerwisu.idTypSerwisu'), nullable=False)
    nazwaElementu = db.Column(db.String(100), nullable=False)
    ilosc = db.Column(db.Integer, nullable=False)
