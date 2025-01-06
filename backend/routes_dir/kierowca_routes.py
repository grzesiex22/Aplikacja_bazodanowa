import json

from flask import Blueprint, request, jsonify
from Aplikacja_bazodanowa.backend.database import db
from Aplikacja_bazodanowa.backend.models import Kierowca
import traceback
from sqlalchemy import asc, desc, func

# Blueprint dla kierowców
kierowca_bp = Blueprint('kierowca', __name__)


@kierowca_bp.route('/kierowca/show/<int:id>', methods=['GET'])
def pobierz_kierowce(id):
    """
    Funkcja obsługuje żądanie GET pod adresem /kierowca/show/<int:id>.
    Umożliwia pobranie danych pojedynczego kierowcy na podstawie jego identyfikatora.

    Parametry URL:
        - id (int, wymagany): Identyfikator kierowcy przekazany w URL.

    Returns:
        Response:
        - 200 OK: Zwraca dane kierowcy, w tym:
            - ID kierowcy
            - Imię
            - Nazwisko
            - Nr telefonu
        - 404 Not Found: Jeśli kierowca o podanym identyfikatorze nie został znaleziony.
        - 500 Internal Server Error: W przypadku błędu serwera.
    """
    try:
        kierowca = Kierowca.query.get(id)
        if kierowca is None:
            return jsonify({'message': 'Kierowca nie znaleziony'}), 404

        # Zastosowanie serializacji z przyjaznymi nazwami
        serialized_kierowca = Kierowca.serialize(kierowca)

        return jsonify(serialized_kierowca), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500




@kierowca_bp.route('/kierowca/show/all', methods=['GET'])
def pobierz_wszystkich_kierowcow():
    """
    Funkcja obsługuje żądanie GET pod adresem /kierowca/show/all.
    Umożliwia pobranie listy wszystkich kierowców z bazy danych.

    Returns:
        Response:
        - 200 OK: Zwraca listę kierowców z poniższymi polami:
            - ID kierowcy
            - Imię
            - Nazwisko
            - Numer telefonu
        - 500 Internal Server Error: W przypadku błędu serwera.
    """
    try:
        kierowcy = Kierowca.query.all()
        wynik = []
        for kierowca in kierowcy:
            wynik.append(Kierowca.serialize(kierowca))
        return jsonify(wynik), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@kierowca_bp.route('/kierowca/filtry', methods=['GET'])
def pobierz_filtry_dla_pojazdy():
    """
    Funkcja obsługuje żądanie GET pod adresem /kierowca/filtry.
    Umożliwia pobranie unikalnych wartości dla kolumny kierowców, na podstawie której można filtrować dane.

    Parametry wejściowe:
        - filtr (string, wymagany): Typ filtru, który określa nazwę kolumny w tabeli kierowców,
          na której mają zostać pobrane unikalne wartości.

    Returns:
        Response:
        - 200 OK: Zwraca posortowaną listę unikalnych wartości dla wskazanej kolumny.
        - 400 Bad Request: Jeśli podany filtr nie jest zgodny z żadną kolumną w tabeli kierowców.
        - 500 Internal Server Error: W przypadku błędu serwera.
    """
    typ_filtru = request.args.get('filtr')  # Pobieramy parametr 'typPojazdu' z zapytania
    print(f"api: pobierz_filtry_dla_kierowcy")
    print(f"Pobrany typ filtru {typ_filtru}")
    # Mapowanie `friendly_name` na rzeczywiste kolumny `Pojazd`
    sort_column_name = None
    for column_name, column_info in Kierowca.COLUMN_NAME_MAP.items():
        if column_info['friendly_name'] == typ_filtru:
            sort_column_name = column_name
            break

    print(f"Znaleziona nazwa kolumny do sortowania: {sort_column_name}")
    # Sprawdzenie, czy znaleziono kolumnę. Jeśli nie, zgłaszamy błąd.
    if sort_column_name is None:
        return jsonify(f"Nie znaleziono kolumny: '{typ_filtru}' w tabeli {Kierowca.__name__}"), 400

    try:
        column_to_filter = getattr(Kierowca, sort_column_name)
        # Zapytanie do bazy danych: unikalne wartości z ignorowaniem wielkości liter
        unique_values_query = (
            Kierowca.query
            .with_entities(func.lower(column_to_filter).label('unique_value'))  # Konwertujemy na małe litery
            .distinct()  # Wybieramy tylko unikalne wartości
        )
        # Pobrane wartości zamieniamy na listę
        unique_values = [row.unique_value for row in unique_values_query]
        unique_values.sort()
        return jsonify(unique_values), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500



