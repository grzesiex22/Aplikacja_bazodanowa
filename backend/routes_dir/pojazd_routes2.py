from flask import Blueprint, request, jsonify
from Aplikacja_bazodanowa.backend.database import db
from Aplikacja_bazodanowa.backend.models import Pojazd, Kierowca, TypPojazdu
import re
import traceback
from sqlalchemy import asc, desc


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


############ http://127.0.0.1:5000/pojazdy?typPojazdu=Ciągnik ############# (wyświetli tylko ciągniki)
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


from sqlalchemy.orm import aliased

@pojazd_bp.route('/pojazd/show', methods=['GET'])
def pobierz_i_sortuj_pojazdy():
    # Pobierz parametry zapytania jako słownik
    combined_params = request.args.to_dict()

    typ_pojazdu = request.args.get('Typ pojazdu')
    sort_by = combined_params.get('sort_by', 'ID pojazdu')  # Domyślnie sortowanie po `idPojazd`
    order = combined_params.get('order', 'asc')  # Domyślny kierunek sortowania to `asc`

    # Ustal kierunek sortowania
    kierunek_sortowania = asc if order == 'asc' else desc

    try:
        # Budowanie podstawowego zapytania
        query = db.session.query(Pojazd)

        # Filtrowanie po `typPojazdu`, jeśli podano
        if typ_pojazdu:
            query = query.filter(Pojazd.typPojazdu == typ_pojazdu)

        # Dynamiczne filtrowanie na podstawie przekazanych parametrów
        for param, value in combined_params.items():
            if param in ['marka', 'model', 'nrRejestracyjny', 'dodatkoweInf']:  # Możesz dodać inne parametry do listy
                query = query.filter(getattr(Pojazd, param).ilike(f"%{value}%"))

            # Filtrowanie po `imie` i `nazwisko` jeśli podano
            if param == 'imie' or param == 'nazwisko':
                query = query.join(Kierowca, Pojazd.idKierowca == Kierowca.idKierowca)
                query = query.filter(getattr(Kierowca, param).ilike(f"%{value}%"))

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

# @pojazd_bp.route('/pojazd/show', methods=['GET'])
# def pobierz_i_sortuj_pojazdy():
#     # Pobierz parametry zapytania
#     typ_pojazdu = request.args.get('Typ pojazdu')  # Filtrowanie po `typPojazdu`
#     sort_by = request.args.get('sort_by', 'ID pojazdu')  # Sortowanie po `idPojazd` domyślnie
#     order = request.args.get('order', 'asc')  # Domyślny kierunek sortowania to `asc`
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
