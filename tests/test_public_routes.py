import os
import sys
import pytest

# Add root directory to path to import app and init_db
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set env vars BEFORE importing app
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['SESSION_SECRET'] = 'test'
os.environ['FLASK_ENV'] = 'testing'
os.environ['USE_HTTPS'] = 'false'

from app import create_app
from extensions import db
from models.site_settings import SiteSettings

@pytest.fixture
def app():
    # Environment variables are already set above, but create_app uses them.
    # We can rely on the import time check passing, but we want a fresh app for testing.
    # However, create_app() was called at import time for the global 'app' variable in app.py.
    # We will call it again here for our test fixture.

    app = create_app()
    app.config['TESTING'] = True

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_index_page_settings(app, client):
    """Test that the index page correctly renders site settings."""
    with app.app_context():
        # Setup settings
        s1 = SiteSettings(key='site_name', value='Test Pharmacy Site')
        # We need pwa_enabled=true to see the logo in the PWA modal, OR just check favicon
        s2 = SiteSettings(key='site_logo_filename', value='logo.png')
        s3 = SiteSettings(key='header_code', value='<meta name="custom" content="header">')
        s5 = SiteSettings(key='site_favicon_filename', value='favicon.png')
        s6 = SiteSettings(key='pwa_enabled', value='true')

        db.session.add_all([s1, s2, s3, s5, s6])
        db.session.commit()

    response = client.get('/')
    assert response.status_code == 200

    # Check site name in title or content (depends on template)
    assert b'Test Pharmacy Site' in response.data

    # Check favicon URL
    assert b'/static/uploads/settings/favicon.png' in response.data

    # Check logo URL (now visible because PWA enabled)
    assert b'/static/uploads/settings/logo.png' in response.data

    # Check header code
    assert b'<meta name="custom" content="header">' in response.data

def test_manifest_json(app, client):
    """Test that manifest.json correctly uses site settings."""
    with app.app_context():
        # Setup settings
        s1 = SiteSettings(key='pwa_enabled', value='true')
        s2 = SiteSettings(key='site_name', value='PWA App')
        s3 = SiteSettings(key='site_logo_filename', value='icon.png')
        db.session.add_all([s1, s2, s3])
        db.session.commit()

    response = client.get('/manifest.json')
    assert response.status_code == 200
    data = response.get_json()

    assert data['name'] == 'PWA App'

    # Check icons
    icons = data['icons']
    assert len(icons) > 0
    found_icon = False
    for icon in icons:
        if '/static/uploads/settings/icon.png' in icon['src']:
            found_icon = True
            break
    assert found_icon

def test_manifest_disabled(app, client):
    """Test manifest returns 404 when disabled."""
    with app.app_context():
        # Setup settings
        s1 = SiteSettings(key='pwa_enabled', value='false')
        db.session.add(s1)
        db.session.commit()

    response = client.get('/manifest.json')
    assert response.status_code == 404
