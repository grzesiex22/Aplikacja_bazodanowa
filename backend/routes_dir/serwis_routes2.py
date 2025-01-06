import json
import traceback

from flask import Blueprint, request, jsonify
from sqlalchemy import func, asc, desc

from Aplikacja_bazodanowa.backend.database import db
from Aplikacja_bazodanowa.backend.models import Serwis, SerwisWidok, Pojazd, TypSerwisu
from datetime import datetime


# Blueprint dla serwisów
serwis_bp = Blueprint('serwis', __name__)


# Pobieranie pojedynczego serwisu
@serwis_bp.route('/serwis/show/<int:id>', methods=['GET'])
def pobierz_serwis(id):
    """
    Endpoint do pobierania szczegółowych informacji o serwisie na podstawie jego unikalnego identyfikatora.

    Parametry URL:
        - id (int): Identyfikator serwisu, którego szczegóły chcemy pobrać.

    Returns:
        Response:
        - 200 OK: Zwraca dane serwisu, w tym:
            - ID serwisu
            - ID pojazdu
            - ID typu serwisu
            - Dane pojazdu (typ, marka, model, numer rejestracyjny)
            - Typ serwisu (np. Ciągnik, Klimatyzacja)
            - Data serwisu
            - Przebieg
            - Koszt robocizny
            - Cena części netto
            - Koszt całkowity netto
            - Dodatkowe informacje
        - 404 Not Found: Jeśli serwis o podanym identyfikatorze nie został znaleziony.
        - 500 Internal Server Error: W przypadku błędu serwera.
    """
    try:
        # Pobranie widoku serwisu z bazy danych na podstawie podanego ID
        serwis = Serwis.query.get(id)
        print(f"Serwis pobrany: {serwis}")

        # Sprawdzenie, czy serwis istnieje
        if serwis is None:
            return jsonify({'message': 'Serwis nie znaleziony'}), 404

        # Serializacja obiektu serwis z przyjaznymi nazwami pól
        serialized_serwis = Serwis.serialize(serwis)

        # Zwrócenie zserializowanych danych serwisu
        return jsonify(serialized_serwis), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Pobieranie pojedynczego serwisu
@serwis_bp.route('/serwiswidok/show/<int:id>', methods=['GET'])
def pobierz_serwis_widok(id):
    """
    Endpoint do pobierania szczegółowych informacji o widoku serwisu na podstawie jego unikalnego identyfikatora.

    Parametry URL:
        - id (int): Identyfikator serwisu, którego szczegóły chcemy pobrać.

    Returns:
        Response:
        - 200 OK: Zwraca dane serwisu, w tym:
            - ID serwisu
            - ID pojazdu
            - Typ pojazdu (np. Ciągnik)
            - Marka pojazdu (np. Volvo)
            - Model pojazdu (np. FH16)
            - Numer rejestracyjny (np. PO12345)
            - Typ serwisu (np. Klimatyzacja)
            - Data serwisu (np. 05-09-2024)
            - Przebieg (np. 180000 km)
            - Koszt robocizny (np. 300)
            - Cena części netto (np. 750)
            - Koszt całkowity netto (np. 1050)
            - Dodatkowe informacje (np. Regeneracja sprężarki klimatyzacji)
        - 404 Not Found: Jeśli serwis o podanym identyfikatorze nie został znaleziony.
        - 500 Internal Server Error: W przypadku błędu serwera.

    """
    try:
        # Pobranie widoku serwisu z bazy danych na podstawie podanego ID
        serwis = SerwisWidok.query.get(id)

        # Sprawdzenie, czy serwis istnieje
        if serwis is None:
            return jsonify({'message': 'Serwis nie znaleziony'}), 404

        # Serializacja obiektu serwis z przyjaznymi nazwami pól
        serialized_serwis = SerwisWidok.serialize(serwis)

        # Zwrócenie zserializowanych danych serwisu
        return jsonify(serialized_serwis), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@serwis_bp.route('/serwiswidok/show/all', methods=['GET'])
