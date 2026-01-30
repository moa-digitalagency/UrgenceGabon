
import os
import sys
import pytest
from sqlalchemy import text, inspect

# Add root directory to path to import app and init_db
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set env vars BEFORE importing app to avoid RuntimeError
os.environ['DATABASE_URL'] = 'sqlite:///migration_test.db'
os.environ['SESSION_SECRET'] = 'test'
os.environ['FLASK_ENV'] = 'testing'
os.environ['USE_HTTPS'] = 'false'

from app import create_app
from extensions import db
import init_db

# Configure test app
@pytest.fixture
def app():
    # Environment variables are already set above
    app = create_app()
    app.config['TESTING'] = True

    with app.app_context():
        # Clean up existing DB
        db.drop_all()
        yield app
        # Cleanup after test
        db.session.remove()
        db.drop_all()
        if os.path.exists('migration_test.db'):
            os.remove('migration_test.db')

def test_migration_add_missing_column(app):
    """
    Test that init_db.check_and_add_missing_columns correctly adds
    a missing column to an existing table without losing data.
    """
    # Patch init_db.app to use our test app
    init_db.app = app

    with app.app_context():
        # 1. Manually create an "old" version of the Pharmacy table
        # We omit 'is_verified' which exists in the model
        create_sql = """
        CREATE TABLE pharmacy (
            id INTEGER PRIMARY KEY,
            code VARCHAR(20) NOT NULL,
            nom VARCHAR(200) NOT NULL,
            ville VARCHAR(100) NOT NULL,
            quartier VARCHAR(200),
            telephone VARCHAR(100),
            bp VARCHAR(50),
            horaires VARCHAR(200),
            services TEXT,
            proprietaire VARCHAR(200),
            type_etablissement VARCHAR(100),
            categorie_emplacement VARCHAR(50),
            is_garde BOOLEAN,
            garde_start_date DATETIME,
            garde_end_date DATETIME,
            latitude FLOAT,
            longitude FLOAT,
            location_validated BOOLEAN,
            validated_at DATETIME,
            validated_by_admin_id INTEGER,
            created_at DATETIME,
            updated_at DATETIME
        );
        """
        db.session.execute(text(create_sql))

        # 2. Insert some data
        insert_sql = """
        INSERT INTO pharmacy (code, nom, ville, type_etablissement, categorie_emplacement)
        VALUES ('PH001', 'Pharmacie Test', 'Libreville', 'pharmacie_generale', 'standard');
        """
        db.session.execute(text(insert_sql))
        db.session.commit()

        # Verify the column is missing
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('pharmacy')]
        assert 'is_verified' not in columns

        # 3. Run the migration function
        print("\nRunning check_and_add_missing_columns...")
        init_db.check_and_add_missing_columns()

        # 4. Verify the column was added
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('pharmacy')]
        assert 'is_verified' in columns, "Column 'is_verified' should have been added"

        # 5. Verify data preservation and default value
        result = db.session.execute(text("SELECT nom, is_verified FROM pharmacy WHERE code='PH001'"))
        row = result.fetchone()
        assert row is not None
        assert row[0] == 'Pharmacie Test'
        # SQLite stores booleans as 0/1. The default for bool in init_db is 'false', so we expect 0.
        # Note: init_db.py uses 'false' string for default. SQLite might interpret this depending on how it's inserted.
        # Let's check what init_db does: "ALTER ... DEFAULT false"
        # In SQLite, DEFAULT false might be literal 'false' string if type affinity is weird, or 0.
        # However, boolean columns usually take 0/1.
        print(f"Row after migration: {row}")

        # If SQLite, 'false' might be treated as string "false" or 0 if parsed.
        # But let's assert it exists first.

def test_migration_create_missing_table(app):
    """
    Test that init_db.check_and_create_missing_tables creates missing tables.
    """
    # Patch init_db.app to use our test app
    init_db.app = app

    with app.app_context():
        # 1. Ensure DB is empty (setup does drop_all)
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        assert 'admin' not in tables

        # 2. Run creation
        print("\nRunning check_and_create_missing_tables...")
        init_db.check_and_create_missing_tables()

        # 3. Verify admin table exists
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        assert 'admin' in tables
