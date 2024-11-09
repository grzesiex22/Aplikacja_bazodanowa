from flask import Blueprint
from routes_dir.kierowca_routes import kierowca_bp

bp = Blueprint('api', __name__)

# Rejestracja blueprintów
bp.register_blueprint(kierowca_bp)
