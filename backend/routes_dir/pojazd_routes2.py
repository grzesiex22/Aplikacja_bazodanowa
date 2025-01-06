from typing import Tuple

from flask import Blueprint, request, jsonify, Response
from Aplikacja_bazodanowa.backend.database import db
from Aplikacja_bazodanowa.backend.models import Pojazd, Kierowca, TypPojazdu
import re
import traceback
from sqlalchemy import asc, desc, func
import json


# Blueprint dla pojazdów
pojazd_bp = Blueprint('pojazd', __name__)


@pojazd_bp.route('/pojazd/show/<int:id>', methods=['GET'])
def pobierz_pojazd(id):
    """
     Endpoint do pobierania szczegółowych informacji o pojeździe na podstawie jego unikalnego identyfikatora.

     Parametry URL:
         - id (int): Identyfikator pojazdu, którego szczegóły chcemy pobrać.

    Returns:
        Response:
        - 200 OK: Zwraca dane pojazdu, w tym:
            - ID pojazdu
            - Marka
            - Model
            - Numer rejestracyjny
            - Typ pojazdu
            - Dodatkowe informacje
            - ID kierowca
            - Dane kierowcy
        - 404 Not Found: Jeśli pojazd o podanym identyfikatorze nie został znaleziony.
        - 500 Internal Server Error: W przypadku błędu serwera.
     """
    print(f"pojazd/show/{id}")
    try:
        # Pobranie pojazdu z bazy danych na podstawie podanego ID
        pojazd = Pojazd.query.get(id)

        # Sprawdzenie, czy pojazd istnieje
        if pojazd is None:
            return jsonify({'message': 'Pojazd nie znaleziony'}), 404

        # Serializacja obiektu pojazdu z przyjaznymi nazwami pól
        serialized_pojazd = Pojazd.serialize(pojazd)

        # Zwrócenie zserializowanych danych pojazdu
        return jsonify(serialized_pojazd), 200
    except Exception as e:
        # Obsługa błędów: zwracamy szczegóły błędu w odpowiedzi
        return jsonify({'error': str(e)}), 500


############ http://127.0.0.1:5000/pojazd/show/all?typPojazdu=Ciągnik #############
@pojazd_bp.route('/pojazd/show/all', methods=['GET'])
def pobierz_pojazdy():
    """
     Endpoint do pobierania listy wszystkich pojazdów z bazy danych.

    Parametry wejściowe:
        - typPojazdu (str, opcjonalny): Typ pojazdu, według którego chcemy filtrować wyniki (domyślnie: brak filtru).

    Returns:
        Response:
        - 200 OK: Zwraca listę pojazdów składającą się z:
             - ID pojazdu
             - Marka
             - Model
             - Numer rejestracyjny
             - Typ pojazdu
             - Dodatkowe informacje
             - ID kierowca
             - Dane kierowcy
         - 500 Internal Server Error: W przypadku błędu serwera.
     """
    # Pobieramy parametr 'typPojazdu' z zapytania, aby filtrować wyniki (opcjonalnie)
    typ_pojazdu = request.args.get('typPojazdu')

    try:
        # Sprawdzamy, czy podano typ pojazdu do filtrowania
        if typ_pojazdu:
            # Filtrujemy pojazdy po zadanym typie, jeśli typ jest określony
            pojazdy = Pojazd.query.filter_by(typPojazdu=typ_pojazdu).all()
        else:
            # Jeśli typ pojazdu nie jest podany, pobieramy wszystkie pojazdy
            pojazdy = Pojazd.query.all()

        # Inicjalizacja listy do przechowywania wyników
        wynik = []
        for pojazd in pojazdy:
            # Serializujemy każdy pojazd i dodajemy do listy wyników
            wynik.append(Pojazd.serialize(pojazd))

        # Zwracamy listę zserializowanych pojazdów w formacie JSON
        return jsonify(wynik), 200

    except Exception as e:
        # Obsługa błędów: zwracamy szczegóły błędu w odpowiedzi
        return jsonify({'error': str(e)}), 500


