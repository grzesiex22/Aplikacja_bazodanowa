from flask import Blueprint, request, jsonify
from Aplikacja_bazodanowa.backend.database import db
from Aplikacja_bazodanowa.backend.models import Serwis, Pojazd, TypSerwisu
from datetime import datetime
import re

# Blueprint dla serwisów
serwis_bp = Blueprint('serwis', __name__)

# Pobieranie wszystkich serwisów z możliwością filtrowania
@serwis_bp.route('/serwis', methods=['GET'])
def pobierz_serwisy():
    try:
        # Pobieranie parametrów z zapytania (query params)
        id_pojazd = request.args.get('idPojazd', None)
        id_typ_serwisu = request.args.get('idTypSerwisu', None)
        data = request.args.get('data', None)
        cena_czesci_netto_min = request.args.get('cenaCzesciNettoMin', None)
        cena_czesci_netto_max = request.args.get('cenaCzesciNettoMax', None)
        robocizna_min = request.args.get('robociznaMin', None)
        robocizna_max = request.args.get('robociznaMax', None)
        koszt_calkowity_netto_min = request.args.get('kosztCalkowityNettoMin', None)
        koszt_calkowity_netto_max = request.args.get('kosztCalkowityNettoMax', None)
        przebieg_min = request.args.get('przebiegMin', None)
        przebieg_max = request.args.get('przebiegMax', None)
        info_dodatkowe = request.args.get('infoDodatkowe', '').strip()

        # Tworzenie zapytania bazowego
        query = Serwis.query

        # Filtrowanie po dostępnych parametrach
        if id_pojazd:
            query = query.filter(Serwis.idPojazd == int(id_pojazd))
        if id_typ_serwisu:
            query = query.filter(Serwis.idTypSerwisu == int(id_typ_serwisu))
        if data:
            query = query.filter(Serwis.data == data)
        if cena_czesci_netto_min:
            query = query.filter(Serwis.cenaCzesciNetto >= int(cena_czesci_netto_min))
        if cena_czesci_netto_max:
            query = query.filter(Serwis.cenaCzesciNetto <= int(cena_czesci_netto_max))
        if robocizna_min:
            query = query.filter(Serwis.robocizna >= int(robocizna_min))
        if robocizna_max:
            query = query.filter(Serwis.robocizna <= int(robocizna_max))
        if koszt_calkowity_netto_min:
            query = query.filter(Serwis.kosztCalkowityNetto >= int(koszt_calkowity_netto_min))
        if koszt_calkowity_netto_max:
            query = query.filter(Serwis.kosztCalkowityNetto <= int(koszt_calkowity_netto_max))
        if przebieg_min:
            query = query.filter(Serwis.przebieg >= int(przebieg_min))
        if przebieg_max:
            query = query.filter(Serwis.przebieg <= int(przebieg_max))
        if info_dodatkowe:
            query = query.filter(Serwis.infoDodatkowe.ilike(f'%{info_dodatkowe}%'))

        # Pobranie wyników zapytania
        serwisy = query.all()

        wynik = []
        for serwis in serwisy:
            # Pobieranie danych pojazdu na podstawie idPojazd
            pojazd = Pojazd.query.get(serwis.idPojazd)
            pojazd_info = {
                'marka': pojazd.marka,
                'model': pojazd.model,
                'nrRejestracyjny': pojazd.nrRejestracyjny
            } if pojazd else {}

            # Pobieranie nazwy typu serwisu na podstawie idTypSerwisu
            typ_serwisu = TypSerwisu.query.get(serwis.idTypSerwisu)
            typ_serwisu_nazwa = typ_serwisu.rodzajSerwisu if typ_serwisu else "Brak typu serwisu"

            # Obliczanie kosztu całkowitego netto
            if serwis.kosztCalkowityNetto is None:
                koszt_calkowity_netto = (serwis.cenaCzesciNetto or 0) + (serwis.robocizna or 0)
            else:
                koszt_calkowity_netto = serwis.kosztCalkowityNetto

            wynik.append({
                'idSerwis': serwis.idSerwis,
                'pojazd': pojazd_info,  # Wyświetlamy informacje o pojeździe
                'typSerwisu': typ_serwisu_nazwa,  # Wyświetlamy nazwę typu serwisu
                'data': serwis.data,
                'cenaCzesciNetto': serwis.cenaCzesciNetto,
                'robocizna': serwis.robocizna,
                'kosztCalkowityNetto': koszt_calkowity_netto,
                'przebieg': serwis.przebieg,
                'infoDodatkowe': serwis.infoDodatkowe
            })

        return jsonify(wynik), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Pobieranie pojedynczego serwisu
