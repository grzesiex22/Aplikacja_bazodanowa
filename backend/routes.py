from flask import Blueprint

from Aplikacja_bazodanowa.backend.routes_dir.pojazd_routes2 import pojazd_bp
# from routes_dir.pojazd_routes import pojazd_bp_patryk
from Aplikacja_bazodanowa.backend.routes_dir.kierowca_routes import kierowca_bp
from Aplikacja_bazodanowa.backend.routes_dir.typSerwisu_routes import typserwis_bp
from Aplikacja_bazodanowa.backend.routes_dir.czesc_routes import czesc_bp
from Aplikacja_bazodanowa.backend.routes_dir.serwis_routes2 import serwis_bp
from Aplikacja_bazodanowa.backend.routes_dir.app_routes import app_bp
from Aplikacja_bazodanowa.backend.routes_dir.wyposazenie_pojazdu_routes import wyposazenie_bp

bp = Blueprint('api', __name__)

# Rejestracja blueprintów
bp.register_blueprint(kierowca_bp)
bp.register_blueprint(pojazd_bp)
# bp.register_blueprint(pojazd_bp_patryk)
bp.register_blueprint(typserwis_bp)
bp.register_blueprint(czesc_bp)
bp.register_blueprint(serwis_bp)
bp.register_blueprint(wyposazenie_bp)
bp.register_blueprint(app_bp)

