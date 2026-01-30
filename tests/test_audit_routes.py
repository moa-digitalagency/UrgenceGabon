import os
import sys

# Set environment variables BEFORE importing app
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['SESSION_SECRET'] = 'test-secret'
os.environ['FLASK_ENV'] = 'testing'

# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from flask import url_for
from app import create_app
from extensions import db
from models.admin import Admin
from models.pharmacy import Pharmacy
from models.submission import Suggestion, LocationSubmission, InfoSubmission, PharmacyProposal
from models.emergency_contact import EmergencyContact
from models.site_settings import PopupMessage, SiteSettings
from models.advertisement import Advertisement

@pytest.fixture
def app():
    app = create_app()
    app.config['WTF_CSRF_ENABLED'] = False

    with app.app_context():
        db.create_all()

        # Create Admin
        admin = Admin(username='admin')
        admin.set_password('password')
        db.session.add(admin)

        # Create Dummy Data
        pharmacy = Pharmacy(
            id=1, code='PH001', nom='Pharmacie Test', ville='Libreville',
            latitude=0.0, longitude=0.0
        )
        db.session.add(pharmacy)

        suggestion = Suggestion(id=1, category='test', subject='test', message='test')
        db.session.add(suggestion)

        contact = EmergencyContact(id=1, label='Police', phone_numbers='177', is_active=True, service_type='police')
        db.session.add(contact)

        ad = Advertisement(id=1, title='Ad Test', image_filename='test.jpg')
        db.session.add(ad)

        popup = PopupMessage(id=1, title='Popup Test', description='Hello')
        db.session.add(popup)

        loc_sub = LocationSubmission(id=1, pharmacy_id=1, latitude=1.0, longitude=1.0)
        db.session.add(loc_sub)

        info_sub = InfoSubmission(id=1, pharmacy_id=1, field_name='nom', current_value='Old', proposed_value='New')
        db.session.add(info_sub)

        prop = PharmacyProposal(id=1, nom='New Pharma', ville='LBV')
        db.session.add(prop)

        # Enable PWA for manifest test
        SiteSettings.set('pwa_enabled', 'true')

        db.session.commit()

    yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def admin_client(client, app):
    # Log in
    client.post('/admin/login', data={'username': 'admin', 'password': 'password'}, follow_redirects=True)
    return client

def test_public_routes(client):
    """Test public routes return 200 OK."""
    routes = [
        '/',
        '/sitemap.xml',
        '/robots.txt',
        '/manifest.json',
        '/api/pharmacies',
        '/api/popups',
        '/api/ads/settings',
        '/api/emergency-contacts'
    ]
    for route in routes:
        response = client.get(route, follow_redirects=True)
        assert response.status_code == 200, f"Route {route} failed with {response.status_code}"

def test_admin_routes(admin_client):
    """Test admin routes return 200 OK when logged in."""
    routes = [
        '/admin/', # Dashboard
        # '/admin/pharmacies', # This might not be a separate route if it's all in dashboard?
        # Let's check other known routes
        '/admin/emergency-contacts',
        '/admin/popups',
        '/admin/ads',
        '/admin/ads/settings',
        '/admin/settings',
        '/admin/logs',
        '/admin/pharmacy/add',
    ]

    for route in routes:
        response = admin_client.get(route, follow_redirects=True)
        assert response.status_code == 200, f"Admin route {route} failed with {response.status_code}"

def test_admin_dynamic_routes(admin_client):
    """Test admin routes with parameters."""
    routes = [
        '/admin/pharmacy/1/edit',
        '/admin/emergency-contact/1/edit',
        '/admin/popup/1/edit',
        '/admin/ad/1/edit',
    ]
    for route in routes:
        response = admin_client.get(route, follow_redirects=True)
        assert response.status_code == 200, f"Dynamic admin route {route} failed with {response.status_code}"

def test_crawl_all_get_routes(app, admin_client):
    """Crawl ALL GET routes defined in the app to find 500 errors."""

    defaults = {
        'id': 1,
        'filename': 'favicon.svg',
        'path': 'css/style.css',
        'action_type': 'call'
    }

    ignored_endpoints = [
        'static',
        'public.track_action',
        'public.record_view',
        'public.submit_location',
        'public.submit_info',
        'public.submit_suggestion',
        'public.submit_pharmacy_proposal',
        'public.record_ad_view',
        'public.record_ad_click',
        'public.track_interaction',
        'admin.admin_logout',
        'admin.admin_delete_pharmacy',
        'admin.delete_emergency_contact',
        'admin.delete_popup',
        'admin.delete_ad',
        'admin.approve_location_submission',
        'admin.reject_location_submission',
        'admin.approve_info_submission',
        'admin.reject_info_submission',
        'admin.approve_proposal',
        'admin.reject_proposal',
        'admin.mark_suggestion_read',
        'admin.archive_suggestion',
        'admin.toggle_verified',
        'admin.validate_location',
        'admin.invalidate_location',
        'admin.set_garde',
        'admin.toggle_active_popup',
        'admin.toggle_active_ad',
        'admin.toggle_active_contact'
    ]

    # Collect URLs first
    urls_to_test = []
    with app.test_request_context():
        for rule in app.url_map.iter_rules():
            if 'GET' not in rule.methods:
                continue

            endpoint = rule.endpoint
            if endpoint in ignored_endpoints:
                continue

            params = {}
            for arg in rule.arguments:
                if arg in defaults:
                    params[arg] = defaults[arg]
                else:
                    params[arg] = 1

            try:
                url = url_for(endpoint, **params)
                if '/logout' in url:
                    continue
                if endpoint == 'static':
                    continue
                urls_to_test.append((endpoint, url))
            except Exception:
                continue

    # Now test them outside the context to avoid conflict
    for endpoint, url in urls_to_test:
        response = admin_client.get(url, follow_redirects=True)
        assert response.status_code in [200, 302], f"Endpoint {endpoint} ({url}) failed with {response.status_code}"
