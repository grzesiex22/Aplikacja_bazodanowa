from flask import Blueprint, request, jsonify
from Aplikacja_bazodanowa.backend.database import db
from Aplikacja_bazodanowa.backend.models import Kierowca
import traceback

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