@serwis_bp.route('/serwis/<int:id>', methods=['GET'])
def pobierz_serwis(id):
    try:
        serwis = Serwis.query.get(id)
        if serwis is None:
            return jsonify({'message': 'Serwis nie znaleziony'}), 404

        # Pobieranie danych pojazdu na podstawie idPojazd
        pojazd = Pojazd.query.get(serwis.idPojazd)
        pojazd_info = {
            'marka': pojazd.marka,
            'model': pojazd.model,
            'nrRejestracyjny': pojazd.nrRejestracyjny
        } if pojazd else {}

        # Pobieranie nazwy typu serwisu na podstawie idTypSerwisu
        typ_serwisu = TypSerwisu.query.get(serwis.idTypSerwisu)
        typ_serwisu_nazwa = typ_serwisu.rodzajSerwisu if typ_serwisu else "Brak typu serwisu"

        # Obliczanie kosztu całkowitego netto
        if serwis.kosztCalkowityNetto is None:
            koszt_calkowity_netto = (serwis.cenaCzesciNetto or 0) + (serwis.robocizna or 0)
        else:
            koszt_calkowity_netto = serwis.kosztCalkowityNetto

        return jsonify({
            'idSerwis': serwis.idSerwis,
            'pojazd': pojazd_info,  # Wyświetlamy informacje o pojeździe
            'typSerwisu': typ_serwisu_nazwa,  # Wyświetlamy nazwę typu serwisu
            'data': serwis.data,
            'cenaCzesciNetto': serwis.cenaCzesciNetto,
            'robocizna': serwis.robocizna,
            'kosztCalkowityNetto': koszt_calkowity_netto,
            'przebieg': serwis.przebieg,
            'infoDodatkowe': serwis.infoDodatkowe
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Funkcja walidacji daty (format: YYYY-MM-DD)
def waliduj_date(data_str):
    try:
        datetime.strptime(data_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


# Funkcja walidacji liczby (sprawdzamy, czy dane są liczbą i są nieujemne)
def waliduj_liczbe(value):
    return isinstance(value, int) and value >= 0


# Dodawanie nowego serwisu
@serwis_bp.route('/serwis', methods=['POST'])
def dodaj_serwis():
    data = request.get_json()
    try:
        # Walidacja wymaganych danych zgodnie z modelem Serwis
        if 'idPojazd' not in data or not isinstance(data['idPojazd'], int):
            return jsonify({'error': 'Brak lub nieprawidłowy idPojazd (musi być liczbą całkowitą)'}), 400
        if 'idTypSerwisu' not in data or not isinstance(data['idTypSerwisu'], int):
            return jsonify({'error': 'Brak lub nieprawidłowy idTypSerwisu (musi być liczbą całkowitą)'}), 400
        if 'data' not in data or not waliduj_date(data['data']):
            return jsonify({'error': 'Brak lub nieprawidłowy format daty (wymagany format YYYY-MM-DD)'}), 400

        # Walidacja opcjonalnych danych
        cena_czesci_netto = data.get('cenaCzesciNetto')
        if cena_czesci_netto is not None and not waliduj_liczbe(cena_czesci_netto):
            return jsonify({'error': 'Nieprawidłowa cenaCzesciNetto (musi być liczbą całkowitą)'}), 400

        robocizna = data.get('robocizna')
        if robocizna is not None and not waliduj_liczbe(robocizna):
            return jsonify({'error': 'Nieprawidłowa robocizna (musi być liczbą całkowitą)'}), 400

        przebieg = data.get('przebieg')
        if przebieg is not None and not waliduj_liczbe(przebieg):
            return jsonify({'error': 'Nieprawidłowy przebieg (musi być liczbą całkowitą)'}), 400

        info_dodatkowe = data.get('infoDodatkowe')
        if info_dodatkowe is not None and not isinstance(info_dodatkowe, str):
            return jsonify({'error': 'Nieprawidłowy format infoDodatkowe (musi być tekstem)'}), 400

        # Automatyczne obliczenie kosztu całkowitego, jeśli jest pusty
        koszt_calkowity_netto = data.get('kosztCalkowityNetto')
        if koszt_calkowity_netto is None:
            koszt_calkowity_netto = (cena_czesci_netto or 0) + (robocizna or 0)
        elif not waliduj_liczbe(koszt_calkowity_netto):
            return jsonify({'error': 'Nieprawidłowy kosztCalkowityNetto (musi być liczbą całkowitą)'}), 400

        # Dodanie nowego serwisu
        nowy_serwis = Serwis(
            idPojazd=data['idPojazd'],
            idTypSerwisu=data['idTypSerwisu'],
            data=data['data'],
            cenaCzesciNetto=cena_czesci_netto,
            robocizna=robocizna,
            kosztCalkowityNetto=koszt_calkowity_netto,
            przebieg=przebieg,
            infoDodatkowe=info_dodatkowe
        )
        db.session.add(nowy_serwis)
        db.session.commit()
        return jsonify({'message': 'Serwis dodany pomyślnie'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# Edytowanie danych serwisu
@serwis_bp.route('/serwis/<int:id>', methods=['PUT'])
def edytuj_serwis(id):
    data = request.get_json()
    try:
        serwis = Serwis.query.get(id)
        if serwis is None:
            return jsonify({'message': 'Serwis nie znaleziony'}), 404

        # Aktualizacja danych z walidacją
        if 'idPojazd' in data and not isinstance(data['idPojazd'], int):
            return jsonify({'error': 'Nieprawidłowy idPojazd'}), 400
        if 'idTypSerwisu' in data and not isinstance(data['idTypSerwisu'], int):
            return jsonify({'error': 'Nieprawidłowy idTypSerwisu'}), 400
        if 'data' in data and data['data'] and not waliduj_date(data['data']):
            return jsonify({'error': 'Nieprawidłowy format daty'}), 400
        if 'cenaCzesciNetto' in data and not waliduj_liczbe(data['cenaCzesciNetto']):
            return jsonify({'error': 'Nieprawidłowa cenaCzesciNetto'}), 400
        if 'robocizna' in data and not waliduj_liczbe(data['robocizna']):
            return jsonify({'error': 'Nieprawidłowa robocizna'}), 400
        if 'przebieg' in data and not waliduj_liczbe(data['przebieg']):
            return jsonify({'error': 'Nieprawidłowy przebieg'}), 400

        serwis.idPojazd = data.get('idPojazd', serwis.idPojazd)
        serwis.idTypSerwisu = data.get('idTypSerwisu', serwis.idTypSerwisu)
        serwis.data = data.get('data', serwis.data)
        serwis.cenaCzesciNetto = data.get('cenaCzesciNetto', serwis.cenaCzesciNetto)
        serwis.robocizna = data.get('robocizna', serwis.robocizna)

        # Obliczenie kosztu całkowitego
        koszt_calkowity_netto = data.get('kosztCalkowityNetto')
        if koszt_calkowity_netto is None:
            serwis.kosztCalkowityNetto = (serwis.cenaCzesciNetto or 0) + (serwis.robocizna or 0)
        else:
            serwis.kosztCalkowityNetto = koszt_calkowity_netto

        serwis.przebieg = data.get('przebieg', serwis.przebieg)
        serwis.infoDodatkowe = data.get('infoDodatkowe', serwis.infoDodatkowe)

        db.session.commit()
        return jsonify({'message': 'Serwis zaktualizowany pomyślnie'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Usuwanie serwisu
@serwis_bp.route('/serwis/<int:id>', methods=['DELETE'])
def usun_serwis(id):
    try:
        serwis = Serwis.query.get(id)
        if serwis is None:
            return jsonify({'message': 'Serwis nie znaleziony'}), 404
        db.session.delete(serwis)
        db.session.commit()
        return jsonify({'message': 'Serwis usunięty pomyślnie'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
