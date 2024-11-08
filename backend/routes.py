from flask import Blueprint, jsonify
from models import Kierowca, Pojzad, TypSerwisu, Serwis, Czesc

bp = Blueprint('api', __name__)

@bp.route('/api/kierowcy', methods=['GET'])
def get_kierowcy():
    kierowcy = Kierowca.query.all()
    return jsonify([{"id": k.idKierowca, "imie": k.imie, "nazwisko": k.nazwisko, "nrTel": k.nrTel} for k in kierowcy])

@bp.route('/api/pojazdy', methods=['GET'])
def get_pojazdy():
    pojazdy = Pojzad.query.all()
    return jsonify([{"id": p.idPojazd, "marka": p.marka, "model": p.model} for p in pojazdy])
