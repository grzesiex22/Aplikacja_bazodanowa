from flask import Blueprint, jsonify, request
from sqlalchemy import inspect
from Aplikacja_bazodanowa.backend.database import db
from Aplikacja_bazodanowa.backend.models import Kierowca

app_bp = Blueprint('app', __name__)


@app_bp.route('/api/columns/<table_name>', methods=['GET'])
def get_columns(table_name):
    # Pobierz model na podstawie nazwy tabeli
    if table_name == "Kierowca":
        model_class = Kierowca
    else:
        return jsonify({"error": "Nieznana tabela"}), 400

    # Uzyskaj listę kolumn i ich typów
    columns = []
    for column in model_class.__table__.columns:
        column_info = {
            "name": column.name,
            "type": str(column.type),
            "primary_key": column.primary_key,
            "foreign_key": bool(column.foreign_keys)  # True jeśli jest kluczem obcym, False jeśli nie
        }
        columns.append(column_info)

    return jsonify(columns)