def pobierz_serwisy_widok():
    """
    Endpoint do pobierania listy wszystkich serwisów w widoku.

    Returns:
        Response:
        - 200 OK: Zwraca listę serwisów w formacie JSON, w tym dla każdego serwisu:
            - ID serwisu
            - ID pojazdu
            - Typ pojazdu
            - Marka
            - Model
            - Numer rejestracyjny
            - Typ serwisu
            - Data serwisu
            - Przebieg
            - Koszt robocizny
            - Cena części netto
            - Koszt całkowity netto
            - Dodatkowe informacje
        - 404 Not Found: Jeśli żaden serwis nie został znaleziony.
        - 500 Internal Server Error: W przypadku błędu serwera.
    """

    try:
        # Pobranie widoku serwisów z bazy danych na podstawie podanego ID
        serwisy = SerwisWidok.query.all()

        # Sprawdzenie, czy serwisy istnieją
        if serwisy is None:
            return jsonify({'message': 'Serwis nie znaleziony'}), 404

        # Inicjalizacja listy do przechowywania wyników
        wynik = []
        for serwis in serwisy:
            # Serializujemy każdy serwis i dodajemy do listy wyników
            wynik.append(SerwisWidok.serialize(serwis))

        # Zwracamy listę zserializowanych serwisów w formacie JSON
        return jsonify(wynik), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500



# Dodawanie nowego serwisu
@serwis_bp.route('/serwis/add', methods=['POST'])
def dodaj_serwis():
    """
    Endpoint do dodawania nowego serwisu do bazy danych.

    Parametry w formacie JSON:
        - ID pojazdu (int, wymagane): ID pojazdu, którego dotyczy serwis.
        - ID typu serwisu (int, wymagane): ID typu serwisu (np. Klimatyzacja, Silnik).
        - Data serwisu (string, wymagane): Data wykonania serwisu w formacie 'dd-mm-yyyy'.
        - Cena części netto (int, opcjonalny): Koszt części użytych w serwisie (w netto).
        - Koszt robocizny (int, opcjonalny): Koszt robocizny w serwisie (w netto).
        - Koszt całkowity netto (int, opcjonalny): Całkowity koszt serwisu (w netto).
            - Jeśli nie podano, zostanie automatycznie obliczony na podstawie ceny części i kosztu robocizny.
        - Przebieg (int, wymagane): Przebieg pojazdu w momencie serwisu.
        - Dodatkowe informacje (string, opcjonalny): Dodatkowe szczegóły dotyczące serwisu.

    Returns:
        Response:
            - 201 Created: Serwis został pomyślnie dodany do bazy danych.
            - 400 Bad Request: W przypadku błędu walidacji danych wejściowych.
            - 500 Internal Server Error: W przypadku błędu systemowego podczas dodawania serwisu.
    """

    try:
        data = request.get_json()  # Pobieramy dane wejściowe w formacie JSON
        if not data:
            return jsonify({'error': 'Brak danych w żądaniu lub nieprawidłowy JSON'}), 400

        deserialized_data = Serwis.deserialize(data)  # Deserializacja danych
        nowy_serwis = Serwis(**deserialized_data)  # Tworzenie nowego obiektu

        db.session.add(nowy_serwis)
        db.session.commit()
        return jsonify({'message': 'Serwis dodany pomyślnie'}), 201

    except ValueError as ve:
        db.session.rollback()
        return jsonify({'error': f'Błąd walidacji danych: {str(ve)}'}), 400

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Błąd systemowy: {str(e)}'}), 500


# Usuwanie serwisu
@serwis_bp.route('/serwis/delete/<int:id>', methods=['DELETE'])
def usun_serwis(id):
    """
    Endpoint do usuwania serwisu z bazy danych na podstawie jego ID.

    Parametry URL:
        id (int): ID serwisu do usunięcia.

    Returns:
        Response:
          - 200 OK: Serwis został pomyślnie usunięty.
          - 404 Not Found: Serwis o podanym identyfikatorze nie został znaleziony.
          - 500 Internal Server Error: W przypadku błędu serwera.

    """
    try:
        # Pobranie serwisu na podstawie ID
        serwis = Serwis.query.get(id)
        if serwis is None:
            return jsonify({'message': 'Serwis nie znaleziony'}), 404  # Jeśli serwis nie istnieje, zwróć błąd 404

        db.session.delete(serwis)  # Usuwamy serwis z bazy
        db.session.commit()  # Zatwierdzamy zmiany w bazie danych
        return jsonify({'message': 'Serwis usunięty pomyślnie'}), 200  # Zwracamy komunikat o sukcesie

    except Exception as e:
        db.session.rollback()  # W przypadku błędu anulujemy sesję
        return jsonify({'error': str(e)}), 500  # Zwracamy komunikat o błędzie i kod 500


