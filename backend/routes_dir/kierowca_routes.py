from flask import Blueprint, request, jsonify
from Aplikacja_bazodanowa.backend.database import db
from Aplikacja_bazodanowa.backend.models import Kierowca, Pojazd

# Blueprint dla kierowców
kierowca_bp = Blueprint('kierowca', __name__)

# Dodawanie nowego kierowcy
@kierowca_bp.route('/kierowca', methods=['POST'])
def dodaj_kierowce():
    data = request.get_json()
    try:
        nowy_kierowca = Kierowca(
            imie=data['imie'],
            nazwisko=data['nazwisko'],
            nrTel=data['nrTel']
        )
        db.session.add(nowy_kierowca)
        db.session.commit()
        return jsonify({'message': 'Kierowca dodany pomyślnie'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Usuwanie kierowcy
@kierowca_bp.route('/kierowca/<int:id>', methods=['DELETE'])
def usun_kierowce(id):
    try:
        kierowca = Kierowca.query.get(id)
        if kierowca is None:
            return jsonify({'message': 'Kierowca nie znaleziony'}), 404
        db.session.delete(kierowca)
        db.session.commit()
        return jsonify({'message': 'Kierowca usunięty pomyślnie'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Edytowanie danych kierowcy
@kierowca_bp.route('/kierowca/<int:id>', methods=['PUT'])
def edytuj_kierowce(id):
    data = request.get_json()
    try:
        kierowca = Kierowca.query.get(id)
        if kierowca is None:
            return jsonify({'message': 'Kierowca nie znaleziony'}), 404
        kierowca.imie = data.get('imie', kierowca.imie)
        kierowca.nazwisko = data.get('nazwisko', kierowca.nazwisko)
        kierowca.nrTel = data.get('nrTel', kierowca.nrTel)
        db.session.commit()
        return jsonify({'message': 'Dane kierowcy zaktualizowane pomyślnie'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


