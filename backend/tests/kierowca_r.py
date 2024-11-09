import pytest
from backend.database import db, create_app
from backend.models import Kierowca, Pojzad

@pytest.fixture
def app():
    app = create_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.engine.execute("PRAGMA foreign_keys=OFF")
        db.drop_all()
        db.engine.execute("PRAGMA foreign_keys=ON")

@pytest.fixture
def client(app):
    return app.test_client()

# Testowanie endpointu do pobierania kierowców
def test_get_kierowcy(client, app):
    with app.app_context():
        kierowca = Kierowca(imie="Jan", nazwisko="Kowalski", nrTel="123456789")
        db.session.add(kierowca)
        db.session.commit()

    response = client.get('/api/kierowcy')
    assert response.status_code == 200
    json_data = response.get_json()
    assert len(json_data) == 1
    assert json_data[0]['imie'] == "Jan"
    assert json_data[0]['nazwisko'] == "Kowalski"

def test_add_kierowca(client):
    new_kierowca = {'imie': 'Anna', 'nazwisko': 'Nowak', 'nrTel': '987654321'}
    response = client.post('/api/kierowcy', json=new_kierowca)

    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data['imie'] == 'Anna'
    assert json_data['nazwisko'] == 'Nowak'

def test_update_kierowca(client, app):
    with app.app_context():
        kierowca = Kierowca(imie="Piotr", nazwisko="Szymczak", nrTel="111222333")
        db.session.add(kierowca)
        db.session.commit()

    updated_data = {'imie': 'Piotr', 'nazwisko': 'Nowak', 'nrTel': '444555666'}
    response = client.put(f'/api/kierowcy/{kierowca.idKierowca}', json=updated_data)

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['imie'] == 'Piotr'
    assert json_data['nazwisko'] == 'Nowak'
    assert json_data['nrTel'] == '444555666'

def test_delete_kierowca(client, app):
    with app.app_context():
        kierowca = Kierowca(imie="Marek", nazwisko="Kowalski", nrTel="555666777")
        db.session.add(kierowca)
        db.session.commit()

    response = client.delete(f'/api/kierowcy/{kierowca.idKierowca}')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['message'] == "Kierowca usunięty pomyślnie"

    with app.app_context():
        kierowca = Kierowca.query.get(kierowca.idKierowca)
        assert kierowca is None