# Edytowanie danych serwisu
@serwis_bp.route('/serwis/edit/<int:id>', methods=['PUT'])
def edytuj_serwis(id):
    """
    Endpoint do edytowania danych serwisu na podstawie jego ID.

    Parametry URL:
        - id (int): ID serwisu, który ma zostać edytowany.

    Parametry w formacie JSON:
        - ID pojazdu (int, opcjonalny): ID pojazdu, którego dotyczy serwis.
        - ID typu serwisu (int, opcjonalny): ID typu serwisu (np. Klimatyzacja, Silnik).
        - Data serwisu (string, opcjonalny): Data wykonania serwisu w formacie `dd-mm-yyyy`.
        - Cena części netto (int, opcjonalny): Koszt części użytych w serwisie (w netto).
        - Koszt robocizny (int, opcjonalny): Koszt robocizny w serwisie (w netto).
        - Koszt całkowity netto (int, opcjonalny): Całkowity koszt serwisu (w netto). Jeśli nie podano, zostanie obliczony automatycznie.
        - Przebieg (int, opcjonalny): Przebieg pojazdu w momencie serwisu.
        - Dodatkowe informacje (string, opcjonalny): Dodatkowe szczegóły dotyczące serwisu.

    Returns:
        Response:
            - 200 OK: Dane serwisu zostały pomyślnie zaktualizowane.
            - 404 Not Found: Serwis o podanym identyfikatorze nie został znaleziony.
            - 500 Internal Server Error: Wystąpił błąd podczas próby aktualizacji danych serwisu.
    """

    data = request.get_json()  # Pobieramy dane wejściowe w formacie JSON

    # Deserializacja danych wejściowych do obiektu
    deserialized_data = Serwis.deserialize(data)
    print(f"Deserialized data: {deserialized_data}")

    try:
        # Pobranie serwisu na podstawie ID
        serwis = Serwis.query.get(id)
        if serwis is None:
            return jsonify({'message': 'serwis nie znaleziony'}), 404  # Jeśli serwis nie istnieje, zwróć błąd 404

        # Aktualizacja pól serwisu na podstawie deserializowanych danych
        serwis.idPojazd = deserialized_data.get('idPojazd', serwis.idPojazd)
        serwis.idTypSerwisu = deserialized_data.get('idTypSerwisu', serwis.idTypSerwisu)
        serwis.data = deserialized_data.get('data', serwis.data)
        serwis.cenaCzesciNetto = deserialized_data.get('cenaCzesciNetto', serwis.cenaCzesciNetto)
        serwis.robocizna = deserialized_data.get('robocizna', serwis.robocizna)
        serwis.kosztCalkowityNetto = deserialized_data.get('kosztCalkowityNetto', serwis.kosztCalkowityNetto)
        serwis.przebieg = deserialized_data.get('przebieg', serwis.przebieg)
        serwis.infoDodatkowe = deserialized_data.get('infoDodatkowe', serwis.infoDodatkowe)

        db.session.commit()  # Zatwierdzamy zmiany w bazie danych

        return jsonify({'message': 'Dane serwisu zaktualizowane pomyślnie'}), 200  # Zwracamy komunikat o sukcesie

    except Exception as e:
        db.session.rollback()  # W przypadku błędu anulujemy sesję
        print(f"Błąd: {str(e)}")
        print(traceback.format_exc())  # Wypisanie szczegółów błędu
        return jsonify({'error': 'Wystąpił problem z aktualizacją danych. Spróbuj ponownie później.'}), 500  # Komunikat o błędzie


