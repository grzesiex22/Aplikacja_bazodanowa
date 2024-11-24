import traceback

from flask import Blueprint, request, jsonify
from sqlalchemy import func

from Aplikacja_bazodanowa.backend.database import db
from Aplikacja_bazodanowa.backend.models import Serwis, SerwisWidok, Pojazd, TypSerwisu
from datetime import datetime
import re

# Blueprint dla serwisów
serwis_bp = Blueprint('serwis', __name__)


# Pobieranie pojedynczego serwisu
@serwis_bp.route('/serwis/show/<int:id>', methods=['GET'])
def pobierz_serwis(id):
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


# Pobieranie wszystkich serwisów z możliwością filtrowania
@serwis_bp.route('/serwiswidok/show/all', methods=['GET'])
def pobierz_serwisy_widok():
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


# @serwis_bp.route('/serwis/filtry', methods=['GET'])
# def jakie_filtry_dla_serwisow():


# Dodawanie nowego serwisu
@serwis_bp.route('/serwis/add', methods=['POST'])
def dodaj_serwis():
    """
    Endpoint do dodawania nowego serwisu do bazy danych.

    Returns:
        Response: Odpowiedź w formacie JSON z komunikatem o sukcesie lub błędzie.
        int: Kod statusu HTTP, 201 dla sukcesu (dodanie serwisu), 500 w przypadku błędu.
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

    Parametry:
        id (int): ID serwisu do usunięcia.

    Returns:
        Response: Odpowiedź w formacie JSON z komunikatem o sukcesie lub błędzie.
        int: Kod statusu HTTP - 200 w przypadku sukcesu (usunięcie serwisu), 404, jeśli serwis nie znaleziony, 500 w przypadku błędu.
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

    Parametry:
        id (int): ID serwisu, który ma zostać edytowany.

    Returns:
        Response: Odpowiedź w formacie JSON z komunikatem o sukcesie lub błędzie.
        int: Kod statusu HTTP, 200 w przypadku sukcesu (aktualizacja serwisu), 404, jeśli serwis nie znaleziony, 500 w przypadku błędu.
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
    Endpoint do pobierania dostępnych filtrów dla serwisów z możliwością filtrowania według rodzaju serwisu
    oraz według innych kryteriów, takich jak dane kierowcy.

    W przyupadku "Dane kierowcy" zwraca JSON którego elementy to słowniki: {'ID': ... , 'data': ....}

    Parametry zapytania:
        Typ serwisu (str, opcjonalny): Typ serwisu, według którego chcemy filtrować wyniki. (domyślnie: None)
        filtr (str): Przyjazna nazwa filtru określająca, według której kolumny chcemy filtrować.

    Returns:
        Tuple[Response, int]: Krotka zawierająca:
            - Response (JSON) : zawiera listę zserializowanych danych serwisów, jeśli znaleziono serwisy.
            - Code (int) : Kod statusu HTTP, np. 200 dla sukcesu lub 500, jeśli wystąpił błąd serwera.
    """
    # Pobranie parametrów zapytania z URL (typ filtru - kolumna)
    typ_filtru = request.args.get('filtr')

    print(f"api: pobierz_filtry_dla_serwisy")
    print(f"Pobrany typ filtru {typ_filtru}")

    # Mapowanie `friendly_name` z parametru `filtr` na właściwą kolumnę w modelu Serwis
    filtr_column_name = None
    for column_name, column_info in SerwisWidok.COLUMN_NAME_MAP.items():
        if column_info['friendly_name'] == typ_filtru:
            filtr_column_name = column_name
            break  # Zatrzymanie pętli po znalezieniu kolumny

    # # Specjalny przypadek dla filtrowania po danych kierowcy
    # if typ_filtru == 'Dane pojazdu':
    #     filtr_column_name = 'idPojazd'
    # elif typ_filtru == 'Typ serwisu':
    #     filtr_column_name = 'idTypSerwisu'



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


