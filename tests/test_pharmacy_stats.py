import os
import sys
import pytest

# Add root directory to path to import app and init_db
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set env vars BEFORE importing app
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['SESSION_SECRET'] = 'test'
os.environ['FLASK_ENV'] = 'testing'

from extensions import db
from models.pharmacy import Pharmacy
from services.pharmacy_service import PharmacyService
from app import create_app

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

def test_get_stats(app):
    with app.app_context():
        # Seed Data
        p1 = Pharmacy(code="P1", nom="P1", ville="Libreville", is_garde=True, categorie_emplacement="gare", location_validated=True)
        p2 = Pharmacy(code="P2", nom="P2", ville="Libreville", is_garde=False, categorie_emplacement="standard", location_validated=False)
        p3 = Pharmacy(code="P3", nom="P3", ville="Port-Gentil", is_garde=True, categorie_emplacement="standard", location_validated=True)

        db.session.add_all([p1, p2, p3])
        db.session.commit()

        stats = PharmacyService.get_stats()

        assert stats['total'] == 3
        assert stats['pharmacies_garde'] == 2
        assert stats['pharmacies_gare'] == 1
        assert stats['locations_validated'] == 2
        assert stats['par_ville']['Libreville'] == 2
        assert stats['par_ville']['Port-Gentil'] == 1
