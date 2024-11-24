from flask import Blueprint, request, jsonify
from Aplikacja_bazodanowa.backend.database import db
from Aplikacja_bazodanowa.backend.models import TypSerwisu
import re

# Blueprint dla TypSerwisu
typserwis_bp = Blueprint('typserwis', __name__)

# Pobieranie danych pojedynczego typu serwisu
@typserwis_bp.route('/typserwis/<int:id>', methods=['GET'])
def pobierz_typserwis(id):
    try:
        typserwis = TypSerwisu.query.get(id)
        if typserwis is None:
            return jsonify({'message': 'Typ serwisu nie znaleziony'}), 404
        return jsonify({
            'idTypSerwisu': typserwis.idTypSerwisu,
            'rodzajSerwisu': typserwis.rodzajSerwisu,
            'typPojazdu': typserwis.typPojazdu
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Pobieranie listy wszystkich typów serwisów
@typserwis_bp.route('/typserwisy', methods=['GET'])
def pobierz_wszystkie_typy_serwisow():
    try:
        typy_serwisow = TypSerwisu.query.all()
        wynik = []
        for typserwis in typy_serwisow:
            wynik.append({
                'idTypSerwisu': typserwis.idTypSerwisu,
                'rodzajSerwisu': typserwis.rodzajSerwisu,
                'typPojazdu': typserwis.typPojazdu
            })
        return jsonify(wynik), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Pobieranie listy wszystkich kierowców
@typserwis_bp.route('/typserwisu/show/alltochoice', methods=['GET'])
def pobierz_wszystkich_kierowcow_do_okna_wyboru():
    try:
        typyserwisow = TypSerwisu.query.all()
        wynik = []
        for typserwisu in typyserwisow:
            data = {'ID': typserwisu.idTypSerwisu, 'data': f"{typserwisu.rodzajSerwisu}"}
            wynik.append(data)
        return jsonify(wynik), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Dodawanie nowego typu serwisu
@typserwis_bp.route('/typserwis', methods=['POST'])
def dodaj_typserwis():
    data = request.get_json()
    try:
        # Walidacja danych wejściowych
        if 'rodzajSerwisu' not in data or not isinstance(data['rodzajSerwisu'], str):
            return jsonify({'message': 'Rodzaj serwisu musi być ciągiem znaków'}), 400
        if 'typPojazdu' not in data or data['typPojazdu'] not in ['Ciągnik', 'Naczepa']:
            return jsonify({'message': 'Typ pojazdu musi być "Ciągnik" lub "Naczepa"'}), 400

        nowy_typserwis = TypSerwisu(
            rodzajSerwisu=data['rodzajSerwisu'],
            typPojazdu=data['typPojazdu']
        )
        db.session.add(nowy_typserwis)
        db.session.commit()
        return jsonify({'message': 'Typ serwisu dodany pomyślnie'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Usuwanie typu serwisu
@typserwis_bp.route('/typserwis/<int:id>', methods=['DELETE'])
def usun_typserwis(id):
    try:
        typserwis = TypSerwisu.query.get(id)
        if typserwis is None:
            return jsonify({'message': 'Typ serwisu nie znaleziony'}), 404
        db.session.delete(typserwis)
        db.session.commit()
        return jsonify({'message': 'Typ serwisu usunięty pomyślnie'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Edytowanie danych typu serwisu
@typserwis_bp.route('/typserwis/<int:id>', methods=['PUT'])
def edytuj_typserwis(id):
    data = request.get_json()
    try:
        typserwis = TypSerwisu.query.get(id)
        if typserwis is None:
            return jsonify({'message': 'Typ serwisu nie znaleziony'}), 404

        # Walidacja danych wejściowych
        if 'rodzajSerwisu' in data and not isinstance(data['rodzajSerwisu'], str):
            return jsonify({'message': 'Rodzaj serwisu musi być ciągiem znaków'}), 400
        if 'typPojazdu' in data and data['typPojazdu'] not in ['Ciągnik', 'Naczepa']:
            return jsonify({'message': 'Typ pojazdu musi być "Ciągnik" lub "Naczepa"'}), 400

        typserwis.rodzajSerwisu = data.get('rodzajSerwisu', typserwis.rodzajSerwisu)
        typserwis.typPojazdu = data.get('typPojazdu', typserwis.typPojazdu)
        db.session.commit()

        return jsonify({'message': 'Typ serwisu zaktualizowany pomyślnie'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500



@typserwis_bp.route('/typserwis/show/alltochoice', methods=['GET'])
def pobierz_wszystkie_pojazdy_do_okna_wyboru():
    try:
        typySerwisu = TypSerwisu.query.order_by(TypSerwisu.typPojazdu.asc(), TypSerwisu.rodzajSerwisu.asc()).all()
        wynik = []
        for typSerwisu in typySerwisu:
            if typSerwisu.rodzajSerwisu != 'Wyposażenie':
                data = {'ID': typSerwisu.idTypSerwisu, 'data': f"{typSerwisu.typPojazdu}, {typSerwisu.rodzajSerwisu}"}
                wynik.append(data)
        return jsonify(wynik), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