@serwis_bp.route('/serwis/filtry', methods=['GET'])
def jakie_filtry_dla_serwisu():  # nie działa chyba
    """
    Endpoint do pobierania dostępnych filtrów dla serwisów z możliwością filtrowania według rodzaju serwisu
    oraz według innych kryteriów, takich jak dane kierowcy.

    W przyupadku "Dane kierowcy" zwraca JSON którego elementy to słowniki: {'ID': ... , 'data': ....}

    Parametry zapytania:
        Typ serwisu (str, opcjonalny): Typ serwisu, według którego chcemy filtrować wyniki. (domyślnie: None)
        filtr (str): Przyjazna nazwa filtru określająca, według której kolumny chcemy filtrować.

    Returns:
        Tuple[Response, int]: Krotka zawierająca:
            - Response (JSON) : zawiera listę zserializowanych danych serwisów, jeśli znaleziono serwisy.
            - Code (int) : Kod statusu HTTP, np. 200 dla sukcesu lub 500, jeśli wystąpił błąd serwera.
    """
    # Pobranie parametrów zapytania z URL (typ filtru - kolumna)
    typ_filtru = request.args.get('filtr')

    print(f"api: pobierz_filtry_dla_serwisy")
    print(f"Pobrany typ filtru {typ_filtru}")

    # Mapowanie `friendly_name` z parametru `filtr` na właściwą kolumnę w modelu Serwis
    filtr_column_name = None
    for column_name, column_info in Serwis.COLUMN_NAME_MAP.items():
        if column_info['friendly_name'] == typ_filtru:
            filtr_column_name = column_name
            break  # Zatrzymanie pętli po znalezieniu kolumny

    # Specjalny przypadek dla filtrowania po danych kierowcy
    if typ_filtru == 'Dane pojazdu':
        filtr_column_name = 'idPojazd'
    elif typ_filtru == 'Typ serwisu':
        filtr_column_name = 'idTypSerwisu'



    print(f"Znaleziona nazwa kolumny do filtrowania: {filtr_column_name}")

    # Sprawdzenie, czy znaleziono kolumnę do filtrowania; jeśli nie, zgłaszamy błąd
    if filtr_column_name is None:
        return jsonify(f"Nie znaleziono kolumny: '{typ_filtru}' w tabeli {Serwis.__name__}"), 400

    try:
        # Obsługa przypadku, gdy filtrujemy po danych pojazdu
        if filtr_column_name == 'idPojazd':
            # Pobranie listy wszystkich kierowców powiązanych z serwisami, posortowanych alfabetycznie
            pojazdy_query = Pojazd.query.order_by(Pojazd.marka.asc(), Pojazd.model.asc()).all()

            # Formatowanie wyników dla każdego kierowcy do listy
            unique_values = []
            data = {
                'ID': None,
                'data': f"Brak pojazdu"}
            unique_values.append(data)

            for pojazd in pojazdy_query:
                data = {
                    'ID': pojazd.idPojazd,
                    'data': f"{pojazd.marka}, {pojazd.model}, nr rej. {pojazd.nrRejestracyjny}"}
                unique_values.append(data)

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
                    'ID': typserwisu.idPojazd,
                    'data': f"{typserwisu.typPojazdu}, {typserwisu.rodzajSerwisu}"}
                unique_values.append(data)

        else:
            column_to_filter = getattr(Serwis, filtr_column_name, None)
            # Jeśli nie znaleziono kolumny w modelu Serwis, zgłaszamy błąd
            if column_to_filter is None:
                return jsonify({'error': f"Kolumna '{filtr_column_name}' nie istnieje w modelu Serwis."}), 400

            # Tworzymy zapytanie do bazy danych, aby uzyskać unikalne wartości w tej kolumnie
            unique_values_query = (
                Serwis.query
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


@serwis_bp.route('/serwis/validate', methods=['POST'])
def validate_serwis():
    """
    Endpoint do walidacji danych serwisu przed dodaniem lub edytowaniem.

    Returns:
        Response: Odpowiedź w formacie JSON z komunikatem o błędzie, jeśli dane są niepoprawne, lub potwierdzeniem poprawności danych.
        int: Kod statusu HTTP - 200, jeśli dane są poprawne - 400, jeśli dane są błędne.
    """
    data = request.get_json()  # Pobieramy dane wejściowe w formacie JSON
    print(f"Data in validation api: {data}")

    # Walidacja danych serwisu
    validation_result = Serwis.validate_data(data)

    # Jeśli wynik walidacji jest dostępny, zwróć odpowiedni komunikat i kod statusu
    if validation_result:
        return jsonify(validation_result[0]), validation_result[1]

    return jsonify({'message': 'Dane są poprawne'}), 200  # Jeśli dane są poprawne, zwróć komunikat i kod 200


