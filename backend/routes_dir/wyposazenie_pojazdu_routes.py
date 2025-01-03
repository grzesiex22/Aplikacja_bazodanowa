from flask import Blueprint, request, jsonify
from sqlalchemy import asc, desc

from Aplikacja_bazodanowa.backend.database import db
from Aplikacja_bazodanowa.backend.models import WyposazeniePojazdu, Pojazd

# Blueprint dla Wyposażenia Pojazdu
wyposazenie_bp = Blueprint('wyposazenie', __name__)


# Pobieranie szczegółowych informacji o wyposażeniu pojazdu
@wyposazenie_bp.route('/wyposazenie/show/<int:id>', methods=['GET'])
def pobierz_wyposazenie(id):
    try:
        wyposazenie = WyposazeniePojazdu.query.get(id)
        if wyposazenie is None:
            return jsonify({'message': 'Wyposażenie pojazdu nie znalezione'}), 404

        # Pobieramy dane pojazdu
        pojazd = Pojazd.query.get(wyposazenie.idPojazd) if wyposazenie.idPojazd else None
        pojazd_opis = f"{pojazd.typPojazdu.value}, {pojazd.marka}, {pojazd.model}, nr rej. {pojazd.nrRejestracyjny}" if pojazd else "Brak pojazdu"

        # Zwracamy szczegółowe dane wyposażenia
        return jsonify({
            'ID Wyposażenia Pojazdu': wyposazenie.idWyposazeniePojazdu,
            'ID Pojazdu': wyposazenie.idPojazd,
            'Pojazd': pojazd_opis,
            'Opis': wyposazenie.opis,
            'Ilość': wyposazenie.ilosc
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Pobieranie listy wyposażenia pojazdu z możliwością filtrowania i sortowania
@wyposazenie_bp.route('/wyposazenie/show/all', methods=['GET'])
def pobierz_wszystkie_wyposazenie():
    try:
        # Pobieranie parametrów zapytania
        opis = request.args.get('opis', '').strip()
        id_pojazd = request.args.get('idPojazd', None)
        sort_by = request.args.get('sort_by', 'opis')  # Domyślnie sortowanie po opisie
        order = request.args.get('order', 'asc')  # Domyślnie sortowanie rosnące

        # Tworzenie zapytania
        query = WyposazeniePojazdu.query

        # Filtracja po opisie
        if opis:
            query = query.filter(WyposazeniePojazdu.opis.ilike(f'%{opis}%'))

        # Filtracja po ID pojazdu
        if id_pojazd:
            query = query.filter(WyposazeniePojazdu.idPojazd == int(id_pojazd))

        # Sortowanie wyników
        if sort_by in ['opis', 'ilosc']:
            sort_column = getattr(WyposazeniePojazdu, sort_by, WyposazeniePojazdu.opis)
            query = query.order_by(sort_column.desc() if order == 'desc' else sort_column)
        if sort_by == "idPojazd":
            print("sort_by idPojazd")
            kierunek_sortowania = asc if order == 'asc' else desc  # Ustalanie kierunku sortowania
            # Sortowanie po imieniu i nazwisku kierowcy
            query = query.join(Pojazd, WyposazeniePojazdu.idPojazd == Pojazd.idPojazd, isouter=True)
            query = query.order_by(
                kierunek_sortowania(Pojazd.typPojazdu),
                kierunek_sortowania(Pojazd.marka),
                kierunek_sortowania(Pojazd.model),
                kierunek_sortowania(Pojazd.nrRejestracyjny)
            )

        # Pobieranie wyników
        wyposazenie_list = query.all()

        # Tworzenie listy wyników
        wynik = []
        for wyposazenie in wyposazenie_list:
            pojazd = Pojazd.query.get(wyposazenie.idPojazd) if wyposazenie.idPojazd else None
            pojazd_opis = f"{pojazd.typPojazdu.value}, {pojazd.marka}, {pojazd.model}, nr rej. {pojazd.nrRejestracyjny}" if pojazd else "Brak pojazdu"
            wynik.append({
                'ID Wyposażenia Pojazdu': wyposazenie.idWyposazeniePojazdu,
                'ID Pojazdu': wyposazenie.idPojazd,
                'Pojazd': pojazd_opis,
                'Opis': wyposazenie.opis,
                'Ilość': wyposazenie.ilosc
            })

        return jsonify(wynik), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Dodawanie nowego wyposażenia pojazdu
# @wyposazenie_bp.route('/wyposazenie/add', methods=['POST'])
# def dodaj_wyposazenie():
#     try:
#         data = request.get_json()
#
#         # Tworzenie obiektu WyposazeniePojazdu na podstawie danych
#         nowe_wyposazenie = WyposazeniePojazdu(
#             idPojazd=int(data['ID Pojazdu']),
#             opis=data['Opis'],
#             ilosc=int(data['Ilość'])
#         )
#
#         # Dodanie do bazy danych
#         db.session.add(nowe_wyposazenie)
#         db.session.commit()
#
#         return jsonify({'message': 'Wyposażenie pojazdu dodane pomyślnie'}), 201
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({'error': str(e)}), 500


@wyposazenie_bp.route('/wyposazenie/add', methods=['POST'])
def dodaj_wyposazenie():
    try:
        data = request.get_json()

        # Tworzenie obiektu WyposazeniePojazdu na podstawie danych
        id_pojazd = int(data['ID Pojazdu'])
        opis = data['Opis']
        ilosc = int(data['Ilość'])

        # Sprawdzenie, czy wyposażenie już istnieje w tabeli
        istnieje_wyposazenie = WyposazeniePojazdu.query.filter_by(idPojazd=id_pojazd, opis=opis).first()

        if istnieje_wyposazenie:
            # Jeśli wyposażenie istnieje, zwiększamy wartość pola 'ilosc'
            istnieje_wyposazenie.ilosc += ilosc
        else:
            # Jeśli wyposażenie nie istnieje, tworzymy nowe
            nowe_wyposazenie = WyposazeniePojazdu(
                idPojazd=id_pojazd,
                opis=opis,
                ilosc=ilosc
            )
            db.session.add(nowe_wyposazenie)

        # Zapisujemy zmiany w bazie danych
        db.session.commit()

        return jsonify({'message': 'Wyposażenie pojazdu zostało dodane lub zaktualizowane pomyślnie'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# Walidacja danych wejściowych
@wyposazenie_bp.route('/wyposazenie/validate', methods=['POST'])
def validate_wyposazenie():
    try:
        data = request.get_json()

        # Walidacja opisu
        if 'Opis' not in data or not isinstance(data['Opis'], str) or not data['Opis'].strip() or len(
                data['Opis']) > 100:
            return jsonify({'message': 'Opis musi być niepustym ciągiem znaków o długości maksymalnie 100'}), 400

        # Walidacja ilości
        if 'Ilość' not in data or not isinstance(data['Ilość'], int) or data['Ilość'] < 0:
            return jsonify({'message': 'Ilość musi być liczbą całkowitą większą lub równą 0'}), 400

        # Walidacja ID pojazdu
        if 'ID Pojazdu' not in data or not data['ID Pojazdu']:
            return jsonify({'message': 'Musisz wybrać pojazd'}), 400

        if not Pojazd.query.get(int(data['ID Pojazdu'])):
            return jsonify({'message': 'Musisz wybrać pojazd'}), 400

        return jsonify({'message': 'Dane są poprawne'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Walidacja danych wejściowych
@wyposazenie_bp.route('/wyposazenie/edit/validate', methods=['POST'])
def validate_wyposazenie_edit():
    try:
        data = request.get_json()

        # Walidacja opisu
        if 'Opis' not in data or not isinstance(data['Opis'], str) or not data['Opis'].strip() or len(
                data['Opis']) > 100:
            return jsonify({'message': 'Opis musi być niepustym ciągiem znaków o długości maksymalnie 100'}), 400

        # Walidacja ilości
        if 'Ilość' not in data or not isinstance(data['Ilość'], int) or data['Ilość'] < 0:
            return jsonify({'message': 'Ilość musi być liczbą całkowitą większą lub równą 0'}), 400

        # Walidacja ID pojazdu
        if 'ID Pojazdu' not in data or not data['ID Pojazdu']:
            return jsonify({'message': 'Musisz podać ID pojazdu'}), 400

        if not Pojazd.query.get(int(data['ID Pojazdu'])):
            return jsonify({'message': 'Podano nieprawidłowe ID pojazdu'}), 400

        return jsonify({'message': 'Dane są poprawne'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Usuwanie wyposażenia pojazdu
@wyposazenie_bp.route('/wyposazenie/delete/<int:id>', methods=['DELETE'])
def usun_wyposazenie(id):
    try:
        wyposazenie = WyposazeniePojazdu.query.get(id)
        if wyposazenie is None:
            return jsonify({'message': 'Wyposażenie pojazdu nie znalezione'}), 404

        db.session.delete(wyposazenie)
        db.session.commit()

        return jsonify({'message': 'Wyposażenie pojazdu usunięte pomyślnie'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# Edytowanie wyposażenia pojazdu
@wyposazenie_bp.route('/wyposazenie/edit/<int:id>', methods=['PUT'])
def edytuj_wyposazenie(id):
    try:
        data = request.get_json()

        # Pobranie wyposażenia pojazdu
        wyposazenie = WyposazeniePojazdu.query.get(id)
        if wyposazenie is None:
            return jsonify({'message': 'Wyposażenie pojazdu nie znalezione'}), 404

        # Aktualizacja pól
        wyposazenie.idPojazd = int(data.get('ID Pojazdu', wyposazenie.idPojazd))
        wyposazenie.opis = data.get('Opis', wyposazenie.opis)
        wyposazenie.ilosc = int(data.get('Ilość', wyposazenie.ilosc))

        # Zapis do bazy danych
        db.session.commit()

        return jsonify({'message': 'Wyposażenie pojazdu zaktualizowane pomyślnie'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@wyposazenie_bp.route('/wyposazenie/check', methods=['POST'])
def sprawdz_wyposazenie():
    try:
        data = request.get_json()

        # Walidacja danych wejściowych: sprawdzenie, czy opis i ID Pojazdu są w danych
        if 'Opis' not in data or 'ID Pojazdu' not in data:
            return jsonify({'error': 'Opis i ID Pojazdu są wymagane'}), 400

        opis = data['Opis']
        id_pojazd = data['ID Pojazdu']

        # Sprawdzenie, czy pojazd o podanym ID istnieje
        pojazd = Pojazd.query.get(id_pojazd)
        if not pojazd:
            return jsonify({'error': 'Pojazd o podanym ID nie istnieje'}), 404

        # Wyszukiwanie wyposażenia w bazie danych na podstawie opisu i ID Pojazdu
        wyposazenie = WyposazeniePojazdu.query.filter_by(opis=opis, idPojazd=id_pojazd).first()

        # Zwracanie wyniku
        if wyposazenie:
            return jsonify({'idWyposazeniePojazdu': wyposazenie.idWyposazeniePojazdu}), 200
        else:
            return jsonify({'idWyposazeniePojazdu': None}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500