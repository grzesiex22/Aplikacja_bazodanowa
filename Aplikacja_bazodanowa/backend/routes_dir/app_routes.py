from flask import Blueprint, jsonify, request
from sqlalchemy import inspect
from Aplikacja_bazodanowa.backend.database import db

app_bp = Blueprint('app', __name__)

@app_bp.route('/api/columns/<table_name>', methods=['GET'])
def get_columns(table_name):
    inspector = inspect(db.engine)
    columns = inspector.get_columns(table_name)
    # Zwracamy tylko nazwy kolumn, które nie są kluczami głównymi
    column_info = [{"name": col['name'], "type": col['type'].__class__.__name__}
                   for col in columns if not col.get('primary_key')]
    return jsonify(column_info)