@kierowca_bp.route('/kierowca/show', methods=['GET'])
def pobierz_i_sortuj_kierowcow():
    """
    Funkcja obsługuje żądanie GET pod adresem /kierowca/show.
    Umożliwia pobranie i sortowanie listy kierowców na podstawie parametrów zapytania.
    Obsługuje filtrowanie, wybór kolumny do sortowania oraz kierunek sortowania.

    Parametry wejściowe:
        - filter_by (string, opcjonalny): Filtry w formacie JSON. Domyślnie `{}` (brak filtrów).
        - sort_by (string, opcjonalny): Kolumna, według której ma nastąpić sortowanie. Domyślnie "ID kierowcy".
        - order (string, opcjonalny): Kierunek sortowania. Możliwe wartości to "asc" (rosnąco) lub "desc" (malejąco). Domyślnie "asc".

    Returns:
        Response:
        - 200 OK: Zwraca posortowaną i przefiltrowaną listę kierowców w formacie JSON:
            - ID kierowcy
            - Imię
            - Nazwisko
            - Numer telefonu
        - 500 Internal Server Error: W przypadku błędu serwera.

    Przykład użycia:
        - `/kierowca/show?filter_by={"Imię": ["Jan"]}&sort_by=ID kierowcy&order=asc`
    """
    # Pobierz parametry zapytania
    filter_by = request.args.get('filter_by', '{}')  # Filtrowanie - jest to słownik
    sort_by = request.args.get('sort_by', 'ID kierowcy')  # Sortowanie po `idPojazd` domyślnie
    order = request.args.get('order', 'asc')  # Domyślny kierunek sortowania to `asc`

    # Printy do wyświetlania wartości parametrów
    print(f"api: pobierz i sortuj kierowców")
    print(f"Filter by: {filter_by}")
    print(f"Sort by: {sort_by}")
    print(f"Order: {order}")

    # Ustal kierunek sortowania
    kierunek_sortowania = asc if order == 'asc' else desc

    try:
        # Budowanie podstawowego zapytania
        query = db.session.query(Kierowca)

        # Jeżeli filtr 'filter_by' jest przekazany, należy dodać filtry do zapytania
        if filter_by != '{}':
            print(f"Received filter_by: {filter_by}")

            # Filtrujemy po każdym 'friendly_name' i jego wartościach
            try:
                filters = json.loads(filter_by)
                print(f"Parsed filters: {filters}")

                for friendly_name, values in filters.items():
                    print(f"Processing filter: {friendly_name} with values: {values}")

                    # Mapowanie `friendly_name` na rzeczywiste kolumny `Pojazd`
                    column_name = None

                    # Mapowanie na inne kolumny
                    print(f"Searching for column corresponding to {friendly_name}")
                    for column, column_info in Kierowca.COLUMN_NAME_MAP.items():
                        if column_info['friendly_name'] == friendly_name:
                            column_name = column
                            print(f"Found column: {column_name}")
                            break

                    if column_name:
                        column_to_filter = getattr(Kierowca, column_name)
                        print(f"Applying filter for column {column_name}")

                        # Dodajemy filtr, jeśli wartości są przekazane
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
        # Mapowanie `friendly_name` na rzeczywiste kolumny `Pojazd`
        sort_column_name = None
        for column_name, column_info in Kierowca.COLUMN_NAME_MAP.items():
            if column_info['friendly_name'] == sort_by:
                sort_column_name = column_name
                break

        # Pobieramy kolumnę modelu na podstawie `sort_column_name`, lub domyślnie `idPojazd`
        sort_column = getattr(Kierowca, sort_column_name, Kierowca.idKierowca)
        query = query.order_by(kierunek_sortowania(sort_column))

        # Pobranie wyników
        kierowcy = query.all()

        # Konwersja wyników do formatu JSON
        wynik = [Kierowca.serialize(k) for k in kierowcy]

        return jsonify(wynik), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@kierowca_bp.route('/kierowca/show/alltochoice', methods=['GET'])
