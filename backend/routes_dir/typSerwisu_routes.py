import json

from flask import Blueprint, request, jsonify
from sqlalchemy import asc, desc

from Aplikacja_bazodanowa.backend.database import db
from Aplikacja_bazodanowa.backend.models import TypSerwisu
import re

# Blueprint dla TypSerwisu
typserwis_bp = Blueprint('typserwis', __name__)

# Pobieranie danych pojedynczego typu serwisu
@typserwis_bp.route('/typserwis/<int:id>', methods=['GET'])
def pobierz_typserwis(id):
    """
    Endpoint do pobierania szczegółowych informacji o jednym typie serwisu na podstawie jego ID.

    Parametry URL:
        - id (int): Identyfikator typu serwisu, który ma zostać pobrany.

    Returns:
        Response:
            - 200 OK: Zwraca szczegóły typu serwisu:
                  - idTypSerwisu (int): Identyfikator typu serwisu
                  - rodzajSerwisu (string): Rodzaj serwisu
                  - typPojazdu (string): Typ pojazdu
            - 404 Not Found: Jeśli typ serwisu o podanym ID nie został znaleziony.
            - 500 Internal Server Error: W przypadku błędu serwera.
    """

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
    """
    Endpoint do pobierania szczegółowych informacji o wszystkich typach serwisów.

    Returns:
        Response:
            - 200 OK: Zwraca listę typów serwisów:
                  - idTypSerwisu (int): Identyfikator typu serwisu
                  - rodzajSerwisu (string): Rodzaj serwisu
                  - typPojazdu (string): Typ pojazdu
            - 404 Not Found: Jeśli typ serwisu o podanym ID nie został znaleziony.
            - 500 Internal Server Error: W przypadku błędu serwera.
    """
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


@typserwis_bp.route('/typserwis', methods=['POST'])
def dodaj_typserwis():
    """
    Endpoint do dodawania nowego typu serwisu.

    Parametry wejściowe w formacie JSON:
        - rodzajSerwisu (str, wymagany): Rodzaj serwisu.
        - typPojazdu (str, wymagany): Typ pojazdu ("Ciągnik" lub "Naczepa").

    Returns:
        Response:
            - 201 Created: Jeśli typ serwisu został dodany pomyślnie.
            - 400 Bad Request: W przypadku błędnych danych wejściowych, np. brak wymaganych pól lub niewłaściwy typ pojazdu.
            - 500 Internal Server Error: W przypadku błędu serwera.
    """
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


@typserwis_bp.route('/typserwis/<int:id>', methods=['DELETE'])
def usun_typserwis(id):
    """
    Endpoint do usuwania typu serwisu na podstawie identyfikatora.

    Parametry URL:
        - id (int): Identyfikator typu serwisu, który ma zostać usunięty.

    Returns:
        Response:
            - 200 OK: Jeśli typ serwisu został usunięty pomyślnie.
            - 404 Not Found: Jeśli typ serwisu o podanym identyfikatorze nie został znaleziony.
            - 500 Internal Server Error: W przypadku błędu serwera.
    """
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


@typserwis_bp.route('/typserwis/<int:id>', methods=['PUT'])
def edytuj_typserwis(id):
    """
    Endpoint do usuwania typu serwisu na podstawie identyfikatora.

    Parametry URL:
        - id (int): Identyfikator typu serwisu, który ma zostać usunięty.
    Parametry wejściowe w formacie JSON:
        - rodzajSerwisu (str, opcjonalny): Rodzaj serwisu.
        - typPojazdu (str, opcjonalny): Typ pojazdu ("Ciągnik" lub "Naczepa").

    Returns:
        Response:
            - 200 OK: Jeśli typ serwisu został usunięty pomyślnie.
            - 404 Not Found: Jeśli typ serwisu o podanym identyfikatorze nie został znaleziony.
            - 500 Internal Server Error: W przypadku błędu serwera.
    """

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
def pobierz_wszystkie_typyserwisu_do_okna_wyboru():
    """
    Endpoint do pobierania listy typów serwisów przeznaczonej do wyboru, z możliwością filtrowania czy ma być tylko
    rodzaj wyposażenie, czy wszystko oprócz niego.

    Parametry wejściowe:
        - withWyposażenie (bool, opcjonalny): Jeśli 'true', zwróci tylko rekordy z rodzajem serwisu 'Wyposażenie'. Domyślnie 'false'.

    Returns:
        Response:
            - 200 OK: Zwraca listę typów serwisów:
                - ID (int): Identyfikator typu serwisu
                - data (string): Połączenie - Typ pojazdu, rodzaj serwisu
            - 500 Internal Server Error: W przypadku błędu serwera.
    """
    try:
        # Pobieranie parametru from query string
        with_wyposażenie = request.args.get('withWyposażenie', 'false').lower() == 'true'

        # Pobieramy wszystkie typy serwisów z bazy danych, posortowane po typie pojazdu i rodzaju serwisu
        typySerwisu = TypSerwisu.query.order_by(TypSerwisu.typPojazdu.asc(), TypSerwisu.rodzajSerwisu.asc()).all()

        wynik = []
        for typSerwisu in typySerwisu:
            if with_wyposażenie:
                # Jeśli withWyposażenie jest True, dodajemy tylko rekordy z rodzajem serwisu 'Wyposażenie'
                if typSerwisu.rodzajSerwisu == 'Wyposażenie':
                    data = {'ID': typSerwisu.idTypSerwisu, 'data': f"{typSerwisu.typPojazdu}, {typSerwisu.rodzajSerwisu}"}
                    wynik.append(data)
            else:
                # Jeśli withWyposażenie jest False, dodajemy tylko rekordy, które nie mają rodzaju serwisu 'Wyposażenie'
                if typSerwisu.rodzajSerwisu != 'Wyposażenie':
                    data = {'ID': typSerwisu.idTypSerwisu, 'data': f"{typSerwisu.typPojazdu}, {typSerwisu.rodzajSerwisu}"}
                    wynik.append(data)

        return jsonify(wynik), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@typserwis_bp.route('/typserwis/show/alltochoice2', methods=['GET'])