@serwis_bp.route('/serwiswidok/filtry', methods=['GET'])
def jakie_filtry_dla_widoku_serwisu():
    """
    Endpoint do pobierania dostępnych unikalnych filtrów dla widoku serwisów dla podanej kolumny.

    Parametry wejściowe:
        - filtr (str, opcjonalny): Przyjazna nazwa filtru, według której kolumny chcemy filtrować (np. 'Typ serwisu', 'Dane pojazdu').
          Jeśli parametr nie zostanie przekazany, zwróci wszystkie dostępne filtry.

    Returns:
        Response:
            - 200 OK: Zwraca listę unikalnych wartości dla zadanego filtra (np. lista rodzajów serwisów, dane pojazdu).
            - 400 Bad Request: Błąd, gdy nie udało się znaleźć kolumny do filtrowania w bazie danych (np. niepoprawna nazwa filtru).
            - 500 Internal Server Error: Wystąpił błąd serwera przy przetwarzaniu zapytania.
    """
    # Pobranie parametrów zapytania z URL (typ filtru - kolumna)
    typ_filtru = request.args.get('filtr', None)

    print(f"api: pobierz_filtry_dla_serwisy")
    print(f"Pobrany typ filtru {typ_filtru}")

    # Mapowanie `friendly_name` z parametru `filtr` na właściwą kolumnę w modelu Serwis
    filtr_column_name = None
    for column_name, column_info in SerwisWidok.COLUMN_NAME_MAP.items():
        if column_info['friendly_name'] == typ_filtru:
            filtr_column_name = column_name
            break  # Zatrzymanie pętli po znalezieniu kolumny


    print(f"Znaleziona nazwa kolumny do filtrowania: {filtr_column_name}")

    # Sprawdzenie, czy znaleziono kolumnę do filtrowania; jeśli nie, zgłaszamy błąd
    if filtr_column_name is None:
        return jsonify(f"Nie znaleziono kolumny: '{typ_filtru}' w tabeli {Serwis.__name__}"), 400

    try:
        # Obsługa przypadku, gdy filtrujemy po rodzaju serwisu
        if filtr_column_name == 'idTypSerwisu':
            # Pobranie listy wszystkich kierowców powiązanych z serwisami, posortowanych alfabetycznie
            typserwisu_query = TypSerwisu.query.order_by(TypSerwisu.typPojazdu.asc(), TypSerwisu.rodzajSerwisu.asc()).all()

            # Formatowanie wyników dla każdego kierowcy do listy
            unique_values = []
            data = {
                'ID': None,
                'data': f"Brak rodzaju serwisu"}
            unique_values.append(data)

            for typserwisu in typserwisu_query:
                data = {
                    'ID': typserwisu.idTypSerwisu,
                    'data': f"{typserwisu.typPojazdu}, {typserwisu.rodzajSerwisu}"}
                unique_values.append(data)

        else:
            column_to_filter = getattr(SerwisWidok, filtr_column_name, None)
            # Jeśli nie znaleziono kolumny w modelu Serwis, zgłaszamy błąd
            if column_to_filter is None:
                return jsonify({'error': f"Kolumna '{filtr_column_name}' nie istnieje w modelu Serwis."}), 400

            # Tworzymy zapytanie do bazy danych, aby uzyskać unikalne wartości w tej kolumnie
            unique_values_query = (
                SerwisWidok.query
                    .with_entities(func.lower(column_to_filter).label('unique_value'))  # Ignorowanie wielkości liter
                    .distinct()  # Pobranie unikalnych wartości
            )
            # Konwersja wyniku zapytania na listę wartości
            unique_values = [row.unique_value for row in unique_values_query]
            # Sortowanie wynikowej listy unikalnych wartości
            unique_values.sort()

        # Zwracamy listę unikalnych wartości filtru lub danych kierowców jako odpowiedź JSON
        return jsonify(unique_values), 200

    except Exception as e:
        # Obsługa błędu - zwracamy szczegóły błędu w formie JSON i kod statusu 500
        return jsonify({'error': str(e)}), 500