def pobierz_wszystkich_kierowcow_do_okna_wyboru():
    """
    Funkcja obsługuje żądanie GET pod adresem /kierowca/show/alltochoice.
    Umożliwia pobranie listy kierowców w formacie odpowiednim do wyświetlania w oknie wyboru (np. dropdown).
    Zwraca ID kierowcy oraz jego dane kontaktowe (imię, nazwisko, numer telefonu).

    Returns:
        Response:
        - 200 OK: Zwraca listę kierowców w formacie JSON, zawierającą:
          - `ID` (int): Identyfikator kierowcy.
          - `data` (string): Imię, nazwisko oraz numer telefonu kierowcy.
        - 500 Internal Server Error: W przypadku błędu serwera.
    """
    try:
        # Pobieramy listę kierowców posortowaną po imieniu i nazwisku
        kierowcy = Kierowca.query.order_by(Kierowca.imie.asc(), Kierowca.nazwisko.asc()).all()

        # Przygotowanie wyników w formacie oczekiwanym w oknie wyboru
        wynik = []
        for kierowca in kierowcy:
            data = {'ID': kierowca.idKierowca, 'data': f"{kierowca.imie} {kierowca.nazwisko}, tel. {kierowca.nrTel}"}
            wynik.append(data)

        return jsonify(wynik), 200
    except Exception as e:
        # W przypadku błędu serwera
        return jsonify({'error': str(e)}), 500


@kierowca_bp.route('/kierowca/add', methods=['POST'])
def dodaj_kierowce():
    """
    Funkcja obsługuje żądanie POST pod adresem /kierowca/add.
    Umożliwia dodanie nowego kierowcy do bazy danych.

    Parametry wejściowe w formacie json (wymagane):
      - `imie` (string): Imię kierowcy.
      - `nazwisko` (string): Nazwisko kierowcy.
      - `nrTel` (string): Numer telefonu kierowcy.

    Returns:
        Response:
        - 201 Created: Jeśli kierowca został pomyślnie dodany do bazy.
        - 500 Internal Server Error: W przypadku błędu serwera przy dodawaniu kierowcy.
    """
    data = request.get_json()

    # Deserializacja danych wejściowych
    deserialized_data = Kierowca.deserialize(data)
    # Tworzenie obiektu Kierowca na podstawie deserializowanych danych
    nowy_kierowca = Kierowca(**deserialized_data)

    try:
        # Dodanie kierowcy do sesji i zapisanie w bazie danych
        db.session.add(nowy_kierowca)
        db.session.commit()
        return jsonify({'message': 'Kierowca dodany pomyślnie'}), 201
    except Exception as e:
        # W przypadku błędu wycofanie transakcji
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@kierowca_bp.route('/kierowca/delete/<int:id>', methods=['DELETE'])
def usun_kierowce(id):
    """
    Funkcja obsługuje żądanie DELETE pod adresem /kierowca/delete/<int:id>.
    Umożliwia usunięcie kierowcy z bazy danych na podstawie jego identyfikatora.

    Parametry URL:
        - id (int): Identyfikator kierowcy, którego chcesz usunąć.

    Returns:
        Response:
        - 200 OK: Jeśli kierowca został pomyślnie usunięty.
        - 404 Not Found: Jeśli kierowca o podanym identyfikatorze nie został znaleziony.
        - 500 Internal Server Error: W przypadku błędu serwera przy usuwaniu kierowcy.
    """
    try:
        # Pobranie kierowcy na podstawie ID
        kierowca = Kierowca.query.get(id)
        if kierowca is None:
            return jsonify({'message': 'Kierowca nie znaleziony'}), 404

        # Usunięcie kierowcy z bazy danych
        db.session.delete(kierowca)
        db.session.commit()

        # Zwrócenie informacji o pomyślnym usunięciu
        return jsonify({'message': 'Kierowca usunięty pomyślnie'}), 200

    except Exception as e:
        # W przypadku błędu wycofanie transakcji
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@kierowca_bp.route('/kierowca/edit/<int:id>', methods=['PUT'])
def edytuj_kierowce(id):
    """
    Funkcja obsługuje żądanie PUT pod adresem /kierowca/edit/<int:id>.
    Umożliwia edytowanie danych istniejącego kierowcy na podstawie jego identyfikatora.

    Parametry URL:
        - id (int): Identyfikator kierowcy, którego dane mają być zaktualizowane.

    Parametry w formacie JSON:
        - imie (string, opcjonalny): Nowe imię kierowcy.
        - nazwisko (string, opcjonalny): Nowe nazwisko kierowcy.
        - nrTel (string, opcjonalny): Nowy numer telefonu kierowcy.

    Returns:
        Response:
        - 200 OK: Jeśli dane kierowcy zostały pomyślnie zaktualizowane.
        - 404 Not Found: Jeśli kierowca o podanym identyfikatorze nie został znaleziony.
        - 500 Internal Server Error: W przypadku błędu przy aktualizacji danych.
    """
    data = request.get_json()

    # Deserializacja danych wejściowych
    deserialized_data = Kierowca.deserialize(data)
    print(f"Deserialized data: {deserialized_data}")

    try:
        # Pobranie kierowcy na podstawie ID
        kierowca = Kierowca.query.get(id)
        if kierowca is None:
            return jsonify({'message': 'Kierowca nie znaleziony'}), 404

        # Aktualizacja danych kierowcy, jeśli są dostępne w przesłanych danych
        kierowca.imie = deserialized_data.get('imie', kierowca.imie)
        kierowca.nazwisko = deserialized_data.get('nazwisko', kierowca.nazwisko)
        kierowca.nrTel = deserialized_data.get('nrTel', kierowca.nrTel)

        # Zapisanie zmian w bazie danych
        db.session.commit()

        return jsonify({'message': 'Dane kierowcy zaktualizowane pomyślnie'}), 200

    except Exception as e:
        # Wycofanie transakcji w przypadku błędu
        db.session.rollback()
        # Logowanie błędu
        print(f"Błąd: {str(e)}")
        print(traceback.format_exc())  # Dodatkowe informacje o błędzie
        return jsonify({'error': 'Wystąpił problem z aktualizacją danych. Spróbuj ponownie później.'}), 500


