from flask import Blueprint, request, jsonify
from sqlalchemy import asc, desc
from sqlalchemy.exc import SQLAlchemyError

from Aplikacja_bazodanowa.backend.database import db
from Aplikacja_bazodanowa.backend.models import WyposazeniePojazdu, Pojazd, Czesc

# Blueprint dla Wyposażenia Pojazdu
wyposazenie_bp = Blueprint('wyposazenie', __name__)


@wyposazenie_bp.route('/wyposazenie/show/<int:id>', methods=['GET'])
def pobierz_wyposazenie(id):
    """
    Funkcja obsługuje żądanie GET pod adresem /wyposazenie/show/<int:id>.
    Pobiera szczegółowe informacje o wyposażeniu pojazdu na podstawie podanego identyfikatora `id`.

    Parametry wejściowe:
        - id (int): Identyfikator wyposażenia pojazdu przekazany w URL.

    Returns:
        Response:
        - 200 OK: Jeśli wyposażenie zostało znalezione, zwraca szczegółowe dane w formacie JSON:
            - ID Wyposażenia Pojazdu: Identyfikator wyposażenia.
            - ID Pojazdu: Identyfikator pojazdu, do którego należy wyposażenie (może być `None`).
            - Pojazd: Opis pojazdu w formacie "typ, marka, model, nr rej." lub "Brak pojazdu", jeśli brak powiązanego pojazdu.
            - Opis: Szczegółowy opis wyposażenia.
            - Ilość: Liczba sztuk wyposażenia.
        - 404 Not Found: Jeśli wyposażenie o podanym identyfikatorze nie istnieje.
        - 500 Internal Server Error: Jeśli wystąpi błąd serwera.
    """

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


@wyposazenie_bp.route('/wyposazenie/show/all', methods=['GET'])
def pobierz_wszystkie_wyposazenie():
    """
    Funkcja obsługuje żądanie GET pod adresem /wyposazenie/show/all.
    Pobiera listę wyposażenia pojazdów z możliwością filtrowania i sortowania wyników.

    Parametry wejściowe:
        - opis (str, opcjonalne): Filtrowanie po fragmencie opisu wyposażenia (ignoruje wielkość liter).
        - idPojazd (int, opcjonalne): Filtrowanie po identyfikatorze pojazdu.
        - sort_by (str, opcjonalne): Pole do sortowania (domyślnie 'opis'). Możliwe wartości:
            - 'opis': Sortowanie po opisie wyposażenia.
            - 'ilosc': Sortowanie po liczbie sztuk wyposażenia.
            - 'pojazd': Sortowanie po typie, marce, modelu i numerze rejestracyjnym pojazdu.
        - order (str, opcjonalne): Kierunek sortowania:
            - 'asc': Rosnąco (domyślnie).
            - 'desc': Malejąco.

    Returns:
        Response:
        - 200 OK: Jeśli zapytanie zostanie wykonane poprawnie, zwraca listę wyposażenia w formacie JSON:
            - ID Wyposażenia Pojazdu: Identyfikator wyposażenia.
            - ID Pojazdu: Identyfikator pojazdu, do którego należy wyposażenie (może być `None`).
            - Pojazd: Opis pojazdu w formacie "typ, marka, model, nr rej." lub "Brak pojazdu".
            - Opis: Szczegółowy opis wyposażenia.
            - Ilość: Liczba sztuk wyposażenia.
        - 500 Internal Server Error: Jeśli wystąpi błąd serwera.


    """
    try:
        # Pobieranie parametrów zapytania
        opis = request.args.get('opis', '').strip()
        id_pojazd = request.args.get('idPojazd', None)
        sort_by = request.args.get('sort_by', 'opis')  # Domyślnie sortowanie po opisie
        order = request.args.get('order', 'asc')  # Domyślnie sortowanie rosnące

        # Tworzenie zapytania bazowego
        query = WyposazeniePojazdu.query

        # Filtracja po opisie wyposażenia
        if opis:
            query = query.filter(WyposazeniePojazdu.opis.ilike(f'%{opis}%'))

        # Filtracja po ID pojazdu
        if id_pojazd:
            query = query.filter(WyposazeniePojazdu.idPojazd == int(id_pojazd))

        # Określenie kierunku sortowania
        kierunek_sortowania = asc if order == 'asc' else desc

        # Sortowanie wyników na podstawie wybranego pola
        if sort_by in ['opis', 'ilosc']:
            sort_column = getattr(WyposazeniePojazdu, sort_by, WyposazeniePojazdu.opis)
            query = query.order_by(kierunek_sortowania(sort_column))
        elif sort_by == 'pojazd':
            # Sortowanie według danych pojazdu (typ, marka, model, nr rejestracyjny)
            query = query.order_by(
                kierunek_sortowania(Pojazd.typPojazdu),
                kierunek_sortowania(Pojazd.marka),
                kierunek_sortowania(Pojazd.model),
                kierunek_sortowania(Pojazd.nrRejestracyjny)
            )

        # Pobieranie wyników z bazy danych
        wyposazenie_list = query.all()

        # Tworzenie listy wyników w formacie JSON
        wynik = []
        for wyposazenie in wyposazenie_list:
            pojazd = Pojazd.query.get(wyposazenie.idPojazd) if wyposazenie.idPojazd else None
            pojazd_opis = (
                f"{pojazd.typPojazdu.value}, {pojazd.marka}, {pojazd.model}, nr rej. {pojazd.nrRejestracyjny}"
                if pojazd else "Brak pojazdu"
            )
            wynik.append({
                'ID Wyposażenia Pojazdu': wyposazenie.idWyposazeniePojazdu,
                'ID Pojazdu': wyposazenie.idPojazd,
                'Pojazd': pojazd_opis,
                'Opis': wyposazenie.opis,
                'Ilość': wyposazenie.ilosc
            })

        return jsonify(wynik), 200
    except Exception as e:
        # Obsługa błędów serwera
        return jsonify({'error': str(e)}), 500


