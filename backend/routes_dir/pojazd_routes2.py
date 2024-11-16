from flask import Blueprint, request, jsonify
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
    print(f"pojazd/show/{id}")
    try:
        pojazd = Pojazd.query.get(id)
        if pojazd is None:
            return jsonify({'message': 'Pojazd nie znaleziony'}), 404

        # Zastosowanie serializacji z przyjaznymi nazwami
        serialized_pojazd = Pojazd.serialize(pojazd)

        return jsonify(serialized_pojazd), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


############ http://127.0.0.1:5000/pojazd/show/all?typPojazdu=Ciągnik ############# (wyświetli tylko ciągniki)
@pojazd_bp.route('/pojazd/show/all', methods=['GET'])
def pobierz_pojazdy():
    typ_pojazdu = request.args.get('typPojazdu')  # Pobieramy parametr 'typPojazdu' z zapytania

    try:
        if typ_pojazdu:
            # Filtrowanie po typie pojazdu
            pojazdy = Pojazd.query.filter_by(typPojazdu=typ_pojazdu).all()
        else:
            # Jeśli nie podano typu pojazdu, pobieramy wszystkie pojazdy
            pojazdy = Pojazd.query.all()

        wynik = []
        for pojazd in pojazdy:
            wynik.append(Pojazd.serialize(pojazd))

        return jsonify(wynik), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@pojazd_bp.route('/pojazd/filtry', methods=['GET'])
def jakie_filtry_dla_pojazdy():
    rodzaj_pojazdu = request.args.get('Typ pojazdu')  # Pobieramy parametr 'typPojazdu' z zapytania
    typ_filtru = request.args.get('filtr')  # Pobieramy parametr 'typPojazdu' z zapytania
    print(f"api: pobierz_filtry_dla_pojazdy")
    print(f"Pobrany typ filtru {typ_filtru}")

    # Mapowanie `friendly_name` na rzeczywiste kolumny `Pojazd`
    filtr_column_name = None
    for column_name, column_info in Pojazd.COLUMN_NAME_MAP.items():
        if column_info['friendly_name'] == typ_filtru:
            filtr_column_name = column_name
            break

    if typ_filtru == 'Dane kierowcy':
        filtr_column_name = 'idKierowca'

    filtr_column_name2 = ''
    if rodzaj_pojazdu == 'Typ pojazdu':
        filtr_column_name2 = 'typPojazdu'  # Kolumna dla typu pojazdu w enum

    print(f"Znaleziona nazwa kolumny do filtrowania: {filtr_column_name}")
    # Sprawdzenie, czy znaleziono kolumnę. Jeśli nie, zgłaszamy błąd.
    if filtr_column_name is None:
        return jsonify(f"Nie znaleziono kolumny: '{typ_filtru}' w tabeli {Pojazd.__name__}"), 400

    try:
        if filtr_column_name == 'idKierowca':
            # Pobieramy wszystkie dane kierowcy powiązane z pojazdami
            kierowcy_query = Kierowca.query.order_by(Kierowca.imie.asc(), Kierowca.nazwisko.asc()).all()

            # Formatowanie wyników jako stringi
            unique_values = []
            for kierowca in kierowcy_query:
                data = {kierowca.idKierowca, f"{kierowca.imie} {kierowca.nazwisko}, tel. {kierowca.nrTel}"}
                unique_values.append(data)
        else:

            column_to_filter = getattr(Pojazd, filtr_column_name, None)
            typPojazduFilter = getattr(Pojazd, filtr_column_name2, None)
            if column_to_filter is None:
                return jsonify({'error': f"Kolumna '{filtr_column_name}' nie istnieje w modelu Pojazd."}), 400

            # Zapytanie do bazy danych: unikalne wartości z ignorowaniem wielkości liter
            unique_values_query = (
                Pojazd.query
                .with_entities(func.lower(column_to_filter).label('unique_value'))  # Konwertujemy na małe litery
                .distinct()  # Wybieramy tylko unikalne wartości
            )
            # Pobrane wartości zamieniamy na listę
            unique_values = [row.unique_value for row in unique_values_query]

            unique_values.sort()

        return jsonify(unique_values), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# @pojazd_bp.route('/pojazd/show', methods=['GET'])
