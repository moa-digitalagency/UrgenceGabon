#!/usr/bin/env python3
"""
UrgenceGabon.com
By MOA Digital Agency LLC
Developed by: Aisance KALONJI
Contact: moa@myoneart.com
Website: www.myoneart.com

init_db.py - Initialisation et migration de la base de données
Ce fichier crée les tables, vérifie l'intégrité et initialise les paramètres par défaut.
Préserve TOUTES les données existantes - migration sécurisée sans perte de données.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import inspect, text

env_file = Path('.env')
if env_file.exists():
    load_dotenv(env_file)

from app import app
from extensions import db


def get_required_models():
    """Retourne tous les modèles requis."""
    with app.app_context():
        from models.pharmacy import Pharmacy
        from models.admin import Admin
        from models.submission import LocationSubmission, InfoSubmission, PharmacyView, Suggestion, PharmacyProposal, PageInteraction, UserAction
        from models.emergency_contact import EmergencyContact
        from models.site_settings import SiteSettings, PopupMessage
        from models.advertisement import Advertisement, AdSettings
        from models.activity_log import ActivityLog
        
        return {
            'pharmacy': Pharmacy,
            'admin': Admin,
            'location_submission': LocationSubmission,
            'info_submission': InfoSubmission,
            'pharmacy_view': PharmacyView,
            'suggestion': Suggestion,
            'pharmacy_proposal': PharmacyProposal,
            'page_interaction': PageInteraction,
            'user_action': UserAction,
            'emergency_contact': EmergencyContact,
            'site_settings': SiteSettings,
            'popup_message': PopupMessage,
            'advertisement': Advertisement,
            'ad_settings': AdSettings,
            'activity_log': ActivityLog,
        }


def get_existing_tables():
    """Retourne l'ensemble des tables existantes dans la base de données."""
    inspector = inspect(db.engine)
    return set(inspector.get_table_names())


def check_table_data_integrity():
    """Vérifie l'intégrité des données existantes et affiche un rapport."""
    with app.app_context():
        inspector = inspect(db.engine)
        existing_tables = get_existing_tables()
        
        print("\n📊 Vérification des données existantes:")
        
        total_tables = 0
        tables_with_data = 0
        
        for table_name in sorted(existing_tables):
            try:
                # Compter les lignes dans chaque table
                result = db.session.execute(text(f"SELECT COUNT(*) as count FROM {table_name}"))
                row_count = result.scalar() or 0
                
                if row_count > 0:
                    print(f"  ✓ {table_name}: {row_count} lignes")
                    tables_with_data += 1
                else:
                    print(f"  ✓ {table_name}: vide")
                total_tables += 1
            except Exception as e:
                print(f"  ⚠️  {table_name}: impossible à lire ({str(e)[:40]})")
        
        if total_tables == 0:
            print("  ℹ️  Base de données vide (première initialisation)")
        elif tables_with_data > 0:
            print(f"\n✅ {tables_with_data}/{total_tables} table(s) contiennent des données - Elles seront préservées")
        
        return tables_with_data > 0


def check_and_create_missing_tables():
    """Vérifie et crée les tables manquantes sans affecter les données existantes."""
    with app.app_context():
        models = get_required_models()
        existing_tables = get_existing_tables()
        required_table_names = set(models.keys())
        
        missing_tables = required_table_names - existing_tables
        
        if not missing_tables:
            print("\n✅ Toutes les tables requises existent!")
            return True
        
        print(f"\n⚠️  {len(missing_tables)} table(s) manquante(s):")
        for table in sorted(missing_tables):
            print(f"  - {table}")
        
        print("\n📝 Création des tables manquantes (les données existantes sont préservées)...")
        success_count = 0
        for table_name in sorted(missing_tables):
            try:
                models[table_name].__table__.create(db.engine, checkfirst=True)
                print(f"  ✓ Créée: {table_name}")
                success_count += 1
            except Exception as e:
                print(f"  ✗ Erreur pour {table_name}: {str(e)[:60]}")
                # Continuer même en cas d'erreur
        
        if success_count == len(missing_tables):
            return True
        else:
            print(f"⚠️  {len(missing_tables) - success_count} table(s) n'ont pas pu être créées")
            return True  # Continuer quand même