@serwis_bp.route('/serwiswidok/show', methods=['GET'])
def pobierz_i_sortuj_widok_serwisów():
    """
    Endpoint do pobierania serwisów z możliwością filtrowania i sortowania według różnych kryteriów.

    Parametry wejściowe:
        - filter_by (str, opcjonalny): Filtr w formacie JSON, który pozwala na filtrowanie danych.
          Przykładowy format: `{"Typ serwisu": ["Naprawa", "Przegląd"], "Data serwisu": {"Od": "01-01-2020", "Do": "31-12-2020"}}`.
        - sort_by (str, opcjonalny): Kolumna, po której ma nastąpić sortowanie (domyślnie 'ID serwisu').
        - order (str, opcjonalny): Kierunek sortowania - 'asc' dla rosnącego, 'desc' dla malejącego (domyślnie 'asc').

    Returns:
        Response:
            - 200 OK: Zwraca przefiltrowane i posortowane dane serwisów w formacie JSON:
                - ID serwisu
                - ID pojazdu
                - Typ pojazdu
                - Marka
                - Model
                - Numer rejestracyjny
                - Typ serwisu
                - Data serwisu
                - Przebieg
                - Koszt robocizny
                - Cena części netto
                - Koszt całkowity netto
                - Dodatkowe informacje
            - 500 Internal Server Error: Wystąpił błąd podczas przetwarzania zapytania.
    """

    # Pobieramy poszczególne parametry zapytania
    filter_by = request.args.get('filter_by', '{}')  # Filtrowanie - domyślnie '{}' jeśli brak
    sort_by = request.args.get('sort_by', 'ID serwisu')  # Sortowanie domyślnie po 'ID serwisu'
    order = request.args.get('order', 'asc')  # Domyślny kierunek sortowania to 'asc'

    # Logowanie parametrów zapytania dla celów debugowania
    print(f"api: pobierz i sortuj serwisy")
    print(f"Filter by: {filter_by}")
    print(f"Sort by: {sort_by}")
    print(f"Order: {order}")

    # Ustalanie kierunku sortowania na podstawie wartości 'order'
    kierunek_sortowania = asc if order == 'asc' else desc  # Ustalanie kierunku sortowania

    try:
        # Budowanie podstawowego zapytania do bazy danych
        query = db.session.query(SerwisWidok)

        # Sprawdzamy, czy istnieje filtr 'filter_by', jeśli tak to dodajemy do zapytania
        if filter_by != '{}':  # Jeśli filtr jest różny od pustego słownika
            print(f"Received filter_by: {filter_by}")

            # Przetwarzamy filtr w formacie JSON na słownik
            try:
                filters = json.loads(filter_by)  # Konwersja filtra JSON na słownik
                print(f"Parsed filters: {filters}")

                # Iteracja po filtrach i ich wartościach
                for friendly_name, values in filters.items():
                    print(f"Processing filter: {friendly_name} with values: {values}")

                    # Mapowanie 'friendly_name' na odpowiadającą kolumnę w tabeli SerwisWidok
                    column_name = None

                    # Mapowanie na inne kolumny w tabeli SerwisWidok
                    print(f"Searching for column corresponding to {friendly_name}")
                    for column, column_info in SerwisWidok.COLUMN_NAME_MAP.items():
                        if column_info['friendly_name'] == friendly_name:
                            column_name = column
                            print(f"Found column: {column_name}")
                            break

                    # Jeśli znaleziono odpowiadającą kolumnę, dodajemy filtr
                    if column_name:
                        column_to_filter = getattr(SerwisWidok, column_name)
                        print(f"Applying filter for column {column_name}")

                        if friendly_name == 'Data serwisu':
                            date_from = values['Od']
                            date_to = values['Do']

                            if date_to != '':
                                # print(f"date_to: |{date_to}|")
                                try:
                                    parsed_date = datetime.strptime(date_to, '%d-%m-%Y')
                                    date_to = parsed_date.strftime('%Y-%m-%d')  # Zamiana na 'yyyy-mm-dd'
                                except ValueError:
                                    raise ValueError(
                                        f"Nieprawidłowy format daty: {date_to}. Oczekiwano 'dd-mm-yyyy'.")

                                query = query.filter(column_to_filter <= date_to)
                            if date_from != '':
                                # print(f"date_from: |{date_from}|")
                                try:
                                    parsed_date = datetime.strptime(date_from, '%d-%m-%Y')
                                    date_from = parsed_date.strftime('%Y-%m-%d')  # Zamiana na 'yyyy-mm-dd'
                                except ValueError:
                                    raise ValueError(f"Nieprawidłowy format daty: {date_from}. Oczekiwano 'dd-mm-yyyy'.")

                                query = query.filter(column_to_filter >= date_from)
                            print(f"Date range match filter applied for: {values}")

                        # Jeśli 'values' to lista, filtrujemy na podstawie tej listy
                        elif isinstance(values, list):  # Lista wartości
                            query = query.filter(column_to_filter.in_(values))
                            print(f"Filter applied for list of values: {values}")

                        # Jeśli 'values' to ciąg znaków o długości co najmniej 3, stosujemy filtr 'LIKE'
                        elif isinstance(values, str) and len(values) >= 3:  # Minimalna długość dla LIKE
                            query = query.filter(column_to_filter.ilike(f"%{values}%"))
                            print(f"Partial match filter applied for: {values}")

                    else:
                        print(f"No column found for friendly_name: {friendly_name}")

            except json.JSONDecodeError as e:
                print(f"Error decoding JSON for filter_by: {str(e)}")
            except Exception as e:
                print(f"Unexpected error while processing filters: {str(e)}")

        # Mapowanie 'friendly_name' na kolumny do sortowania w tabeli SerwisWidok
        sort_column_name = None
        for column_name, column_info in SerwisWidok.COLUMN_NAME_MAP.items():
            if column_info['friendly_name'] == sort_by:
                sort_column_name = column_name
                break

        # Jeśli znaleziono odpowiednią kolumnę, wykonujemy sortowanie po niej
        # W przeciwnym razie domyślnie sortujemy po 'idSerwis'
        sort_column = getattr(SerwisWidok, sort_column_name, SerwisWidok.idSerwis)
        query = query.order_by(kierunek_sortowania(sort_column))

        # Pobranie wyników zapytania z bazy danych
        serwisy = query.all()

        # Konwersja wyników na format JSON
        wynik = [SerwisWidok.serialize(serwis) for serwis in serwisy]

        return jsonify(wynik), 200  # Zwracamy wynik w formacie JSON z kodem 200 (sukces)

    except Exception as e:
        # Jeśli wystąpił błąd, zwracamy szczegóły błędu w formacie JSON oraz kod 500 (błąd serwera)
        return jsonify({'error': str(e)}), 500