@pojazd_bp.route('/pojazd/filtry', methods=['GET'])
def jakie_filtry_dla_pojazdy():
    """
    Endpoint do pobierania dostępnych unikalnych filtrów dla pojazdów, z możliwością filtrowania według rodzaju pojazdu
    oraz według innych kryteriów, takich jak dane kierowcy.

    Parametry wejściowe:
        - Typ pojazdu (str, opcjonalny): Typ pojazdu, według którego chcemy filtrować wyniki (domyślnie: brak filtru).
        - filtr (str, wymagany): Przyjazna nazwa filtru określająca, według której kolumny chcemy filtrować.

    Returns:
        Response:
            - 200 OK: Zwraca posortowaną listę unikalnych wartości w formacie JSON.
            - 400 Bad Request: Jeśli wystąpi błąd związany z niewłaściwą nazwą kolumny lub innymi parametrami.
            - 500 Internal Server Error: W przypadku błędu serwera.
    """
    # Pobranie parametrów zapytania z URL (opcjonalnie: typ pojazdu i typ filtru)
    rodzaj_pojazdu = request.args.get('Typ pojazdu', None)  # (opcjonalne)
    typ_filtru = request.args.get('filtr')

    print(f"api: pobierz_filtry_dla_pojazdy")
    print(f"Pobrany typ filtru {typ_filtru}")

    # Mapowanie `friendly_name` z parametru `filtr` na właściwą kolumnę w modelu Pojazd
    filtr_column_name = None
    for column_name, column_info in Pojazd.COLUMN_NAME_MAP.items():
        if column_info['friendly_name'] == typ_filtru:
            filtr_column_name = column_name
            break  # Zatrzymanie pętli po znalezieniu kolumny

    # Specjalny przypadek dla filtrowania po danych kierowcy
    if typ_filtru == 'Dane kierowcy':
        filtr_column_name = 'idKierowca'

    print(f"Znaleziona nazwa kolumny do filtrowania: {filtr_column_name}")

    # Sprawdzenie, czy znaleziono kolumnę do filtrowania; jeśli nie, zgłaszamy błąd
    if filtr_column_name is None:
        return jsonify(f"Nie znaleziono kolumny: '{typ_filtru}' w tabeli {Pojazd.__name__}"), 400

    try:
        # Obsługa przypadku, gdy filtrujemy po danych kierowcy
        if filtr_column_name == 'idKierowca':
            # Pobranie listy wszystkich kierowców powiązanych z pojazdami, posortowanych alfabetycznie
            kierowcy_query = Kierowca.query.order_by(Kierowca.imie.asc(), Kierowca.nazwisko.asc()).all()

            # Formatowanie wyników dla każdego kierowcy do listy
            unique_values = []
            data = {
                'ID': None,
                'data': f"Brak kierowcy"}
            unique_values.append(data)

            for kierowca in kierowcy_query:
                data = {
                    'ID': kierowca.idKierowca,
                    'data': f"{kierowca.imie} {kierowca.nazwisko}, tel. {kierowca.nrTel}"}
                unique_values.append(data)

        elif rodzaj_pojazdu:
            # Sprawdzamy, czy kolumna 'typPojazdu' istnieje w tabeli Pojazd
            if not hasattr(Pojazd, 'typPojazdu'):
                return jsonify({'error': "Kolumna 'typPojazdu' nie istnieje w tabeli Pojazd."}), 400  # Błąd, jeśli kolumna 'typPojazdu' nie istnieje

            # Dodatkowy filtr po rodzaju pojazdu, jeśli rodzaj_pojazdu jest określony
            filtr_column_name2 = 'typPojazdu'
            typPojazduFilter = getattr(Pojazd, filtr_column_name2, None)

            # Podstawowy filtr po
            column_to_filter = getattr(Pojazd, filtr_column_name, None)
            # Jeśli nie znaleziono kolumny dla podstawowoego filtru w modelu Pojazd, zgłaszamy błąd
            if column_to_filter is None:
                return jsonify({'error': f"Kolumna '{filtr_column_name}' nie istnieje w modelu Pojazd."}), 400

            unique_values_query = (
                Pojazd.query
                    .filter_by(typPojazdu=rodzaj_pojazdu)  # Filtrowanie po rodzaju pojazdu
                    .with_entities(func.lower(column_to_filter).label('unique_value'))  # Pobranie unikalnych wartości
                    .distinct()  # Unikalne wartości
            )
            # Konwersja wyniku zapytania na listę wartości
            unique_values = [row.unique_value for row in unique_values_query]
            # Sortowanie wynikowej listy unikalnych wartości
            unique_values.sort()

        else:
            # Bez filtrowania po rodzaju pojazdu, tylko po wybranej kolumnie
            column_to_filter = getattr(Pojazd, filtr_column_name, None)
            # Jeśli nie znaleziono kolumny w modelu Pojazd, zgłaszamy błąd
            if column_to_filter is None:
                return jsonify({'error': f"Kolumna '{filtr_column_name}' nie istnieje w modelu Pojazd."}), 400

            # Tworzymy zapytanie do bazy danych, aby uzyskać unikalne wartości w tej kolumnie
            unique_values_query = (
                Pojazd.query
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


@pojazd_bp.route('/pojazd/show', methods=['GET'])
def pobierz_i_sortuj_pojazdy():
    """
    Endpoint do pobierania i sortowania pojazdów z możliwością filtrowania według różnych kryteriów.

    Parametry wejściowe:
        - filter_by (str, opcjonalny): Filtr w formacie JSON, który umożliwia filtrowanie pojazdów na podstawie różnych kryteriów.
          Domyślnie '{}' (brak filtra).
        - sort_by (str, opcjonalny): Kolumna, według której mają zostać posortowane wyniki (domyślnie 'ID pojazdu').
          Możliwe wartości: 'Dane kierowcy' lub nazwy kolumn w tabeli Pojazd.
        - order (str, opcjonalny): Kierunek sortowania, 'asc' dla rosnącego, 'desc' dla malejącego (domyślnie 'asc').

        Returns:
            Response:
                - 200 OK: Zwraca listę pojazdów składającą się z:
                     - ID pojazdu
                     - Marka
                     - Model
                     - Numer rejestracyjny
                     - Typ pojazdu
                     - Dodatkowe informacje
                     - ID kierowca
                     - Dane kierowcy
                 - 500 Internal Server Error: Zwraca komunikat o błędzie w przypadku problemów z zapytaniem do bazy danych.
    """

    # Pobieramy poszczególne parametry zapytania
    filter_by = request.args.get('filter_by', '{}')  # Filtrowanie - domyślnie '{}' jeśli brak
    sort_by = request.args.get('sort_by', 'ID pojazdu')  # Sortowanie domyślnie po 'ID pojazdu'
    order = request.args.get('order', 'asc')  # Domyślny kierunek sortowania to 'asc'

    # Logowanie parametrów zapytania dla celów debugowania
    print(f"api: pobierz i sortuj pojazdy")
    print(f"Filter by: {filter_by}")
    print(f"Sort by: {sort_by}")
    print(f"Order: {order}")

    # Ustalanie kierunku sortowania na podstawie wartości 'order'
    kierunek_sortowania = asc if order == 'asc' else desc  # Ustalanie kierunku sortowania

    try:
        # Budowanie podstawowego zapytania do bazy danych
        query = db.session.query(Pojazd)

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

                    # Mapowanie 'friendly_name' na odpowiadającą kolumnę w tabeli Pojazd
                    column_name = None

                    # Obsługuje specjalny przypadek dla 'Dane kierowcy'
                    if friendly_name == 'Dane kierowcy':
                        print("Handling 'Dane kierowcy' filter")

                        # Lista IDs kierowców, którzy są zaznaczeni w filtrze (pomijamy None)
                        kierowcy_ids = [kierowca['ID'] for kierowca in values if kierowca['ID'] is not None]
                        print(f"Kierowcy IDs (excluding None): {kierowcy_ids}")

                        # Jeśli filtr zawiera "Brak kierowcy" (ID: None), uwzględniamy pojazdy bez przypisanego kierowcy
                        if any(kierowca['ID'] is None for kierowca in values):
                            print("Including vehicles without a driver (idKierowca IS NULL)")
                            query = query.filter((Pojazd.idKierowca.is_(None)) | Pojazd.idKierowca.in_(kierowcy_ids))
                        else:
                            # Filtrujemy tylko po przypisanych kierowcach
                            query = query.filter(Pojazd.idKierowca.in_(kierowcy_ids))

                        print("Filter applied for 'Dane kierowcy' by IDs.")
                    else:
                        # Mapowanie na inne kolumny w tabeli Pojazd
                        print(f"Searching for column corresponding to {friendly_name}")
                        for column, column_info in Pojazd.COLUMN_NAME_MAP.items():
                            if column_info['friendly_name'] == friendly_name:
                                column_name = column
                                print(f"Found column: {column_name}")
                                break

                        # Jeśli znaleziono odpowiadającą kolumnę, dodajemy filtr
                        if column_name:
                            column_to_filter = getattr(Pojazd, column_name)
                            print(f"Applying filter for column {column_name}")

                            # Jeśli 'values' to lista, filtrujemy na podstawie tej listy
                            if isinstance(values, list):  # Lista wartości
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

        # Ustalanie kolumny do sortowania
        if sort_by == "Dane kierowcy":
            # Sortowanie po imieniu i nazwisku kierowcy
            query = query.join(Kierowca, Pojazd.idKierowca == Kierowca.idKierowca, isouter=True)
            query = query.order_by(
                kierunek_sortowania(Kierowca.imie.is_(None)),
                # Pojazdy bez kierowcy na początku lub końcu (zależnie od kierunku)
                kierunek_sortowania(Kierowca.imie),
                kierunek_sortowania(Kierowca.nazwisko)
            )
        else:
            # Mapowanie 'friendly_name' na kolumny do sortowania w tabeli Pojazd
            sort_column_name = None
            for column_name, column_info in Pojazd.COLUMN_NAME_MAP.items():
                if column_info['friendly_name'] == sort_by:
                    sort_column_name = column_name
                    break

            # Jeśli znaleziono odpowiednią kolumnę, wykonujemy sortowanie po niej
            # W przeciwnym razie domyślnie sortujemy po 'idPojazd'
            sort_column = getattr(Pojazd, sort_column_name, Pojazd.idPojazd)
            query = query.order_by(kierunek_sortowania(sort_column))

        # Pobranie wyników zapytania z bazy danych
        pojazdy = query.all()

        # Konwersja wyników na format JSON
        wynik = [Pojazd.serialize(pojazd) for pojazd in pojazdy]

        return jsonify(wynik), 200  # Zwracamy wynik w formacie JSON z kodem 200 (sukces)

    except Exception as e:
        # Jeśli wystąpił błąd, zwracamy szczegóły błędu w formacie JSON oraz kod 500 (błąd serwera)
        return jsonify({'error': str(e)}), 500


# Pobieranie listy wszystkich kierowców
@pojazd_bp.route('/pojazd/show/alltochoice', methods=['GET'])
def pobierz_wszystkie_pojazdy_do_okna_wyboru():
    """
    Endpoint do pobierania listy wszystkich pojazdów w formacie dostosowanym do okna wyboru.

    Returns:
        Response:
        - 200 OK: Zwraca listę pojazdów w formacie JSON.
            - "ID": <idPojazdu>,
            - "data": "<typPojazdu>, <marka>, <model>, nr rej. <nrRejestracyjny>"
        - 500 Internal Server Error: W przypadku błędu serwera.
    """
    try:
        pojazdy = Pojazd.query.order_by(Pojazd.typPojazdu.asc(), Pojazd.marka.asc(), Pojazd.model.asc()).all()
        wynik = []
        for pojazd in pojazdy:
            data = {'ID': pojazd.idPojazd, 'data': f"{pojazd.typPojazdu.value}, {pojazd.marka}, {pojazd.model}, nr rej. {pojazd.nrRejestracyjny}"}
            wynik.append(data)
        return jsonify(wynik), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Dodawanie nowego pojazdu
@pojazd_bp.route('/pojazd/add', methods=['POST'])
def dodaj_pojazd():
    """
    Endpoint do dodawania nowego pojazdu do bazy danych.

    Parametry w formacie JSON:
        - ID kierowca (int, opcjonalny): ID kierowcy.
        - Typ pojazdu (string, wymagane): Typ pojazdu (np. Ciągnik, Naczepa).
        - Marka (string, wymagane): Marka pojazdu.
        - Model (string, wymagane): Model pojazdu.
        - Numer rejestracyjny (string, wymagane): Numer rejestracyjny pojazdu.
        - Dodatkowe informacje (string, opcjonalny): Dodatkowe informacje o pojeździe.

    Returns:
        Response:
            - 201 Created: Pojazd został pomyślnie dodany do bazy danych.
            - 500 Internal Server Error: W przypadku błędu podczas dodawania pojazdu.
    """

    data = request.get_json()  # Pobieramy dane wejściowe w formacie JSON

    # Deserializacja danych wejściowych do obiektu
    deserialized_data = Pojazd.deserialize(data)
    # Tworzymy nowy obiekt pojazdu na podstawie deserializowanych danych
    nowy_pojazd = Pojazd(**deserialized_data)

    try:
        # Dodanie nowego pojazdu do sesji bazy danych
        db.session.add(nowy_pojazd)
        db.session.commit()  # Zatwierdzamy zmiany w bazie danych
        return jsonify({'message': 'Pojazd dodany pomyślnie'}), 201  # Zwracamy komunikat o sukcesie

    except Exception as e:
        db.session.rollback()  # W przypadku błędu anulujemy sesję
        return jsonify({'error': str(e)}), 500  # Zwracamy komunikat o błędzie i kod 500


# Usuwanie pojazdu
@pojazd_bp.route('/pojazd/delete/<int:id>', methods=['DELETE'])
def usun_pojazd(id):
    """
    Endpoint do usuwania pojazdu z bazy danych na podstawie jego ID.

    Parametry URL:
        id (int): ID pojazdu, który ma zostać usunięty.

    Returns:
        Response:
            - Jeśli usunięcie zakończy się sukcesem: Zwraca komunikat o sukcesie w formacie JSON oraz kod statusu 200.
            - Jeśli pojazd o podanym ID nie istnieje: Zwraca komunikat o błędzie w formacie JSON oraz kod statusu 404.
            - W przypadku błędu: Zwraca szczegóły błędu w formacie JSON oraz kod statusu 500.
    """
    try:
        # Pobranie pojazdu na podstawie ID
        pojazd = Pojazd.query.get(id)
        if pojazd is None:
            return jsonify({'message': 'Pojazd nie znaleziony'}), 404  # Jeśli pojazd nie istnieje, zwróć błąd 404

        db.session.delete(pojazd)  # Usuwamy pojazd z bazy
        db.session.commit()  # Zatwierdzamy zmiany w bazie danych
        return jsonify({'message': 'Pojazd usunięty pomyślnie'}), 200  # Zwracamy komunikat o sukcesie

    except Exception as e:
        db.session.rollback()  # W przypadku błędu anulujemy sesję
        return jsonify({'error': str(e)}), 500  # Zwracamy komunikat o błędzie i kod 500


# Edytowanie danych pojazdu
@pojazd_bp.route('/pojazd/edit/<int:id>', methods=['PUT'])
def edytuj_pojazd(id):
    """
    Endpoint do edytowania danych istniejącego pojazdu na podstawie jego identyfikatora.

    Parametry URL:
        - id (int): Identyfikator pojazdu w bazie danych, który ma zostać zaktualizowany.

    Parametry w formacie JSON:
        - ID kierowca (int, opcjonalny): ID kierowcy przypisanego do pojazdu.
        - Typ pojazdu (string, opcjonalny): Typ pojazdu (np. Ciągnik, Naczepa).
        - Marka (string, opcjonalny): Marka pojazdu.
        - Model (string, opcjonalny): Model pojazdu.
        - Numer rejestracyjny (string, opcjonalny): Numer rejestracyjny pojazdu.
        - Dodatkowe informacje (string, opcjonalny): Dodatkowe informacje o pojeździe.

    Returns:
        Response:
            - 200 OK: Pojazd został pomyślnie zaktualizowany.
            - 404 Not Found: Pojazd o podanym identyfikatorze nie został znaleziony.
            - 500 Internal Server Error: Wystąpił problem z aktualizacją danych w bazie.
    """

    data = request.get_json()  # Pobieramy dane wejściowe w formacie JSON

    # Deserializacja danych wejściowych do obiektu
    deserialized_data = Pojazd.deserialize(data)
    print(f"Deserialized data: {deserialized_data}")

    try:
        # Pobranie pojazdu na podstawie ID
        pojazd = Pojazd.query.get(id)
        if pojazd is None:
            # Jeśli pojazd o podanym ID nie został znaleziony
            return jsonify({'message': 'Pojazd nie znaleziony'}), 404  # Jeśli pojazd nie istnieje, zwróć błąd 404

        # Aktualizacja pól pojazdu na podstawie deserializowanych danych
        pojazd.idKierowca = deserialized_data.get('idKierowca', pojazd.idKierowca)
        pojazd.typPojazdu = deserialized_data.get('typPojazdu', pojazd.typPojazdu)
        pojazd.marka = deserialized_data.get('marka', pojazd.marka)
        pojazd.model = deserialized_data.get('model', pojazd.model)
        pojazd.nrRejestracyjny = deserialized_data.get('nrRejestracyjny', pojazd.nrRejestracyjny)
        pojazd.dodatkoweInf = deserialized_data.get('dodatkoweInf', pojazd.dodatkoweInf)

        db.session.commit()  # Zatwierdzamy zmiany w bazie danych

        return jsonify({'message': 'Dane pojazdu zaktualizowane pomyślnie'}), 200  # Zwracamy komunikat o sukcesie

    except Exception as e:
        # W przypadku błędu anulujemy zmiany w bieżącej sesji
        db.session.rollback()
        print(f"Błąd: {str(e)}")
        print(traceback.format_exc())  # Wypisanie szczegółów błędu
        return jsonify({'error': 'Wystąpił problem z aktualizacją danych. Spróbuj ponownie później.'}), 500  # Komunikat o błędzie


@pojazd_bp.route('/pojazd/validate', methods=['POST'])
def validate_pojazd():
    """
    Endpoint do walidacji danych pojazdu przed dodaniem lub edytowaniem.

    Parametry w formacie JSON:
        - ID kierowca (int, opcjonalny): ID kierowcy przypisanego do pojazdu.
        - Typ pojazdu (string, opcjonalny): Typ pojazdu (np. Ciągnik, Naczepa).
        - Marka (string, wymagane): Marka pojazdu.
        - Model (string, wymagane): Model pojazdu.
        - Numer rejestracyjny (string, wymagane): Numer rejestracyjny pojazdu.
        - Dodatkowe informacje (string, opcjonalny): Dodatkowe informacje o pojeździe.

    Returns:
        Response:
            - 200 OK: Dane pojazdu są poprawne.
            - 400 Bad Request: Dane pojazdu zawierają błędy (np. nieprawidłowy numer rejestracyjny).
    """

    data = request.get_json()  # Pobieramy dane wejściowe w formacie JSON
    print(f"Data in validation api: {data}")

    # Walidacja danych pojazdu
    validation_result = Pojazd.validate_data(data)

    # Jeśli wynik walidacji jest dostępny, zwróć odpowiedni komunikat i kod statusu
    if validation_result:
        return jsonify(validation_result[0]), validation_result[1]

    return jsonify({'message': 'Dane są poprawne'}), 200  # Jeśli dane są poprawne, zwróć komunikat i kod 200

@pojazd_bp.route('/pojazd/typpojazdu/<int:id>', methods=['GET'])
def jaki_typ_pojazdu(id):
    """
    Endpoint do pobierania typu pojazdu na podstawie jego ID.

    Parametry URL:
        id (int): ID pojazdu, którego typ ma zostać pobrany.

    Returns:
        Response:
            - Jeśli pojazd istnieje: Zwraca typ pojazdu w formacie JSON oraz kod statusu 200.
            - Jeśli pojazd nie istnieje: Zwraca komunikat o błędzie w formacie JSON oraz kod statusu 404.
            - W przypadku błędu: Zwraca szczegóły błędu w formacie JSON oraz kod statusu 500.
    """
    try:
        # Pobranie pojazdu z bazy danych na podstawie podanego ID
        pojazd = Pojazd.query.get(id)

        # Sprawdzenie, czy pojazd istnieje
        if pojazd is None:
            return jsonify({'message': 'Pojazd nie znaleziony'}), 404

        # Pobranie typu pojazdu z obiektu 'Pojazd'
        typ_pojazdu = pojazd.typPojazdu.value
        print(typ_pojazdu)
        return jsonify({'typ_pojazdu': typ_pojazdu}), 200

    except Exception as e:
        # Obsługa błędów: zwracamy szczegóły błędu w odpowiedzi
        return jsonify({'error': str(e)}), 500