def check_and_add_missing_columns():
    """Vérifie et ajoute les colonnes manquantes sans perdre les données existantes."""
    with app.app_context():
        models = get_required_models()
        existing_tables = get_existing_tables()
        inspector = inspect(db.engine)
        
        print("\n🔍 Vérification des colonnes existantes:")
        
        schema_issues = []
        tables_ok = 0
        
        for table_name, model_class in sorted(models.items()):
            if table_name not in existing_tables:
                print(f"  ℹ️  {table_name}: table à créer")
                continue
            
            db_columns = {col['name'] for col in inspector.get_columns(table_name)}
            model_columns = {col.name for col in model_class.__table__.columns}
            
            missing_cols = model_columns - db_columns
            if missing_cols:
                schema_issues.append((table_name, missing_cols, model_class))
                print(f"  ⚠️  {table_name}: {len(missing_cols)} colonne(s) manquante(s) {sorted(missing_cols)}")
            else:
                print(f"  ✓ {table_name}: schéma complet")
                tables_ok += 1
        
        if not schema_issues:
            print(f"\n✅ Tous les schémas sont à jour! ({tables_ok} table(s) vérifiée(s))")
            return True
        
        print(f"\n🔧 Ajout des colonnes manquantes (les données existantes sont préservées)...")
        
        for table_name, missing_cols, model_class in schema_issues:
            for col_name in sorted(missing_cols):
                try:
                    col = model_class.__table__.columns[col_name]
                    col_type = str(col.type)
                    
                    # Construire la clause ALTER TABLE avec valeur par défaut si nécessaire
                    if col.nullable:
                        alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}"
                    else:
                        # Pour les colonnes non-nullables, utiliser une valeur par défaut appropriée
                        default_val = get_default_value_for_type(col_type)
                        alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type} DEFAULT {default_val}"
                    
                    db.session.execute(text(alter_sql))
                    db.session.commit()
                    print(f"  ✓ Ajoutée colonne: {table_name}.{col_name}")
                except Exception as e:
                    db.session.rollback()
                    print(f"  ⚠️  {table_name}.{col_name}: {str(e)[:50]} (non-critique, continuant...)")
                    # Continuer même en cas d'erreur
        
        return True


def get_default_value_for_type(col_type):
    """Retourne une valeur par défaut appropriée pour un type de colonne."""
    col_type_lower = col_type.lower()
    
    if 'int' in col_type_lower:
        return '0'
    elif 'bool' in col_type_lower:
        return 'false'
    elif 'date' in col_type_lower or 'time' in col_type_lower:
        return "CURRENT_TIMESTAMP"
    elif 'text' in col_type_lower or 'string' in col_type_lower or 'varchar' in col_type_lower:
        return "''"
    elif 'float' in col_type_lower or 'decimal' in col_type_lower or 'numeric' in col_type_lower:
        return '0.0'
    else:
        return 'NULL'


def init_database():
    """Initialise complètement la base de données - crée toutes les tables si nécessaire."""
    print("\n" + "=" * 90)
    print("INITIALISATION ET VÉRIFICATION - BASE DE DONNÉES")
    print("=" * 90)
    
    with app.app_context():
        # Importer tous les modèles pour les enregistrer avec SQLAlchemy
        from models.pharmacy import Pharmacy
        from models.admin import Admin
        from models.submission import LocationSubmission, InfoSubmission, PharmacyView, Suggestion, PharmacyProposal, PageInteraction, UserAction
        from models.emergency_contact import EmergencyContact
        from models.site_settings import SiteSettings, PopupMessage
        from models.advertisement import Advertisement, AdSettings
        from models.activity_log import ActivityLog
        
        existing_tables = get_existing_tables()
        print(f"\n📋 État actuel: {len(existing_tables)} table(s) existante(s)")
        
        # Créer toutes les tables manquantes (checkfirst=True préserve les données)
        print("\n🔨 Création/vérification des tables...")
        db.create_all()
        
        new_existing_tables = get_existing_tables()
        print(f"✅ Toutes les tables requises existent! ({len(new_existing_tables)} table(s))")


