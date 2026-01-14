#!/usr/bin/env python3
"""
UrgenceGabon.com - Nettoyage des données pharmacies
Ce script supprime toutes les pharmacies et données liées de la base de données PostgreSQL.
À utiliser avec précaution sur le VPS de production.

Usage: python clean_pharmacies.py
"""

import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def clean_pharmacies():
    """Supprime toutes les pharmacies et données liées de la base de données"""
    try:
        from app import app
        from extensions import db
        from models.pharmacy import Pharmacy
        from sqlalchemy import text
        
        with app.app_context():
            count = Pharmacy.query.count()
            
            if count == 0:
                logger.info("Aucune pharmacie à supprimer.")
                return True
            
            logger.info(f"Suppression de {count} pharmacie(s) et données liées...")
            
            logger.info("Suppression des soumissions de localisation...")
            db.session.execute(text('DELETE FROM location_submission'))
            
            logger.info("Suppression des soumissions d'informations...")
            db.session.execute(text('DELETE FROM info_submission'))
            
            logger.info("Suppression des vues de pharmacies...")
            db.session.execute(text('DELETE FROM pharmacy_view'))
            
            logger.info("Suppression des actions utilisateurs...")
            db.session.execute(text('DELETE FROM user_action WHERE pharmacy_id IS NOT NULL'))
            
            logger.info("Suppression des pharmacies...")
            db.session.execute(text('DELETE FROM pharmacy'))
            
            db.session.commit()
            
            remaining = Pharmacy.query.count()
            if remaining == 0:
                logger.info(f"{count} pharmacie(s) et données liées supprimées avec succès.")
                return True
            else:
                logger.warning(f"Attention: {remaining} pharmacie(s) restante(s)")
                return False
            
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage: {e}")
        import traceback
        traceback.print_exc()
        try:
            db.session.rollback()
        except:
            pass
        return False


def main():
    print("\n" + "="*60)
    print("NETTOYAGE DES PHARMACIES - UrgenceGabon.com")
    print("="*60)
    print("\nCe script va supprimer:")
    print("  - Toutes les pharmacies")
    print("  - Toutes les soumissions de localisation")
    print("  - Toutes les soumissions d'informations")
    print("  - Toutes les vues de pharmacies")
    print("  - Toutes les actions utilisateurs liées")
    
    confirm = input("\nATTENTION: Cette action est irréversible.\nTapez 'OUI' pour confirmer: ")
    
    if confirm.strip().upper() != 'OUI':
        print("Opération annulée.")
        sys.exit(0)
    
    success = clean_pharmacies()
    
    print("\n" + "="*60)
    if success:
        print("Nettoyage terminé avec succès.")
    else:
        print("Erreur lors du nettoyage.")
    print("="*60 + "\n")
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