# def pobierz_i_sortuj_pojazdy():
#     # Pobierz parametry zapytania jako słownik
#     combined_params = request.args.to_dict()
#
#     typ_pojazdu = request.args.get('typPojazdu')
#     sort_by = combined_params.get('sort_by', 'ID pojazdu')  # Domyślnie sortowanie po `idPojazd`
#     order = combined_params.get('order', 'asc')  # Domyślny kierunek sortowania to `asc`
#
#     # Ustal kierunek sortowania
#     kierunek_sortowania = asc if order == 'asc' else desc
#
#     try:
#         # Budowanie podstawowego zapytania
#         query = db.session.query(Pojazd)
#
#         # Filtrowanie po `typPojazdu`, jeśli podano
#         if typ_pojazdu:
#             query = query.filter(Pojazd.typPojazdu == typ_pojazdu)
#
#         id_kierowca = combined_params.get('idKierowca')
#
#         if id_kierowca:
#             query = query.filter(Pojazd.idKierowca == id_kierowca)
#
#         # Dynamiczne filtrowanie na podstawie przekazanych parametrów
#         for param, value in combined_params.items():
#             if param in ['marka', 'model', 'nrRejestracyjny', 'dodatkoweInf']:  # Możesz dodać inne parametry do listy
#                 query = query.filter(getattr(Pojazd, param).ilike(f"%{value}%"))
#
#             # Filtrowanie po `imie` i `nazwisko` jeśli podano
#             if param == 'imie' or param == 'nazwisko':
#                 query = query.join(Kierowca, Pojazd.idKierowca == Kierowca.idKierowca)
#                 query = query.filter(getattr(Kierowca, param).ilike(f"%{value}%"))
#
#         # Ustalanie kolumny do sortowania
#         if sort_by == "Dane kierowcy":
#             # Sortowanie po `imie` i `nazwisko` w tabeli Kierowca
#             query = query.join(Kierowca, Pojazd.idKierowca == Kierowca.idKierowca)
#             query = query.order_by(
#                 kierunek_sortowania(Kierowca.imie),
#                 kierunek_sortowania(Kierowca.nazwisko)
#             )
#         else:
#             # Mapowanie `friendly_name` na rzeczywiste kolumny `Pojazd`
#             sort_column_name = None
#             for column_name, column_info in Pojazd.COLUMN_NAME_MAP.items():
#                 if column_info['friendly_name'] == sort_by:
#                     sort_column_name = column_name
#                     break
#
#             # Pobieramy kolumnę modelu na podstawie `sort_column_name`, lub domyślnie `idPojazd`
#             sort_column = getattr(Pojazd, sort_column_name, Pojazd.idPojazd)
#             query = query.order_by(kierunek_sortowania(sort_column))
#
#         # Pobranie wyników
#         pojazdy = query.all()
#
#         # Konwersja wyników do formatu JSON
#         wynik = [Pojazd.serialize(pojazd) for pojazd in pojazdy]
#
#         return jsonify(wynik), 200
#
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

