from flask import Blueprint, request, jsonify
from Aplikacja_bazodanowa.backend.database import db
from Aplikacja_bazodanowa.backend.models import Czesc, TypSerwisu
import re

# Blueprint dla Części
czesc_bp = Blueprint('czesc', __name__)


@czesc_bp.route('/czesc/<int:id>', methods=['GET'])
def pobierz_czesc(id):
    try:
        czesc = Czesc.query.get(id)
        if czesc is None:
            return jsonify({'message': 'Część nie znaleziona'}), 404

        # Pobieramy dane typu serwisu na podstawie idTypSerwisu
        typ_serwisu = TypSerwisu.query.get(czesc.idTypSerwisu) if czesc.idTypSerwisu else None
        typ_serwisu_nazwa = typ_serwisu.rodzajSerwisu if typ_serwisu else "Brak typu serwisu"
        typ_serwisu_pojazd = typ_serwisu.typPojazdu if typ_serwisu else ""

        return jsonify({
            'ID części': czesc.idCzesc,
            'idTypSerwisu': czesc.idTypSerwisu,
            'Typ Serwisu': f"{typ_serwisu_pojazd}, {typ_serwisu_nazwa}",  # Zwracamy nazwę typu serwisu
            'Nazwa elementu': czesc.nazwaElementu,
            'Ilość': czesc.ilosc
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ############# np:     http://127.0.0.1:5000/czesci?nazwaElementu=op
# # Pobieranie listy części, z możliwością wyszukiwania po nazwie i typie serwisu
# @czesc_bp.route('/czesci', methods=['GET'])
# def pobierz_wszystkie_czesci():
#     try:
#         # Pobieranie parametrów 'nazwaElementu' i 'idTypSerwisu' z zapytania
#         nazwa_elementu = request.args.get('nazwaElementu', '').strip()
#         id_typ_serwisu = request.args.get('idTypSerwisu', None)
#         exclude_id_typ_serwisu = request.args.get('excludeIdTypSerwisu', None)
#
#         # Filtruj części po nazwie, jeśli podano 'nazwaElementu'
#         query = Czesc.query
#         if nazwa_elementu:
#             query = query.filter(Czesc.nazwaElementu.ilike(f'%{nazwa_elementu}%'))
#
#         # Filtruj części po typie serwisu, jeśli podano 'idTypSerwisu'
#         if id_typ_serwisu:
#             query = query.filter(Czesc.idTypSerwisu == int(id_typ_serwisu))
#
#         # Filtruj części, aby wykluczyć określony 'idTypSerwisu', jeśli podano 'excludeIdTypSerwisu'
#         if exclude_id_typ_serwisu:
#             query = query.filter(Czesc.idTypSerwisu != int(exclude_id_typ_serwisu))
#
#         # Pobierz wyniki zapytania
#         czesci = query.all()
#
#         wynik = []
#         for czesc in czesci:
#             # Pobranie typu serwisu na podstawie idTypSerwisu
#             typ_serwisu = TypSerwisu.query.get(czesc.idTypSerwisu) if czesc.idTypSerwisu else None
#             typ_serwisu_nazwa = typ_serwisu.rodzajSerwisu if typ_serwisu else "Brak typu serwisu"
#
#             wynik.append({
#                 'idCzesc': czesc.idCzesc,
#                 'typSerwisu': typ_serwisu_nazwa,  # Wyświetlamy nazwę typu serwisu
#                 'nazwaElementu': czesc.nazwaElementu,
#                 'ilosc': czesc.ilosc
#             })
#
#         return jsonify(wynik), 200
#
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


# Pobieranie listy części, z możliwością wyszukiwania, filtrowania, i sortowania
@czesc_bp.route('/czesci', methods=['GET'])
def pobierz_wszystkie_czesci():
    try:
        # Pobieranie parametrów z zapytania
        nazwa_elementu = request.args.get('nazwaElementu', '').strip()
        id_typ_serwisu = request.args.get('idTypSerwisu', None)
        include_typ_serwisu = request.args.get('includeTypSerwisu', None)  # Uwzględnienie tylko określonych serwisów
        # exclude_id_typ_serwisu = request.args.get('excludeIdTypSerwisu', None)
        exclude_typ_serwisu = request.args.get('excludeTypSerwisu', None)  # Zmieniona nazwa parametru
        sort_by = request.args.get('sort_by', 'nazwaElementu')  # Domyślnie sortowanie po nazwie elementu
        order = request.args.get('order', 'asc')  # Domyślnie sortowanie rosnące

        # Filtruj części po nazwie, jeśli podano 'nazwaElementu'
        query = Czesc.query
        if nazwa_elementu:
            query = query.filter(Czesc.nazwaElementu.ilike(f'%{nazwa_elementu}%'))

        # Filtruj części po typie serwisu, jeśli podano 'idTypSerwisu'
        if id_typ_serwisu:
            query = query.filter(Czesc.idTypSerwisu == int(id_typ_serwisu))

        # # Filtruj części, aby wykluczyć określony 'idTypSerwisu', jeśli podano 'excludeIdTypSerwisu'
        # if exclude_id_typ_serwisu:
        #     query = query.filter(Czesc.idTypSerwisu != int(exclude_id_typ_serwisu))
        #
        # Jeśli podano 'excludeTypSerwisu', wyszukaj idTypSerwisu dla podanego rodzaju serwisu
        if exclude_typ_serwisu:
            # Wyszukaj idTypSerwisu pasujące do podanego rodzaju serwisu
            typy_serwisu = TypSerwisu.query.filter(TypSerwisu.rodzajSerwisu.ilike(f'%{exclude_typ_serwisu}%')).all()
            exclude_ids = [typ.idTypSerwisu for typ in typy_serwisu]

            if exclude_ids:
                query = query.filter(~Czesc.idTypSerwisu.in_(exclude_ids))

        # Jeśli podano 'includeTypSerwisu', wyszukaj idTypSerwisu dla podanego rodzaju serwisu
        if include_typ_serwisu:
            typy_serwisu = TypSerwisu.query.filter(TypSerwisu.rodzajSerwisu.ilike(f'%{include_typ_serwisu}%')).all()
            include_ids = [typ.idTypSerwisu for typ in typy_serwisu]

            if include_ids:
                query = query.filter(Czesc.idTypSerwisu.in_(include_ids))

        # Dodaj sortowanie
        if sort_by in ['nazwaElementu', 'ilosc']:
            # Sortowanie po dozwolonych kolumnach
            sort_column = getattr(Czesc, sort_by, Czesc.nazwaElementu)
            if order == 'desc':
                sort_column = sort_column.desc()
            query = query.order_by(sort_column)

        # Pobierz wyniki zapytania
        czesci = query.all()

        wynik = []
        for czesc in czesci:
            # Pobranie typu serwisu na podstawie idTypSerwisu
            typ_serwisu = TypSerwisu.query.get(czesc.idTypSerwisu) if czesc.idTypSerwisu else None
            typ_serwisu_nazwa = typ_serwisu.rodzajSerwisu if typ_serwisu else "Brak typu serwisu"
            typ_serwisu_pojazd = typ_serwisu.typPojazdu if typ_serwisu else ""

            wynik.append({
                'idCzesc': czesc.idCzesc,
                'idTypSerwisu': czesc.idTypSerwisu,
                'typSerwisu': str(typ_serwisu_pojazd + ", " + typ_serwisu_nazwa),  # Wyświetlamy nazwę typu serwisu
                'nazwaElementu': czesc.nazwaElementu,
                'ilosc': czesc.ilosc
            })

        return jsonify(wynik), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# # Dodawanie nowego kierowcy
# @czesc_bp.route('/czesc/add', methods=['POST'])
# def dodaj_czesc():
#     data = request.get_json()
#
#     # Deserializacja danych wejściowych
#     deserialized_data = Czesc.deserialize(data)
#     # Tworzenie obiektu Kierowca na podstawie deserializowanych danych
#     nowa_czesc = Czesc(**deserialized_data)
#
#     print(nowa_czesc)
#
#     try:
#         db.session.add(nowa_czesc)
#         db.session.commit()
#         return jsonify({'message': 'Czesc dodana pomyślnie'}), 201
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({'error': str(e)}), 500

@czesc_bp.route('/czesc/add', methods=['POST'])
def dodaj_czesc():
    data = request.get_json()

    try:
        # Tworzenie obiektu Czesc na podstawie danych
        id_typ_serwisu = int(data['idTypSerwisu'])
        nazwa_elementu = data['Nazwa elementu']
        ilosc = int(data['Ilość'])

        # Sprawdzenie, czy część już istnieje w tabeli
        istnieje_czesc = Czesc.query.filter_by(idTypSerwisu=id_typ_serwisu, nazwaElementu=nazwa_elementu).first()

        if istnieje_czesc:
            # Jeśli część istnieje, zwiększamy wartość pola 'ilosc'
            istnieje_czesc.ilosc += ilosc
        else:
            # Jeśli część nie istnieje, tworzymy nową
            nowa_czesc = Czesc(
                idTypSerwisu=id_typ_serwisu,
                nazwaElementu=nazwa_elementu,
                ilosc=ilosc
            )
            db.session.add(nowa_czesc)
        db.session.commit()

        return jsonify({'message': 'Część dodana pomyślnie'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@czesc_bp.route('/czesc/validate', methods=['POST'])
def validate_czesc():
    data = request.get_json()

    # Walidacja danych wejściowych
    if 'Nazwa elementu' not in data or not isinstance(data['Nazwa elementu'], str):
        return jsonify({'message': 'Nazwa elementu musi być ciągiem znaków'}), 400

    # Sprawdzenie długości nazwy elementu
    if len(data['Nazwa elementu']) > 100:
        return jsonify({'message': 'Nazwa elementu nie może mieć więcej niż 100 znaków'}), 400

    if 'Ilość' not in data or not isinstance(data['Ilość'], int):
        return jsonify({'message': 'Ilość musi być liczbą całkowitą'}), 400

    # if 'Dane Typ serwisu' not in data or not isinstance(data['Dane Typ serwisu'], str):
    #     return jsonify({'message': 'Dane Typ serwisu musi być ciągiem znaków'}), 400

    # Walidacja idTypSerwisu
    if 'idTypSerwisu' not in data:
        return jsonify({'message': 'Wybierz typ serwisu'}), 400

    return jsonify({'message': 'Dane są poprawne'}), 200


# Usuwanie części
@czesc_bp.route('/czesc/delete/<int:id>', methods=['DELETE'])
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


@czesc_bp.route('/czesc/edit/<int:id>', methods=['PUT'])
def edytuj_czesc(id):
    data = request.get_json()

    try:
        # Pobranie obiektu Czesc z bazy danych
        czesc = Czesc.query.get(id)
        if czesc is None:
            return jsonify({'message': 'Część nie znaleziona'}), 404

        id_typ_serwisu = int(data['idTypSerwisu'])
        czesc.idTypSerwisu = id_typ_serwisu  # Przypisanie powiązania do nowego obiektu TypSerwisu

        # Aktualizacja pól, jeśli są obecne w danych wejściowych
        czesc.nazwaElementu = data.get('Nazwa elementu', czesc.nazwaElementu)
        czesc.ilosc = data.get('Ilość', czesc.ilosc)

        # Zapisanie zmian w bazie danych
        db.session.commit()

        return jsonify({'message': 'Część zaktualizowana pomyślnie'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@czesc_bp.route('/czesc/check', methods=['POST'])
def sprawdz_czesc():
    try:
        data = request.get_json()

        # Walidacja danych wejściowych
        if 'Nazwa elementu' not in data or 'idTypSerwisu' not in data:
            return jsonify({'error': 'Nazwa elementu i idTypSerwisu są wymagane'}), 400

        nazwa = data['Nazwa elementu']
        id_typ_serwisu = data['idTypSerwisu']

        # Wyszukiwanie części w bazie danych
        czesc = Czesc.query.filter_by(nazwaElementu=nazwa, idTypSerwisu=id_typ_serwisu).first()

        # Zwracanie wyniku
        if czesc:
            return jsonify({'idCzesc': czesc.idCzesc}), 200
        else:
            return jsonify({'idCzesc': None}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
