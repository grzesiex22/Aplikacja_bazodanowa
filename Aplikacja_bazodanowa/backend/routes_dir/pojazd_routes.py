from flask import Blueprint, jsonify, request
from Aplikacja_bazodanowa.backend.database import db
from Aplikacja_bazodanowa.backend.models import Kierowca, Pojazd

pojazd_bp = Blueprint('kierowca_api', __name__)

# Pobierz wszystkie pojazdy
@pojazd_bp.route('/api/pojazdy', methods=['GET'])
def get_pojazdy():
    pojazdy = Pojazd.query.all()
    return jsonify([{"id": p.idPojazd, "idKierowca": p.idKierowca, "typPojazdu": p.typPojazdu,
                     "marka": p.marka, "model": p.model_kierowca, "nrRejestracyjny": p.nrRejestracyjny,
                     "dodatkoweInf": p.dodatkoweInf} for p in pojazdy])

