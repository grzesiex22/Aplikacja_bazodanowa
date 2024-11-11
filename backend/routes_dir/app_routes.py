from flask import Blueprint, jsonify, request

from Aplikacja_bazodanowa.backend.models import Kierowca, Pojazd

app_bp = Blueprint('app', __name__)


@app_bp.route('/api/columns/<table_name>', methods=['GET'])
def get_columns(table_name):
    # Pobierz model na podstawie nazwy tabeli
    print(table_name)
    if table_name == "kierowca":
        model_class = Kierowca
    elif table_name == "pojazd":
        model_class = Pojazd
    else:
        return jsonify({"error": "Nieznana tabela"}), 400

    # Uzyskaj listę kolumn i ich typów z metody get_columns_info
    columns = model_class.get_columns_info()
    print(f"Columns: {columns}")

    # Zwrócenie informacji o kolumnach w formacie JSON
    return jsonify(columns)