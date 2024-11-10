from flask import Blueprint, request, jsonify
from Aplikacja_bazodanowa.backend.database import db
from Aplikacja_bazodanowa.backend.models import Czesc, TypSerwisu
import re

# Blueprint dla Części
czesc_bp = Blueprint('czesc', __name__)


# Pobieranie danych pojedynczej części
@czesc_bp.route('/czesc/<int:id>', methods=['GET'])
def pobierz_czesc(id):
    try:
        czesc = Czesc.query.get(id)
        if czesc is None:
            return jsonify({'message': 'Część nie znaleziona'}), 404
        return jsonify({
            'idCzesc': czesc.idCzesc,
            'idTypSerwisu': czesc.idTypSerwisu,
            'nazwaElementu': czesc.nazwaElementu,
            'ilosc': czesc.ilosc
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

############# np:     http://127.0.0.1:5000/czesci?nazwaElementu=op
# Pobieranie listy części, z możliwością wyszukiwania po nazwie i typie serwisu
@czesc_bp.route('/czesci', methods=['GET'])
def pobierz_wszystkie_czesci():
    try:
        # Pobieranie parametrów 'nazwaElementu' i 'idTypSerwisu' z zapytania
        nazwa_elementu = request.args.get('nazwaElementu', '').strip()
        id_typ_serwisu = request.args.get('idTypSerwisu', None)

        # Filtruj części po nazwie, jeśli podano 'nazwaElementu'
        query = Czesc.query
        if nazwa_elementu:
            query = query.filter(Czesc.nazwaElementu.ilike(f'%{nazwa_elementu}%'))

        # Filtruj części po typie serwisu, jeśli podano 'idTypSerwisu'
        if id_typ_serwisu:
            query = query.filter(Czesc.idTypSerwisu == int(id_typ_serwisu))

        # Pobierz wyniki zapytania
        czesci = query.all()

        wynik = []
        for czesc in czesci:
            wynik.append({
                'idCzesc': czesc.idCzesc,
                'idTypSerwisu': czesc.idTypSerwisu,
                'nazwaElementu': czesc.nazwaElementu,
                'ilosc': czesc.ilosc
            })

        return jsonify(wynik), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Dodawanie nowej części
@czesc_bp.route('/czesc', methods=['POST'])
def dodaj_czesc():
    data = request.get_json()
    try:
        # Walidacja danych wejściowych
        if 'nazwaElementu' not in data or not isinstance(data['nazwaElementu'], str):
            return jsonify({'message': 'Nazwa elementu musi być ciągiem znaków'}), 400
        if 'ilosc' not in data or not isinstance(data['ilosc'], int):
            return jsonify({'message': 'Ilość musi być liczbą całkowitą'}), 400
        if 'idTypSerwisu' not in data or not isinstance(data['idTypSerwisu'], int):
            return jsonify({'message': 'IdTypSerwisu musi być liczbą całkowitą'}), 400

        # Sprawdzanie czy idTypSerwisu istnieje w tabeli TypSerwisu
        typ_serwis = TypSerwisu.query.get(data['idTypSerwisu'])
        if not typ_serwis:
            return jsonify({'message': 'Typ serwisu nie istnieje'}), 404

        nowa_czesc = Czesc(
            idTypSerwisu=data['idTypSerwisu'],
            nazwaElementu=data['nazwaElementu'],
            ilosc=data['ilosc']
        )
        db.session.add(nowa_czesc)
        db.session.commit()
        return jsonify({'message': 'Część dodana pomyślnie'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# Usuwanie części
@czesc_bp.route('/czesc/<int:id>', methods=['DELETE'])
def usun_czesc(id):
    try:
        czesc = Czesc.query.get(id)
        if czesc is None:
            return jsonify({'message': 'Część nie znaleziona'}), 404
        db.session.delete(czesc)
        db.session.commit()
        return jsonify({'message': 'Część usunięta pomyślnie'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# Edytowanie danych części
@czesc_bp.route('/czesc/<int:id>', methods=['PUT'])
def edytuj_czesc(id):
    data = request.get_json()
    try:
        czesc = Czesc.query.get(id)
        if czesc is None:
            return jsonify({'message': 'Część nie znaleziona'}), 404

        # Walidacja danych wejściowych
        if 'nazwaElementu' in data and not isinstance(data['nazwaElementu'], str):
            return jsonify({'message': 'Nazwa elementu musi być ciągiem znaków'}), 400
        if 'ilosc' in data and not isinstance(data['ilosc'], int):
            return jsonify({'message': 'Ilość musi być liczbą całkowitą'}), 400
        if 'idTypSerwisu' in data and not isinstance(data['idTypSerwisu'], int):
            return jsonify({'message': 'IdTypSerwisu musi być liczbą całkowitą'}), 400

        # Sprawdzanie czy idTypSerwisu istnieje w tabeli TypSerwisu
        if 'idTypSerwisu' in data:
            typ_serwis = TypSerwisu.query.get(data['idTypSerwisu'])
            if not typ_serwis:
                return jsonify({'message': 'Typ serwisu nie istnieje'}), 404
            czesc.idTypSerwisu = data['idTypSerwisu']

        czesc.nazwaElementu = data.get('nazwaElementu', czesc.nazwaElementu)
        czesc.ilosc = data.get('ilosc', czesc.ilosc)

        db.session.commit()

        return jsonify({'message': 'Część zaktualizowana pomyślnie'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