@kierowca_bp.route('/kierowca/validate', methods=['POST'])
def validate_kierowca():
    """
    Funkcja obsługuje żądanie POST pod adresem /kierowca/validate.
    Sprawdza poprawność danych kierowcy (np. numer telefonu).

    Parametry w formacie JSON:
        - imie (string): Imię kierowcy.
        - nazwisko (string): Nazwisko kierowcy.
        - nrTel (string): Numer telefonu kierowcy.

    Returns:
        Response:
        - 200 OK: Jeśli dane są poprawne.
        - 400 Bad Request: Jeśli dane są niepoprawne (np. zły format numeru telefonu) - informacja o błędzie zwracana.
    """
    data = request.get_json()
    print(f"Data in validation api: {data}")

    # Sprawdzenie poprawności danych przy użyciu metody validate_data
    validation_result = Kierowca.validate_data(data)

    # Jeśli wynik walidacji zawiera błędy, zwrócimy je
    if validation_result:
        return jsonify(validation_result[0]), validation_result[1]

    # Jeśli dane są poprawne, zwrócimy komunikat o sukcesie
    return jsonify({'message': 'Dane są poprawne'}), 200


@kierowca_bp.route('/kierowca/sort', methods=['GET'])
def sort_pojazdy():
    """
    Funkcja obsługuje żądanie GET pod adresem /kierowca/sort.
    Sortuje kierowców na podstawie wybranej kolumny i kierunku sortowania.

    Parametry zapytania:
        - sort_by (string): Kolumna do sortowania. Domyślnie "ID kierowcy".
        - order (string): Kierunek sortowania ("asc" lub "desc"). Domyślnie "asc".

    Returns:
        Response:
        - 200 OK: Zwraca posortowaną listę kierowców w formacie JSON.
    """
    # Pobierz parametry zapytania
    sort_by = request.args.get('sort_by', 'ID kierowcy')  # Domyślnie sortowanie po `idPojazd`
    order = request.args.get('order', 'asc')
    print(f"Demanding sort_by: {sort_by}")

    # Określenie kierunku sortowania
    kierunek_sortowania = asc if order == 'asc' else desc

    # Ustalanie kolumny do sortowania na podstawie friendly_name
    sort_column_name = None
    for column_name, column_info in Kierowca.COLUMN_NAME_MAP.items():
        if column_info['friendly_name'] == sort_by:
            sort_column_name = column_name
            break

    # Pobierz kolumnę do sortowania, domyślnie "idKierowca"
    sort_column = getattr(Kierowca, sort_column_name, Kierowca.idKierowca)
    sort_direction = kierunek_sortowania(sort_column)

    # Wykonanie zapytania do bazy danych z sortowaniem
    kierowcy = Kierowca.query.order_by(sort_direction).all()

    # Konwertowanie wyników na format JSON
    wynik = [Kierowca.serialize(kierowca) for kierowca in kierowcy]

    return jsonify(wynik), 200