@wyposazenie_bp.route('/wyposazenie/add', methods=['POST'])
def dodaj_wyposazenie():
    """
    Funkcja obsługuje żądanie POST pod adresem /wyposazenie/add.
    Dodaje nowe wyposażenie pojazdu lub aktualizuje istniejące, jeśli wyposażenie o podanym ID pojazdu i opisie już istnieje.

    Parametry wejściowe w formacie JSON (wymagane):
        - ID Pojazdu (int): Identyfikator pojazdu, do którego należy wyposażenie.
        - Opis (str): Szczegółowy opis wyposażenia pojazdu.
        - Ilość (int): Liczba sztuk wyposażenia.

    Returns:
        Response:
        - 201 Created: Jeśli wyposażenie zostało dodane lub zaktualizowane pomyślnie.
        - 500 Internal Server Error: Jeśli wystąpił błąd serwera, zwraca szczegóły błędu.
    """
    try:
        # Pobieranie danych z żądania JSON
        data = request.get_json()

        # Walidacja i przypisanie danych wejściowych
        id_pojazd = int(data['ID Pojazdu'])
        opis = data['Opis']
        ilosc = int(data['Ilość'])

        # Sprawdzanie, czy wyposażenie już istnieje
        istnieje_wyposazenie = WyposazeniePojazdu.query.filter_by(idPojazd=id_pojazd, opis=opis).first()

        if istnieje_wyposazenie:
            # Aktualizacja ilości wyposażenia
            istnieje_wyposazenie.ilosc += ilosc
        else:
            # Tworzenie nowego wpisu
            nowe_wyposazenie = WyposazeniePojazdu(
                idPojazd=id_pojazd,
                opis=opis,
                ilosc=ilosc
            )
            db.session.add(nowe_wyposazenie)

        # Zapis zmian w bazie danych
        db.session.commit()

        # Zwrot odpowiedzi sukcesu
        return jsonify({'message': 'Wyposażenie pojazdu zostało dodane lub zaktualizowane pomyślnie'}), 201
    except Exception as e:
        # Wycofanie transakcji w przypadku błędu
        db.session.rollback()
        # Zwrot odpowiedzi z błędem
        return jsonify({'error': str(e)}), 500


