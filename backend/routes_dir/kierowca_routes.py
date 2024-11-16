import json

from flask import Blueprint, request, jsonify
from Aplikacja_bazodanowa.backend.database import db
from Aplikacja_bazodanowa.backend.models import Kierowca
import traceback
from sqlalchemy import asc, desc, func

# Blueprint dla kierowców
kierowca_bp = Blueprint('kierowca', __name__)


# Pobieranie danych pojedynczego kierowcy
@kierowca_bp.route('/kierowca/show/<int:id>', methods=['GET'])
def pobierz_kierowce(id):
    try:
        kierowca = Kierowca.query.get(id)
        if kierowca is None:
            return jsonify({'message': 'Kierowca nie znaleziony'}), 404

        # Zastosowanie serializacji z przyjaznymi nazwami
        serialized_kierowca = Kierowca.serialize(kierowca)

        return jsonify(serialized_kierowca), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500



# Pobieranie listy wszystkich kierowców
@kierowca_bp.route('/kierowca/show/all', methods=['GET'])
def pobierz_wszystkich_kierowcow():
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

        return jsonify(unique_values), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@kierowca_bp.route('/kierowca/show', methods=['GET'])
def pobierz_i_sortuj_kierowcow():
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



# Pobieranie listy wszystkich kierowców
@kierowca_bp.route('/kierowca/show/alltochoice', methods=['GET'])
def pobierz_wszystkich_kierowcow_do_okna_wyboru():
    try:
        kierowcy = Kierowca.query.order_by(Kierowca.imie.asc(), Kierowca.nazwisko.asc()).all()
        wynik = []
        for kierowca in kierowcy:
            data = {'ID': kierowca.idKierowca, 'data': f"{kierowca.imie} {kierowca.nazwisko}, tel. {kierowca.nrTel}"}
            wynik.append(data)
        return jsonify(wynik), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Dodawanie nowego kierowcy
@kierowca_bp.route('/kierowca/add', methods=['POST'])
def dodaj_kierowce():
    data = request.get_json()

    # Deserializacja danych wejściowych
    deserialized_data = Kierowca.deserialize(data)
    # Tworzenie obiektu Kierowca na podstawie deserializowanych danych
    nowy_kierowca = Kierowca(**deserialized_data)

    try:
        db.session.add(nowy_kierowca)
        db.session.commit()
        return jsonify({'message': 'Kierowca dodany pomyślnie'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500




# Usuwanie kierowcy
@kierowca_bp.route('/kierowca/delete/<int:id>', methods=['DELETE'])
def usun_kierowce(id):
    try:
        kierowca = Kierowca.query.get(id)
        if kierowca is None:
            return jsonify({'message': 'Kierowca nie znaleziony'}), 404
        db.session.delete(kierowca)
        db.session.commit()
        return jsonify({'message': 'Kierowca usunięty pomyślnie'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# Edytowanie danych kierowcy
@kierowca_bp.route('/kierowca/edit/<int:id>', methods=['PUT'])
def edytuj_kierowce(id):
    data = request.get_json()

    # Deserializacja danych wejściowych
    deserialized_data = Kierowca.deserialize(data)
    print(f"Deserialized data: {deserialized_data}")
    try:
        kierowca = Kierowca.query.get(id)
        if kierowca is None:
            return jsonify({'message': 'Kierowca nie znaleziony'}), 404

        kierowca.imie = deserialized_data.get('imie', kierowca.imie)
        kierowca.nazwisko = deserialized_data.get('nazwisko', kierowca.nazwisko)
        kierowca.nrTel = deserialized_data.get('nrTel', kierowca.nrTel)

        db.session.commit()

        return jsonify({'message': 'Dane kierowcy zaktualizowane pomyślnie'}), 200

    except Exception as e:
        db.session.rollback()
        # Logowanie błędu w aplikacji serwera
        print(f"Błąd: {str(e)}")
        print(traceback.format_exc())  # Dodatkowe informacje o błędzie
        return jsonify({'error': 'Wystąpił problem z aktualizacją danych. Spróbuj ponownie później.'}), 500


@kierowca_bp.route('/kierowca/validate', methods=['POST'])
def validate_kierowca():
    data = request.get_json()
    print(f"Data in validation api: {data}")
    validation_result = Kierowca.validate_data(data)
    if validation_result:
        return jsonify(validation_result[0]), validation_result[1]

    return jsonify({'message': 'Dane są poprawne'}), 200

@kierowca_bp.route('/kierowca/sort', methods=['GET'])
def sort_pojazdy():
    # Pobierz parametry zapytania
    sort_by = request.args.get('sort_by', 'ID kierowcy')  # Domyślnie sortowanie po `idPojazd`
    order = request.args.get('order', 'asc')
    print(f"demanding sort_by: {sort_by}")

    sort_column_name = None
    kierunek_sortowania = asc if order == 'asc' else desc

    # Dla innych kolumn ustalamy sortowanie dynamicznie
    for column_name, column_info in Kierowca.COLUMN_NAME_MAP.items():
        if column_info['friendly_name'] == sort_by:
            sort_column_name = column_name
            break

    # Pobierz obiekt kolumny SQLAlchemy na podstawie `sort_column_name`
    sort_column = getattr(Kierowca, sort_column_name, Kierowca.idKierowca)
    sort_direction = kierunek_sortowania(sort_column)

    # Wykonaj zapytanie do bazy danych, sortując wyniki
    kierowcy = Kierowca.query.order_by(sort_direction).all()

    # Konwertuj wyniki na format JSON
    wynik = []
    for kierowca in kierowcy:
        wynik.append(Kierowca.serialize(kierowca))

    return jsonify(wynik), 200