def pobierz_wszystkie_typyserwisu_do_okna_wyboru2():
    """
    Endpoint do pobierania listy typów serwisów przeznaczonej do wyboru.

    Returns:
        Response:
            - 200 OK: Zwraca listę typów serwisów:
                - ID (int): Identyfikator typu serwisu
                - data (string): Połączenie - Typ pojazdu, rodzaj serwisu
            - 500 Internal Server Error: W przypadku błędu serwera.
    """
    try:
        typySerwisu = TypSerwisu.query.order_by(TypSerwisu.typPojazdu.asc(), TypSerwisu.rodzajSerwisu.asc()).all()
        wynik = []
        for typSerwisu in typySerwisu:
            data = {'ID': typSerwisu.idTypSerwisu, 'data': f"{typSerwisu.typPojazdu}, {typSerwisu.rodzajSerwisu}"}
            wynik.append(data)
        return jsonify(wynik), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@typserwis_bp.route('/typserwis/show', methods=['GET'])
def pobierz_i_sortuj_typy_serwisu():
    """
    Endpoint do pobierania i sortowania typów serwisów z możliwością filtrowania według różnych kryteriów.

    Parametry zapytania:
        - filter_by (json, opcjonalny): Parametr do filtrowania danych w formacie JSON.
        - sort_by (string, opcjonalny): Kolumna, po której serwisy mają zostać posortowane (domyślnie 'ID typu serwisu').
        - order (string, opcjonalny): Kierunek sortowania, 'asc' dla rosnącego, 'desc' dla malejącego (domyślnie 'asc').

    Returns:
        Response:
            - 200 OK: Zwraca przefiltrowane i posortowane typy serwisów:
                  - ID typu serwisu (int): Identyfikator typu serwisu
                  - Rodzaj serwisu (string): Rodzaj serwisu
                  - Typ pojazdu (string): Typ pojazdu
            - 500 Internal Server Error: W przypadku błędu serwera.
    """

    # Pobierz parametry zapytania
    filter_by = request.args.get('filter_by', '{}')  # Filtrowanie - jest to słownik
    sort_by = request.args.get('sort_by', 'ID typu serwisu')  # Sortowanie po `idTypSerwisu` domyślnie
    order = request.args.get('order', 'asc')  # Domyślny kierunek sortowania to `asc`

    print(f"api: pobierz i sortuj typy serwisu")
    print(f"Filter by: {filter_by}")
    print(f"Sort by: {sort_by}")
    print(f"Order: {order}")

    # Ustal kierunek sortowania
    kierunek_sortowania = asc if order == 'asc' else desc

    try:
        # Budowanie podstawowego zapytania
        query = db.session.query(TypSerwisu)

        # Jeżeli filtr 'filter_by' jest przekazany, należy dodać filtry do zapytania
        if filter_by != '{}':
            print(f"Received filter_by: {filter_by}")

            try:
                filters = json.loads(filter_by)
                print(f"Parsed filters: {filters}")

                for friendly_name, values in filters.items():
                    print(f"Processing filter: {friendly_name} with values: {values}")

                    # Mapowanie `friendly_name` na rzeczywiste kolumny `TypSerwisu`
                    column_name = None

                    for column, column_info in TypSerwisu.COLUMN_NAME_MAP.items():
                        if column_info['friendly_name'] == friendly_name:
                            column_name = column
                            print(f"Found column: {column_name}")
                            break

                    if column_name:
                        column_to_filter = getattr(TypSerwisu, column_name)
                        print(f"Applying filter for column {column_name}")

                        if isinstance(values, list):  # Jeśli wartości to lista
                            query = query.filter(column_to_filter.in_(values))
                            print(f"Filter applied for list of values: {values}")
                        elif isinstance(values, str) and len(values) >= 3:  # Minimum 3 litery do filtrowania LIKE
                            query = query.filter(column_to_filter.ilike(f"%{values}%"))
                            print(f"Partial match filter applied for: {values}")
                    else:
                        print(f"No column found for friendly_name: {friendly_name}")

            except json.JSONDecodeError as e:
                print(f"Error decoding JSON for filter_by: {str(e)}")
            except Exception as e:
                print(f"Unexpected error while processing filters: {str(e)}")

        # Ustalanie kolumny do sortowania
        sort_column_name = None
        for column_name, column_info in TypSerwisu.COLUMN_NAME_MAP.items():
            if column_info['friendly_name'] == sort_by:
                sort_column_name = column_name
                break

        # Pobieramy kolumnę modelu na podstawie `sort_column_name`, lub domyślnie `idTypSerwisu`
        sort_column = getattr(TypSerwisu, sort_column_name, TypSerwisu.idTypSerwisu)
        query = query.order_by(kierunek_sortowania(sort_column))

        # Pobranie wyników
        typy_serwisu = query.all()

        # Konwersja wyników do formatu JSON
        wynik = [TypSerwisu.serialize(typ_serwisu) for typ_serwisu in typy_serwisu]

        return jsonify(wynik), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
