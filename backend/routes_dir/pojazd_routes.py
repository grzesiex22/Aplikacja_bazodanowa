from flask import Blueprint, jsonify, request
from backend.database import db
from backend.models import Kierowca, Pojzad

pojazd_bp = Blueprint('kierowca_api', __name__)

# Pobierz wszystkie pojazdy
@pojazd_bp.route('/api/pojazdy', methods=['GET'])
def get_pojazdy():
    pojazdy = Pojzad.query.all()
    return jsonify([{"id": p.idPojazd, "idKierowca": p.idKierowca, "typPojazdu": p.typPojazdu,
                     "marka": p.marka, "model": p.model, "nrRejestracyjny": p.nrRejestracyjny,
                     "dodatkoweInf": p.dodatkoweInf} for p in pojazdy])

