from flask import Blueprint, request, jsonify
from Aplikacja_bazodanowa.backend.database import db
from Aplikacja_bazodanowa.backend.models import Kierowca, Pojazd
from Aplikacja_bazodanowa.backend.routes_dir.app_routes import get_columns

# Blueprint dla kierowców
kierowca_bp = Blueprint('kierowca', __name__)


# Pobieranie danych pojedynczego kierowcy
@kierowca_bp.route('/kierowca/<int:id>', methods=['GET'])
def pobierz_kierowce(id):
    try:
        kierowca = Kierowca.query.get(id)
        if kierowca is None:
            return jsonify({'message': 'Kierowca nie znaleziony'}), 404
        return jsonify({
            'id': kierowca.idKierowca,
            'imie': kierowca.imie,
            'nazwisko': kierowca.nazwisko,
            'nrTel': kierowca.nrTel
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@kierowca_bp.route('/kierowca+kolumny/<int:id>', methods=['GET'])
def pobierz_kierowce_z_kolumnami(id):
    try:
        # Pobierz dane kierowcy
        kierowca = Kierowca.query.get(id)
        if kierowca is None:
            return jsonify({'message': 'Kierowca nie znaleziony'}), 404

        # Pobierz metadane kolumn bezpośrednio z funkcji
        columns_info = get_columns("Kierowca").json  # Użycie funkcji bez żądania HTTP

        # Połącz dane kierowcy z informacją o typie kolumn
        kierowca_data = {
            "idKierowca": kierowca.idKierowca,
            "imie": kierowca.imie,
            "nazwisko": kierowca.nazwisko,
            "nrTel": kierowca.nrTel,
        }

        # Łączenie danych kierowcy z informacjami o kolumnach
        kierowca_with_columns = []
        for col in columns_info:
            column_name = col.get('name')
            kierowca_with_columns.append({
                "name": column_name,
                "value": kierowca_data.get(column_name),  # Pobierz wartość dla kolumny
                "primary_key": col.get('primary_key'),
                "foreign_key": col.get('foreign_key')
            })

        return jsonify(kierowca_with_columns), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Pobieranie listy wszystkich kierowców
@kierowca_bp.route('/kierowcy', methods=['GET'])
def pobierz_wszystkich_kierowcow():
    try:
        kierowcy = Kierowca.query.all()
        wynik = []
        for kierowca in kierowcy:
            wynik.append({
                'id': kierowca.idKierowca,
                'imie': kierowca.imie,
                'nazwisko': kierowca.nazwisko,
                'nrTel': kierowca.nrTel
            })
        return jsonify(wynik), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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