@wyposazenie_bp.route('/wyposazenie/validate', methods=['POST'])
def validate_wyposazenie():
    """
    Funkcja obsługuje żądanie POST pod adresem /wyposazenie/validate.
    Waliduje dane wejściowe dla nowego wyposażenia pojazdu, sprawdzając ich poprawność i zgodność z założeniami.

    Parametry wejściowe (w formacie JSON):
        - Opis (str): Opis wyposażenia, który musi być niepustym ciągiem znaków o długości maksymalnie 100 znaków.
        - Ilość (int): Ilość wyposażenia, która musi być liczbą całkowitą większą lub równą 0.
        - ID Pojazdu (int): Identyfikator pojazdu, który musi istnieć w bazie danych.

    Returns:
        Response:
        - 200 OK: Jeśli wszystkie dane wejściowe są poprawne.
        - 400 Bad Request: Jeśli dane są niepoprawne (np. brakujące lub nieprawidłowe wartości).
        - 500 Internal Server Error: Jeśli wystąpił błąd serwera, zwraca szczegóły błędu.
    """

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


@wyposazenie_bp.route('/wyposazenie/edit/validate', methods=['POST'])
def validate_wyposazenie_edit():
    """
    Funkcja obsługuje żądanie POST pod adresem /wyposazenie/validate.
    Waliduje dane wejściowe dla nowego wyposażenia pojazdu, sprawdzając ich poprawność i zgodność z założeniami.

    Parametry wejściowe (w formacie JSON):
        - Opis (str): Opis wyposażenia, który musi być niepustym ciągiem znaków o długości maksymalnie 100 znaków.
        - Ilość (int): Ilość wyposażenia, która musi być liczbą całkowitą większą lub równą 0.
        - ID Pojazdu (int): Identyfikator pojazdu, który musi istnieć w bazie danych.

    Returns:
        Response:
        - 200 OK: Jeśli wszystkie dane wejściowe są poprawne.
        - 400 Bad Request: Jeśli dane są niepoprawne (np. brakujące lub nieprawidłowe wartości).
        - 500 Internal Server Error: Jeśli wystąpił błąd serwera, zwraca szczegóły błędu.
    """

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


@wyposazenie_bp.route('/wyposazenie/delete/<int:id>', methods=['DELETE'])
def usun_wyposazenie(id):
    """
    Funkcja obsługuje żądanie DELETE pod adresem /wyposazenie/delete/<int:id>.
    Usuwa wyposażenie pojazdu na podstawie podanego identyfikatora `id`.

    Parametry URL:
        - `id` (int): Identyfikator wyposażenia pojazdu przekazany w URL.

    Returns:
        Response:
        - 200 OK: Jeśli wyposażenie zostało pomyślnie usunięte.
        - 404 Not Found: Jeśli wyposażenie o podanym identyfikatorze nie istnieje w bazie danych.
        - 500 Internal Server Error: W przypadku błędu serwera.
    """

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


@wyposazenie_bp.route('/wyposazenie/edit/<int:id>', methods=['PUT'])
def edytuj_wyposazenie(id):
    """
    Edytuje dane wyposażenia pojazdu na podstawie identyfikatora `id`.

    Parametry URL:
        - `id` (int): Identyfikator wyposażenia pojazdu w URL.

    Parametry w formacie JSON:
        - `ID Pojazdu` (int): Identyfikator pojazdu (opcjonalne, domyślnie pozostaje niezmieniony).
        - `Opis` (str): Opis wyposażenia (opcjonalne, domyślnie pozostaje niezmieniony).
        - `Ilość` (int): Ilość wyposażenia (opcjonalne, domyślnie pozostaje niezmieniona).

    Odpowiedzi:
        - **200 OK**: Jeśli wyposażenie zostało zaktualizowane.
        - **404 Not Found**: Jeśli wyposażenie o podanym identyfikatorze nie zostało znalezione.
        - **500 Internal Server Error**: W przypadku błędu serwera.
    """
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
    """
    Sprawdza, czy wyposażenie o podanym opisie i ID pojazdu istnieje w bazie danych.

    Parametry w formacie JSON:
        - `Opis` (str): Opis wyposażenia (wymagany).
        - `ID Pojazdu` (int): Identyfikator pojazdu (wymagany).

    Odpowiedzi:
        - **200 OK**: Zwraca `idWyposazeniePojazdu`, jeśli wyposażenie istnieje, lub `null`, jeśli nie istnieje.
        - **404 Not Found**: Jeśli pojazd o podanym ID nie istnieje.
        - **400 Bad Request**: Jeśli w danych wejściowych brakuje wymaganych pól (Opis lub ID Pojazdu).
        - **500 Internal Server Error**: W przypadku błędu serwera.
    """
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




