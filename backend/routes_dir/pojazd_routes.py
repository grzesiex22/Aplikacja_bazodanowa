from flask import Blueprint, request, jsonify
from Aplikacja_bazodanowa.backend.database import db
from Aplikacja_bazodanowa.backend.models import Pojazd, Kierowca
from Aplikacja_bazodanowa.backend.routes_dir.app_routes import get_columns
import re
import traceback

# Blueprint dla pojazdów
pojazd_bp_patryk = Blueprint('pojazd', __name__)


@pojazd_bp_patryk.route('/pojazd/<int:id>', methods=['GET'])
def pobierz_pojazd(id):
    try:
        pojazd = Pojazd.query.get(id)
        if pojazd is None:
            return jsonify({'message': 'Pojazd nie znaleziony'}), 404

        # Pobranie danych kierowcy na podstawie idKierowca
        kierowca = Kierowca.query.get(pojazd.idKierowca) if pojazd.idKierowca else None
        kierowca_imie_nazwisko = f"{kierowca.imie} {kierowca.nazwisko}" if kierowca else "Brak kierowcy"

        return jsonify({
            'id': pojazd.idPojazd,
            'idKierowca': kierowca_imie_nazwisko,  # Wyświetlamy imię i nazwisko kierowcy
            'typPojazdu': pojazd.typPojazdu,
            'marka': pojazd.marka,
            'model': pojazd.model,
            'nrRejestracyjny': pojazd.nrRejestracyjny,
            'dodatkoweInf': pojazd.dodatkoweInf
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


############ http://127.0.0.1:5000/pojazdy?typPojazdu=Ciągnik ############# (wyświetli tylko ciągniki)
@pojazd_bp_patryk.route('/pojazdy', methods=['GET'])
def pobierz_pojazdy():
    # Pobieramy wszystkie parametry z zapytania
    query_params = request.args.to_dict()

    try:
        # Rozpoczynamy zapytanie do bazy danych
        pojazdy_query = Pojazd.query

        # Dodajemy filtry dla każdego parametru, który istnieje w zapytaniu
        for param, value in query_params.items():
            if hasattr(Pojazd, param):  # Sprawdzamy, czy parametr jest kolumną w tabeli Pojazd
                pojazdy_query = pojazdy_query.filter(getattr(Pojazd, param) == value)

        # Pobieramy pojazdy na podstawie zastosowanych filtrów
        pojazdy = pojazdy_query.all()

        wynik = []
        for pojazd in pojazdy:
            # Pobranie danych kierowcy na podstawie idKierowca
            kierowca = Kierowca.query.get(pojazd.idKierowca) if pojazd.idKierowca else None
            kierowca_imie_nazwisko = f"{kierowca.imie} {kierowca.nazwisko}" if kierowca else "Brak kierowcy"

            wynik.append({
                'id': pojazd.idPojazd,
                'idKierowca': kierowca_imie_nazwisko,
                'typPojazdu': pojazd.typPojazdu,
                'marka': pojazd.marka,
                'model': pojazd.model,
                'nrRejestracyjny': pojazd.nrRejestracyjny,
                'dodatkoweInf': pojazd.dodatkoweInf
            })

        return jsonify(wynik), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500



# Dodawanie nowego pojazdu
@pojazd_bp_patryk.route('/pojazd', methods=['POST'])
def dodaj_pojazd():
    data = request.get_json()
    try:
        # Walidacja danych wejściowych
        if 'typPojazdu' in data and data['typPojazdu'] not in ['Ciągnik', 'Naczepa']:
            return jsonify({'message': 'Typ pojazdu musi być "Ciągnik" lub "Naczepa"'}), 400
        if 'marka' in data and not isinstance(data['marka'], str):
            return jsonify({'message': 'Marka musi być ciągiem znaków'}), 400
        if 'model' in data and not isinstance(data['model'], str):
            return jsonify({'message': 'Model musi być ciągiem znaków'}), 400
        if 'nrRejestracyjny' in data and not re.match(r'^[A-Z0-9]{1,8}$', data['nrRejestracyjny']):
            return jsonify({'message': 'Numer rejestracyjny musi składać się z maksymalnie 8 znaków alfanumerycznych'}), 400

        nowy_pojazd = Pojazd(
            idKierowca=data.get('idKierowca'),
            typPojazdu=data['typPojazdu'],
            marka=data['marka'],
            model=data['model'],
            nrRejestracyjny=data['nrRejestracyjny'],
            dodatkoweInf=data.get('dodatkoweInf')
        )
        db.session.add(nowy_pojazd)
        db.session.commit()
        return jsonify({'message': 'Pojazd dodany pomyślnie'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# Usuwanie pojazdu
@pojazd_bp_patryk.route('/pojazd/<int:id>', methods=['DELETE'])
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
@pojazd_bp_patryk.route('/pojazd/<int:id>', methods=['PUT'])
def edytuj_pojazd(id):
    data = request.get_json()
    try:
        pojazd = Pojazd.query.get(id)
        if pojazd is None:
            return jsonify({'message': 'Pojazd nie znaleziony'}), 404

        # Walidacja danych wejściowych
        if 'typPojazdu' in data and data['typPojazdu'] not in ['Ciągnik', 'Naczepa']:
            return jsonify({'message': 'Typ pojazdu musi być "Ciągnik" lub "Naczepa"'}), 400
        if 'marka' in data and not isinstance(data['marka'], str):
            return jsonify({'message': 'Marka musi być ciągiem znaków'}), 400
        if 'model' in data and not isinstance(data['model'], str):
            return jsonify({'message': 'Model musi być ciągiem znaków'}), 400
        if 'nrRejestracyjny' in data and not re.match(r'^[A-Z0-9]{1,8}$', data['nrRejestracyjny']):
            return jsonify({'message': 'Numer rejestracyjny musi składać się z maksymalnie 8 znaków alfanumerycznych'}), 400

        pojazd.idKierowca = data.get('idKierowca', pojazd.idKierowca)
        pojazd.typPojazdu = data.get('typPojazdu', pojazd.typPojazdu)
        pojazd.marka = data.get('marka', pojazd.marka)
        pojazd.model = data.get('model', pojazd.model)
        pojazd.nrRejestracyjny = data.get('nrRejestracyjny', pojazd.nrRejestracyjny)
        pojazd.dodatkoweInf = data.get('dodatkoweInf', pojazd.dodatkoweInf)
        db.session.commit()

        return jsonify({'message': 'Dane pojazdu zaktualizowane pomyślnie'}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Błąd: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': 'Wystąpił problem z aktualizacją danych. Spróbuj ponownie później.'}), 500
