import os
import sys
import pytest
import json
from datetime import datetime, timedelta, timezone

# Add root directory to path to import app and init_db
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set env vars BEFORE importing app
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['SESSION_SECRET'] = 'test'
os.environ['FLASK_ENV'] = 'testing'
os.environ['USE_HTTPS'] = 'false'

from app import create_app
from extensions import db, limiter
from models.advertisement import Advertisement, AdSettings

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['RATELIMIT_ENABLED'] = False  # Disable rate limiter for tests
    limiter.enabled = False # Explicitly disable limiter

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_get_random_ad_no_ads(app, client):
    """Test that it returns null when no ads exist."""
    response = client.get('/api/ads/random')
    assert response.status_code == 200
    assert response.get_json() is None

def test_get_random_ad_single_active(app, client):
    """Test that it returns the single active ad."""
    with app.app_context():
        ad = Advertisement(
            title="Test Ad",
            description="Buy this!",
            priority=1,
            is_active=True
        )
        db.session.add(ad)
        db.session.commit()

    response = client.get('/api/ads/random')
    assert response.status_code == 200
    data = response.get_json()
    assert data is not None
    assert data['title'] == "Test Ad"

def test_get_random_ad_respects_dates(app, client):
    """Test that it respects start and end dates."""
    with app.app_context():
        # Future ad (should not show)
        future_ad = Advertisement(
            title="Future Ad",
            start_date=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=1),
            is_active=True
        )
        # Expired ad (should not show)
        expired_ad = Advertisement(
            title="Expired Ad",
            end_date=datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=1),
            is_active=True
        )
        # Active ad
        active_ad = Advertisement(
            title="Active Ad",
            start_date=datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=1),
            end_date=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=1),
            is_active=True
        )
        db.session.add_all([future_ad, expired_ad, active_ad])
        db.session.commit()

    response = client.get('/api/ads/random')
    data = response.get_json()
    assert data is not None
    assert data['title'] == "Active Ad"

def test_get_random_ad_weighted_distribution(app, client):
    """
    Test that higher priority ads are returned more often.
    This is probabilistic, so we use a large sample size and loose bounds.
    """
    with app.app_context():
        # Low priority ad (weight = 1 + 1 = 2)
        low_prio = Advertisement(title="Low", priority=1, is_active=True)
        # High priority ad (weight = 9 + 1 = 10)
        high_prio = Advertisement(title="High", priority=9, is_active=True)
        db.session.add_all([low_prio, high_prio])
        db.session.commit()

    low_count = 0
    high_count = 0
    iterations = 500

    for _ in range(iterations):
        response = client.get('/api/ads/random')
        data = response.get_json()
        if data['title'] == "Low":
            low_count += 1
        else:
            high_count += 1

    # Expected ratio is roughly 1:5 (2 vs 10)
    # So high_count should be significantly higher than low_count
    assert high_count > low_count
    # Check that we got at least some of both (it's random, but 500 trials should hit both)
    assert low_count > 0
    assert high_count > 0