@pojazd_bp.route('/pojazd/show', methods=['GET'])
def pobierz_i_sortuj_pojazdy():
    combined_params = request.args.to_dict()

    # Pobierz parametry zapytania
    filter_by = request.args.get('filter_by', '{}')  # Filtrowanie - jest to słownik
    sort_by = request.args.get('sort_by', 'ID pojazdu')  # Sortowanie po `idPojazd` domyślnie
    order = request.args.get('order', 'asc')  # Domyślny kierunek sortowania to `asc`

    # Printy do wyświetlania wartości parametrów
    print(f"api: pobierz i sortuj pojazdy")
    print(f"Filter by: {filter_by}")
    print(f"Sort by: {sort_by}")
    print(f"Order: {order}")

    # Ustal kierunek sortowania
    kierunek_sortowania = asc if order == 'asc' else desc

    try:
        # Budowanie podstawowego zapytania
        query = db.session.query(Pojazd)

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

                    # Obsługa "Dane Kierowcy" (przekształcenie danych kierowcy do filtrów po ID)
                    if friendly_name == 'Dane Kierowcy':
                        print("Handling 'Dane Kierowcy' filter")

                        # Wyciągamy tylko ID kierowców z listy
                        kierowcy_ids = [kierowca['ID'] for kierowca in values]
                        print(f"Kierowcy IDs: {kierowcy_ids}")

                        # Filtrujemy po idKierowcy w tabeli Pojazd
                        query = query.filter(Pojazd.idKierowca.in_(kierowcy_ids))
                        print("Filter applied for 'Dane Kierowcy' by IDs.")

                    else:
                        # Mapowanie na inne kolumny
                        print(f"Searching for column corresponding to {friendly_name}")
                        for column, column_info in Pojazd.COLUMN_NAME_MAP.items():
                            if column_info['friendly_name'] == friendly_name:
                                column_name = column
                                print(f"Found column: {column_name}")
                                break

                        if column_name:
                            column_to_filter = getattr(Pojazd, column_name)
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
        if sort_by == "Dane kierowcy":
            # Sortowanie po `imie` i `nazwisko` w tabeli Kierowca
            query = query.join(Kierowca, Pojazd.idKierowca == Kierowca.idKierowca)
            query = query.order_by(
                kierunek_sortowania(Kierowca.imie),
                kierunek_sortowania(Kierowca.nazwisko)
            )
        else:
            # Mapowanie `friendly_name` na rzeczywiste kolumny `Pojazd`
            sort_column_name = None
            for column_name, column_info in Pojazd.COLUMN_NAME_MAP.items():
                if column_info['friendly_name'] == sort_by:
                    sort_column_name = column_name
                    break

            # Pobieramy kolumnę modelu na podstawie `sort_column_name`, lub domyślnie `idPojazd`
            sort_column = getattr(Pojazd, sort_column_name, Pojazd.idPojazd)
            query = query.order_by(kierunek_sortowania(sort_column))

        # Pobranie wyników
        pojazdy = query.all()

        # Konwersja wyników do formatu JSON
        wynik = [Pojazd.serialize(pojazd) for pojazd in pojazdy]

        return jsonify(wynik), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Dodawanie nowego pojazdu
@pojazd_bp.route('/pojazd/add', methods=['POST'])
def dodaj_pojazd():
    data = request.get_json()

    # Deserializacja danych wejściowych
    deserialized_data = Pojazd.deserialize(data)
    # Tworzenie obiektu Kierowca na podstawie deserializowanych danych
    nowy_pojazd = Pojazd(**deserialized_data)
    try:
        db.session.add(nowy_pojazd)
        db.session.commit()
        return jsonify({'message': 'Pojazd dodany pomyślnie'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# Usuwanie pojazdu
@pojazd_bp.route('/pojazd/delete/<int:id>', methods=['DELETE'])
def usun_pojazd(id):
    try:
        pojazd = Pojazd.query.get(id)
        if pojazd is None:
            return jsonify({'message': 'Pojazd nie znaleziony'}), 404
        db.session.delete(pojazd)
        db.session.commit()
        return jsonify({'message': 'Pojazd usunięty pomyślnie'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# Edytowanie danych pojazdu
@pojazd_bp.route('/pojazd/edit/<int:id>', methods=['PUT'])
def edytuj_pojazd(id):
    data = request.get_json()

    # Deserializacja danych wejściowych
    deserialized_data = Pojazd.deserialize(data)
    print(f"Deserialized data: {deserialized_data}")

    try:
        pojazd = Pojazd.query.get(id)
        if pojazd is None:
            return jsonify({'message': 'Pojazd nie znaleziony'}), 404

        pojazd.idKierowca = deserialized_data.get('idKierowca', pojazd.idKierowca)
        pojazd.typPojazdu = deserialized_data.get('typPojazdu', pojazd.typPojazdu)
        pojazd.marka = deserialized_data.get('marka', pojazd.marka)
        pojazd.model = deserialized_data.get('model', pojazd.model)
        pojazd.nrRejestracyjny = deserialized_data.get('nrRejestracyjny', pojazd.nrRejestracyjny)
        pojazd.dodatkoweInf = deserialized_data.get('dodatkoweInf', pojazd.dodatkoweInf)

        db.session.commit()

        return jsonify({'message': 'Dane pojazdu zaktualizowane pomyślnie'}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Błąd: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': 'Wystąpił problem z aktualizacją danych. Spróbuj ponownie później.'}), 500


@pojazd_bp.route('/pojazd/validate', methods=['POST'])
def validate_pojazd():
    data = request.get_json()
    print(f"Data in validation api: {data}")
    validation_result = Pojazd.validate_data(data)
    if validation_result:
        return jsonify(validation_result[0]), validation_result[1]

    return jsonify({'message': 'Dane są poprawne'}), 200