@serwis_bp.route('/serwis/validate', methods=['POST'])
def validate_serwis():
    """
    Endpoint do walidacji danych serwisu przed dodaniem lub edytowaniem.

    Parametry w formacie JSON:
        - ID pojazdu (int, opcjonalne): ID pojazdu, którego dotyczy serwis.
        - ID typu serwisu (int, opcjonalne): ID typu serwisu (np. Klimatyzacja, Silnik).
        - Data serwisu (string, opcjonalne): Data wykonania serwisu w formacie 'dd-mm-yyyy'.
        - Cena części netto (int, opcjonalne): Koszt części użytych w serwisie (w netto).
        - Koszt robocizny (int, opcjonalne): Koszt robocizny w serwisie (w netto).
        - Koszt całkowity netto (int, opcjonalne): Całkowity koszt serwisu (w netto).
            - Jeśli nie podano, zostanie automatycznie obliczony na podstawie ceny części i kosztu robocizny.
        - Przebieg (int, opcjonalne): Przebieg pojazdu w momencie serwisu.
        - Dodatkowe informacje (string, opcjonalne): Dodatkowe szczegóły dotyczące serwisu.

    Returns:
        Response:
            - 200 OK: Walidacja zakończona pomyślnie, dane są poprawne.
            - 400 Bad Request: Błąd walidacji danych, zwrócone szczegóły błędu w formacie JSON.
    """

    data = request.get_json()  # Pobieramy dane wejściowe w formacie JSON
    print(f"Data in validation api: {data}")

    # Walidacja danych serwisu
    validation_result = Serwis.validate_data(data)

    # Jeśli wynik walidacji jest dostępny, zwróć odpowiedni komunikat i kod statusu
    if validation_result:
        return jsonify(validation_result[0]), validation_result[1]

    return jsonify({'message': 'Dane są poprawne'}), 200  # Jeśli dane są poprawne, zwróć komunikat i kod 200