@wyposazenie_bp.route('/store_item', methods=['POST'])
def store_item():
    """
    Endpoint umożliwia zapisanie danych o części oraz aktualizację wyposażenia pojazdu w jednym bloku transakcyjnym.
    Operacja jest atomowa — w przypadku błędu, wszystkie zmiany są wycofywane

    Parametry w formacie JSON (wymagane):
        - `czesc` (dict): Dane o części, w tym:
            - `idTypSerwisu` (int): Identyfikator typu serwisu.
            - `ilosc` (int): Ilość części.
        - `wyposazenie` (dict): Dane o wyposażeniu pojazdu, w tym:
            - `idPojazd` (int): Identyfikator pojazdu.
            - `opis` (str): Opis wyposażenia.
            - `ilosc` (int): Ilość wyposażenia.

    Odpowiedzi:
        - **200 OK**: Część i wyposażenie zostały zapisane pomyślnie.
        - **400 Bad Request**: Brak wymaganych danych wejściowych.
        - **500 Internal Server Error**: W przypadku błędu serwera.
    """

    try:
        data = request.get_json()
        czesc_data = data.get('czesc')  # Informacje o części
        wyposazenie_data = data.get('wyposazenie')  # Informacje o wyposażeniu pojazdu

        if not czesc_data or not wyposazenie_data:
            return jsonify({"error": "Brak wymaganych danych"}), 400

        # Rozpoczynamy transakcję
        with db.session.begin():  # Rozpoczynamy transakcję
            # Sprawdzamy, czy pojazd wyposażenie istnieje
            wyposazenie = WyposazeniePojazdu.query.filter_by(idPojazd=wyposazenie_data['idPojazd'], opis=wyposazenie_data['opis']).first()

            if wyposazenie:
                if wyposazenie_data['ilosc'] > 0:
                    wyposazenie.ilosc = wyposazenie_data['ilosc']
                else:
                    db.session.delete(wyposazenie)
            else:
                return jsonify({"error": "Brak takiego wyposażenia"}), 401

            pojazd = Pojazd.query.get(wyposazenie.idPojazd)

            # Sprawdzanie czy część już istnieje
            czesc = Czesc.query.filter_by(nazwaElementu=wyposazenie_data['opis'],
                                          idTypSerwisu=czesc_data['idTypSerwisu']).first()

            if czesc:
                # Jeśli część już istnieje, edytujemy jej ilość
                czesc.ilosc = czesc.ilosc + czesc_data['ilosc']
                print(f"Zaktualizowano część {czesc.nazwaElementu}, nowa ilość: {czesc.ilosc}")
            else:
                # Jeśli część nie istnieje, dodajemy nową część
                czesc = Czesc(nazwaElementu=wyposazenie_data['opis'],
                              idTypSerwisu=czesc_data['idTypSerwisu'],
                              ilosc=czesc_data['ilosc'])
                db.session.add(czesc)
                print(f"Dodano nową część: {czesc.nazwaElementu}")

            # Na końcu, jeśli wszystko przebiegło pomyślnie, zatwierdzamy transakcję
            db.session.commit()

        return jsonify({"message": "Część i wyposażenie zostały zapisane pomyślnie."}), 200

    except SQLAlchemyError as e:
        # Jeśli wystąpił błąd związany z bazą danych, wycofujemy zmiany
        db.session.rollback()
        return jsonify({"error": f"Wystąpił błąd bazy danych: {str(e)}"}), 500

    except Exception as e:
        # Obsługuje inne rodzaje wyjątków
        return jsonify({"error": f"Wystąpił nieoczekiwany błąd: {str(e)}"}), 500