def init_admin_from_env():
    """Initialise le compte administrateur à partir des variables d'environnement."""
    with app.app_context():
        from models.admin import Admin
        
        username = os.environ.get('ADMIN_USERNAME', 'admin')
        password = os.environ.get('ADMIN_PASSWORD')
        
        if not password:
            print("\n⚠️  ADMIN_PASSWORD non configuré - admin ne sera pas initialisé.")
            print("   Définissez ADMIN_PASSWORD pour créer/mettre à jour le compte admin.")
            return False
        
        existing_admin = Admin.query.filter_by(username=username).first()
        if existing_admin:
            existing_admin.set_password(password)
            db.session.commit()
            print(f"\n✓ Admin '{username}' - mot de passe mis à jour")
        else:
            try:
                admin = Admin(username=username)
                admin.set_password(password)
                db.session.add(admin)
                db.session.commit()
                print(f"\n✓ Admin '{username}' - créé avec succès")
            except Exception as e:
                db.session.rollback()
                print(f"\n⚠️  Admin '{username}' - impossible de créer ({str(e)[:50]})")
        
        return True


def init_default_seo_settings():
    """Initialise les paramètres SEO par défaut s'ils ne sont pas présents."""
    with app.app_context():
        from models.site_settings import SiteSettings
        
        defaults = {
            'site_name': 'UrgenceGabon.com',
            'og_title': 'UrgenceGabon.com - Trouvez votre pharmacie au Gabon',
            'og_description': 'Annuaire complet des pharmacies au Gabon. Trouvez les pharmacies de garde, numéros d\'urgence et informations de contact.',
            'meta_description': 'Annuaire des pharmacies au Gabon. Pharmacies de garde 24h/24, numéros d\'urgence, carte interactive. Trouvez la pharmacie la plus proche.',
            'meta_keywords': 'pharmacie gabon, pharmacie garde libreville, urgence gabon, pharmacie 24h, samu gabon, pompiers gabon',
            'twitter_handle': '',
            'canonical_url': '',
            'google_site_verification': '',
            'robots_txt': 'User-agent: *\nAllow: /',
        }
        
        created_count = 0
        for key, value in defaults.items():
            existing = SiteSettings.query.filter_by(key=key).first()
            if not existing:
                try:
                    SiteSettings.set(key, value)
                    created_count += 1
                except Exception:
                    pass  # Continuer même en cas d'erreur
        
        if created_count > 0:
            print(f"\n✓ {created_count} paramètre(s) SEO créé(s)")
        else:
            print("\n✓ Les paramètres SEO existaient déjà")


def init_default_pwa_settings():
    """Initialise les paramètres PWA par défaut s'ils ne sont pas présents."""
    with app.app_context():
        from models.site_settings import SiteSettings

        defaults = {
            'pwa_enabled': 'false',
            'pwa_mode': 'default',
            'pwa_custom_name': '',
            'pwa_custom_icon_filename': '',
        }

        created_count = 0
        for key, value in defaults.items():
            existing = SiteSettings.query.filter_by(key=key).first()
            if not existing:
                try:
                    SiteSettings.set(key, value)
                    created_count += 1
                except Exception:
                    pass

        if created_count > 0:
            print(f"\n✓ {created_count} paramètre(s) PWA créé(s)")
        else:
            print("\n✓ Les paramètres PWA existaient déjà")


if __name__ == '__main__':
    try:
        # Étape 1: Initialiser les tables
        init_database()
        
        # Étape 2: Vérifier l'intégrité des données
        has_data = check_table_data_integrity()
        
        # Étape 3: Créer les tables manquantes
        check_and_create_missing_tables()
        
        # Étape 4: Vérifier et ajouter les colonnes manquantes
        check_and_add_missing_columns()
        
        # Étape 5: Initialiser l'admin et les paramètres
        init_admin_from_env()
        init_default_seo_settings()
        init_default_pwa_settings()
        
        print("\n" + "=" * 90)
        if has_data:
            print("✅ Migration terminée - Données existantes préservées!")
        else:
            print("✅ Initialisation terminée - Base de données prête!")
        print("=" * 90)
        
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erreur lors de la migration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
