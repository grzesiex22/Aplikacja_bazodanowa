from flask import Blueprint, jsonify, request
from Aplikacja_bazodanowa.backend.database import db
from Aplikacja_bazodanowa.backend.models import Kierowca, Pojzad

kierowca_bp = Blueprint('kierowca_api', __name__)

# Pobierz wszystkich kierowców
@kierowca_bp.route('/api/kierowcy', methods=['GET'])
def get_kierowcy():
    kierowcy = Kierowca.query.all()
    return jsonify([{"id": k.idKierowca, "imie": k.imie, "nazwisko": k.nazwisko, "nrTel": k.nrTel} for k in kierowcy])

# Dodaj nowego kierowcę
@kierowca_bp.route('/api/kierowcy', methods=['POST'])
def add_kierowca():
    data = request.get_json()
    imie = data.get('imie')
    nazwisko = data.get('nazwisko')
    nrTel = data.get('nrTel')

    if not imie or not nazwisko or not nrTel:
        return jsonify({"error": "Brak wymaganych pól"}), 400

    kierowca = Kierowca(imie=imie, nazwisko=nazwisko, nrTel=nrTel)
    db.session.add(kierowca)
    db.session.commit()

    return jsonify({"id": kierowca.idKierowca, "imie": kierowca.imie, "nazwisko": kierowca.nazwisko, "nrTel": kierowca.nrTel}), 201

# Zaktualizuj dane kierowcy
@kierowca_bp.route('/api/kierowcy/<int:id>', methods=['PUT'])
def update_kierowca(id):
    data = request.get_json()
    kierowca = Kierowca.query.get(id)

    if not kierowca:
        return jsonify({"error": "Kierowca nie znaleziony"}), 404

    kierowca.imie = data.get('imie', kierowca.imie)
    kierowca.nazwisko = data.get('nazwisko', kierowca.nazwisko)
    kierowca.nrTel = data.get('nrTel', kierowca.nrTel)

    db.session.commit()

    return jsonify({"id": kierowca.idKierowca, "imie": kierowca.imie, "nazwisko": kierowca.nazwisko, "nrTel": kierowca.nrTel})

# Usuń kierowcę
@kierowca_bp.route('/api/kierowcy/<int:id>', methods=['DELETE'])
def delete_kierowca(id):
    kierowca = Kierowca.query.get(id)

    if not kierowca:
        return jsonify({"error": "Kierowca nie znaleziony"}), 404

    db.session.delete(kierowca)
    db.session.commit()

    return jsonify({"message": "Kierowca usunięty pomyślnie"}), 200

# Przypisz kierowcę do pojazdu
@kierowca_bp.route('/api/kierowcy/<int:id_kierowca>/przypisz_pojazd/<int:id_pojazd>', methods=['PUT'])
def assign_kierowca_to_pojazd(id_kierowca, id_pojazd):
    try:
        kierowca = Kierowca.query.get(id_kierowca)
        pojazd = Pojzad.query.get(id_pojazd)

        if not kierowca:
            return jsonify({"error": "Kierowca nie znaleziony"}), 404

        if not pojazd:
            return jsonify({"error": "Pojazd nie znaleziony"}), 404

        # Sprawdzenie poprawności relacji przed przypisaniem
        pojazd.idKierowca = kierowca.idKierowca
        db.session.commit()

        return jsonify({"message": f"Kierowca {kierowca.imie} {kierowca.nazwisko} przypisany do pojazdu {pojazd.marka} {pojazd.model}."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Wystąpił błąd: {str(e)}"}), 500