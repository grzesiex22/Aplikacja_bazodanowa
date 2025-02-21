from flask import Blueprint, jsonify, request

from Aplikacja_bazodanowa.backend.models import Kierowca, Pojazd, Czesc, SerwisWidok, Serwis, WyposazeniePojazdu

app_bp = Blueprint('app', __name__)


@app_bp.route("/", methods=['GET'])
def index():
    return "Flask server is running!"


@app_bp.route('/api/columns/<table_name>', methods=['GET'])
def get_columns(table_name):
    # Pobierz model na podstawie nazwy tabeli
    print(table_name)
    if table_name == "kierowca":
        model_class = Kierowca
    elif table_name == "pojazd":
        model_class = Pojazd
    elif table_name == "czesc":
        model_class = Czesc
    elif table_name == "serwiswidok":
        model_class = SerwisWidok
    elif table_name == "serwis":
        model_class = Serwis
    elif table_name == "WyposazeniePojazdu":
        model_class = WyposazeniePojazdu
    else:
        return jsonify({"error": "Nieznana tabela"}), 400

    # Uzyskaj listę kolumn i ich typów z metody get_columns_info
    columns = model_class.get_columns_info()
    print(f"Columns: {columns}")

    # Zwrócenie informacji o kolumnach w formacie JSON
    return jsonify(columns)