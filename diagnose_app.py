#!/usr/bin/env python3
"""
UrgenceGabon.com - Diagnostic Script
Ce script vérifie l'état de l'application, de la base de données et de la configuration.
"""

import os
import sys
import logging
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def check_env():
    logger.info("Vérification des variables d'environnement...")
    required = ['DATABASE_URL', 'SESSION_SECRET']
    missing = [var for var in required if not os.environ.get(var)]

    if missing:
        logger.error(f"Variables manquantes: {', '.join(missing)}")
        return False

    logger.info("✓ Variables d'environnement OK")
    return True

def check_db():
    logger.info("Vérification de la connexion à la base de données...")
    try:
        from app import app
        from extensions import db
        from sqlalchemy import text

        with app.app_context():
            db.session.execute(text("SELECT 1"))
            logger.info("✓ Connexion à la base de données réussie")

            from init_db import get_existing_tables, get_required_models
            existing = get_existing_tables()
            required = set(get_required_models().keys())

            missing = required - existing
            if missing:
                logger.warning(f"Tables manquantes: {', '.join(missing)}")
                logger.info("Conseil: Exécutez 'python init_db.py' pour créer les tables.")
            else:
                logger.info(f"✓ Toutes les tables ({len(required)}) sont présentes")

    except Exception as e:
        logger.error(f"Erreur de base de données: {e}")
        return False
    return True

def check_files():
    logger.info("Vérification des fichiers statiques et uploads...")
    paths = [
        'static',
        'static/uploads',
        'static/uploads/popups',
        'static/uploads/settings',
        'templates'
    ]

    for p in paths:
        if Path(p).exists():
            logger.info(f"✓ {p} existe")
        else:
            logger.warning(f"✗ {p} est manquant")
            try:
                os.makedirs(p, exist_ok=True)
                logger.info(f"  -> Créé {p}")
            except Exception as e:
                logger.error(f"  -> Impossible de créer {p}: {e}")

if __name__ == '__main__':
    print("="*50)
    print("UrgenceGabon.com - Diagnostic")
    print("="*50)

    e_ok = check_env()
    db_ok = check_db()
    check_files()

    print("="*50)
    if e_ok and db_ok:
        print("Diagnostic terminé: L'application semble prête.")
    else:
        print("Diagnostic terminé: Des problèmes ont été identifiés.")
    print("="*50)
