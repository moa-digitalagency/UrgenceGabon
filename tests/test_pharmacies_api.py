
import os
import pytest

# Set env vars BEFORE importing app
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['SESSION_SECRET'] = 'test'
os.environ['FLASK_ENV'] = 'testing'

from app import create_app
from extensions import db
from models.pharmacy import Pharmacy
from datetime import datetime, timedelta, timezone

@pytest.fixture
def app():
    # create_app() is called when importing app, but we want a fresh one for testing
    # configured for in-memory DB (which is what we set in env vars above)
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    with app.app_context():
        db.create_all()

        # Create test data
        p1 = Pharmacy(
            code="P1", nom="Pharmacie Alpha", ville="Libreville", quartier="Centre",
            is_garde=True, garde_end_date=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=1),
            latitude=0.1, longitude=0.1
        )
        p2 = Pharmacy(
            code="P2", nom="Pharmacie Beta", ville="Port-Gentil", quartier="Plage",
            is_garde=False,
            latitude=0.2, longitude=0.2
        )
        db.session.add_all([p1, p2])
        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_get_pharmacies(client):
    response = client.get('/api/pharmacies')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2

    names = sorted([p['nom'] for p in data])
    assert names == ["Pharmacie Alpha", "Pharmacie Beta"]

    # Check keys match expected structure
    p = data[0]
    expected_keys = {
        'id', 'code', 'nom', 'ville', 'quartier', 'telephone', 'bp',
        'horaires', 'services', 'proprietaire', 'type_etablissement',
        'categorie_emplacement', 'is_garde', 'lat', 'lng',
        'location_validated', 'is_verified', 'garde_end_date'
    }
    assert set(p.keys()) == expected_keys

def test_get_pharmacies_filter_city(client):
    response = client.get('/api/pharmacies?ville=Libreville')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]['nom'] == "Pharmacie Alpha"

def test_get_pharmacies_filter_search(client):
    response = client.get('/api/pharmacies?search=Beta')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]['nom'] == "Pharmacie Beta"

def test_get_pharmacies_filter_garde(client):
    response = client.get('/api/pharmacies?garde=true')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]['nom'] == "Pharmacie Alpha"
    assert data[0]['is_garde'] == True
