from flask import Blueprint, request, jsonify
from Aplikacja_bazodanowa.backend.database import db
from Aplikacja_bazodanowa.backend.models import Serwis
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
            wynik.append({
                'idSerwis': serwis.idSerwis,
                'idPojazd': serwis.idPojazd,
                'idTypSerwisu': serwis.idTypSerwisu,
                'data': serwis.data,
                'cenaCzesciNetto': serwis.cenaCzesciNetto,
                'robocizna': serwis.robocizna,
                'kosztCalkowityNetto': serwis.kosztCalkowityNetto,
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
        return jsonify({
            'idSerwis': serwis.idSerwis,
            'idPojazd': serwis.idPojazd,
            'idTypSerwisu': serwis.idTypSerwisu,
            'data': serwis.data,
            'cenaCzesciNetto': serwis.cenaCzesciNetto,
            'robocizna': serwis.robocizna,
            'kosztCalkowityNetto': serwis.kosztCalkowityNetto,
            'przebieg': serwis.przebieg,
            'infoDodatkowe': serwis.infoDodatkowe
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Dodawanie nowego serwisu
@serwis_bp.route('/serwis', methods=['POST'])
def dodaj_serwis():
    data = request.get_json()
    try:
        nowy_serwis = Serwis(
            idPojazd=data['idPojazd'],
            idTypSerwisu=data['idTypSerwisu'],
            data=data['data'],
            cenaCzesciNetto=data.get('cenaCzesciNetto'),
            robocizna=data.get('robocizna'),
            kosztCalkowityNetto=data['kosztCalkowityNetto'],
            przebieg=data.get('przebieg'),
            infoDodatkowe=data.get('infoDodatkowe')
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

        serwis.idPojazd = data.get('idPojazd', serwis.idPojazd)
        serwis.idTypSerwisu = data.get('idTypSerwisu', serwis.idTypSerwisu)
        serwis.data = data.get('data', serwis.data)
        serwis.cenaCzesciNetto = data.get('cenaCzesciNetto', serwis.cenaCzesciNetto)
        serwis.robocizna = data.get('robocizna', serwis.robocizna)
        serwis.kosztCalkowityNetto = data.get('kosztCalkowityNetto', serwis.kosztCalkowityNetto)
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
