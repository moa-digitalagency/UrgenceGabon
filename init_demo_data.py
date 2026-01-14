#!/usr/bin/env python3
"""
UrgenceGabon.com - Initialisation des données de démonstration
Ce script importe les pharmacies directement depuis les données intégrées.

Usage: python init_demo_data.py
"""

import os
import sys
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

PHARMACIES_DATA = [
    {"code": "PG001", "nom": "Pharmacie Radoca", "ville": "Port-Gentil", "quartier": "La Balise", "telephone": "011 55 10 72", "latitude": -0.713589, "longitude": 8.784512, "horaires": "7j/7, 08h00-20h00", "services": "Générale"},
    {"code": "PG002", "nom": "Pharmacie du Grand Village", "ville": "Port-Gentil", "quartier": "Grand Village", "telephone": "011 55 34 83", "latitude": -0.725142, "longitude": 8.771235, "horaires": "7j/7, 08h00-21h00", "services": "Générale / Garde"},
    {"code": "PG003", "nom": "Pharmacie Banco", "ville": "Port-Gentil", "quartier": "Banco", "telephone": "011 55 50 45", "latitude": -0.718521, "longitude": 8.785614, "horaires": "Horaires standards", "services": "Parapharmacie"},
    {"code": "PG004", "nom": "Pharmacie Von'Okuwa", "ville": "Port-Gentil", "quartier": "Centre-ville", "telephone": "011 55 55 32", "latitude": -0.716645, "longitude": 8.785312, "horaires": "Horaires standards", "services": "Générale"},
    {"code": "PG005", "nom": "Pharmacie Andrea", "ville": "Port-Gentil", "quartier": "Boulevard", "telephone": "077 03 97 96", "latitude": -0.711854, "longitude": 8.779214, "horaires": "Horaires standards", "services": "Générale"},
    {"code": "PG006", "nom": "Pharmacie du Boulevard", "ville": "Port-Gentil", "quartier": "Boulevard", "telephone": "011 53 11 03", "latitude": -0.719321, "longitude": 8.781547, "horaires": "Horaires standards", "services": "Générale"},
    {"code": "PG007", "nom": "Pharmacie du Cap", "ville": "Port-Gentil", "quartier": "Centre-ville", "telephone": "011 55 26 80", "latitude": -0.712541, "longitude": 8.786541, "horaires": "Horaires standards", "services": "Générale"},
    {"code": "PG008", "nom": "Pharmacie de Bac Aviation", "ville": "Port-Gentil", "quartier": "Bac Aviation", "telephone": "066 51 43 12", "latitude": -0.713214, "longitude": 8.756214, "horaires": "24h/24 (selon garde)", "services": "Garde"},
    {"code": "PG009", "nom": "Pharmacie du Château", "ville": "Port-Gentil", "quartier": "Château", "telephone": "074 12 45 67", "latitude": -0.731245, "longitude": 8.774125, "horaires": "Horaires standards", "services": "Proximité"},
    {"code": "PG010", "nom": "Pharmacie Centrale", "ville": "Port-Gentil", "quartier": "Centre-ville", "telephone": "011 55 21 64", "latitude": -0.715847, "longitude": 8.783214, "horaires": "Horaires standards", "services": "Générale"},
    {"code": "PG011", "nom": "Pharmacie de la Mosquée", "ville": "Port-Gentil", "quartier": "Mosquée", "telephone": "065 41 22 10", "latitude": -0.721458, "longitude": 8.778541, "horaires": "Horaires standards", "services": "Générale"},
    {"code": "LBV001", "nom": "Grande Pharmacie des Forestiers", "ville": "Libreville", "quartier": "Centre-Ville", "telephone": "011 72 23 52", "latitude": 0.407425, "longitude": 9.443673, "horaires": "08h-20h", "services": "Générale"},
    {"code": "LBV002", "nom": "Pharmacie Sainte-Marie", "ville": "Libreville", "quartier": "Bd Triomphal", "telephone": "011 74 00 52", "latitude": 0.406850, "longitude": 9.444210, "horaires": "07h30-21h", "services": "Générale"},
    {"code": "LBV003", "nom": "La Nouvelle Pharmacie d'Awondo", "ville": "Libreville", "quartier": "Louis", "telephone": "066 15 80 00", "latitude": 0.421689, "longitude": 9.433842, "horaires": "24h/24", "services": "Garde"},
    {"code": "LBV004", "nom": "Pharmacie des Facultés", "ville": "Libreville", "quartier": "Sobraga", "telephone": "011 44 37 38", "latitude": 0.419214, "longitude": 9.450841, "horaires": "07h30-21h30", "services": "Générale"},
    {"code": "LBV005", "nom": "Pharmacie d'Akébé", "ville": "Libreville", "quartier": "Akébé", "telephone": "011 72 01 38", "latitude": 0.398512, "longitude": 9.462314, "horaires": "08h-20h", "services": "Générale"},
    {"code": "LBV006", "nom": "Pharmacie Avolenzame", "ville": "Libreville", "quartier": "Nkembo", "telephone": "065 29 10 02", "latitude": 0.403421, "longitude": 9.463254, "horaires": "07h-20h", "services": "Générale"},
    {"code": "LBV007", "nom": "Pharmacie d'Avorbam", "ville": "Libreville", "quartier": "Akanda", "telephone": "065 50 54 54", "latitude": 0.485124, "longitude": 9.421458, "horaires": "24h/24", "services": "Garde"},
    {"code": "LBV008", "nom": "Pharmacie de l'Aéroport", "ville": "Libreville", "quartier": "Aéroport", "telephone": "077 77 77 77", "latitude": 0.457317, "longitude": 9.412406, "horaires": "08h-21h", "services": "Générale"},
    {"code": "LBV009", "nom": "Pharmacie Nouo Cécile", "ville": "Libreville", "quartier": "IAI", "telephone": "066 28 35 22", "latitude": 0.395214, "longitude": 9.485124, "horaires": "24h/24", "services": "Garde"},
    {"code": "LBV010", "nom": "Pharmacie des Acaé", "ville": "Libreville", "quartier": "Acaé", "telephone": "011 70 49 49", "latitude": 0.365412, "longitude": 9.481245, "horaires": "24h/24", "services": "Garde"},
    {"code": "LBV011", "nom": "Pharmacie de la Poste", "ville": "Libreville", "quartier": "Bord de Mer", "telephone": "011 72 83 30", "latitude": 0.391245, "longitude": 9.441258, "horaires": "08h-19h", "services": "Générale"},
    {"code": "LBV012", "nom": "Pharmacie d'Oloumi", "ville": "Libreville", "quartier": "Oloumi", "telephone": "011 72 15 82", "latitude": 0.384512, "longitude": 9.461245, "horaires": "07h30-20h30", "services": "Générale"},
    {"code": "LBV013", "nom": "Pharmacie du Commissariat Central", "ville": "Libreville", "quartier": "Centre-Ville", "telephone": "074 64 22 22", "latitude": 0.390541, "longitude": 9.453214, "horaires": "08h-21h", "services": "Générale"},
    {"code": "LBV014", "nom": "Pharmacie Jeanne et Léo", "ville": "Libreville", "quartier": "Owendo", "telephone": "011 70 47 60", "latitude": 0.312458, "longitude": 9.501245, "horaires": "08h-20h", "services": "Générale"},
    {"code": "LBV015", "nom": "Pharmacie de Bikélé", "ville": "Libreville", "quartier": "Bikélé", "telephone": "065 19 03 36", "latitude": 0.371245, "longitude": 9.581245, "horaires": "24h/24", "services": "Garde"},
    {"code": "LBV016", "nom": "Pharmacie Rapha-Ël", "ville": "Libreville", "quartier": "PK12", "telephone": "011 46 45 54", "latitude": 0.385214, "longitude": 9.541258, "horaires": "24h/24", "services": "Garde"},
    {"code": "LBV017", "nom": "Pharmacie des Gué-Gué", "ville": "Libreville", "quartier": "Gué-Gué", "telephone": "011 44 41 36", "latitude": 0.435412, "longitude": 9.421245, "horaires": "08h-20h", "services": "Générale"},
    {"code": "LBV018", "nom": "Pharmacie de Glass", "ville": "Libreville", "quartier": "Glass", "telephone": "011 77 23 99", "latitude": 0.375412, "longitude": 9.451245, "horaires": "07h30-21h", "services": "Générale"},
    {"code": "LBV019", "nom": "Pharmacie Saint André", "ville": "Libreville", "quartier": "Okala", "telephone": "066 25 56 67", "latitude": 0.471245, "longitude": 9.401245, "horaires": "08h-20h", "services": "Générale"},
    {"code": "LBV020", "nom": "Pharmacie Le Bon Samaritain", "ville": "Libreville", "quartier": "Angondjé", "telephone": "065 19 03 40", "latitude": 0.501245, "longitude": 9.412458, "horaires": "24h/24", "services": "Garde"},
]


def import_pharmacies():
    """Importe les pharmacies depuis les données intégrées"""
    try:
        from app import app
        from extensions import db
        from models.pharmacy import Pharmacy
        
        with app.app_context():
            imported = 0
            updated = 0
            
            for data in PHARMACIES_DATA:
                try:
                    services = data.get('services', '')
                    is_garde = 'garde' in services.lower() if services else False
                    
                    pharmacy_data = {
                        'code': data['code'],
                        'nom': data['nom'],
                        'ville': data['ville'],
                        'quartier': data.get('quartier', ''),
                        'telephone': data.get('telephone', ''),
                        'horaires': data.get('horaires', ''),
                        'services': services,
                        'latitude': data.get('latitude'),
                        'longitude': data.get('longitude'),
                        'is_garde': is_garde,
                        'is_verified': False,
                        'location_validated': data.get('latitude') is not None and data.get('longitude') is not None,
                        'type_etablissement': 'pharmacie_generale',
                        'categorie_emplacement': 'standard'
                    }
                    
                    existing = Pharmacy.query.filter_by(code=data['code']).first()
                    if existing:
                        for key, value in pharmacy_data.items():
                            setattr(existing, key, value)
                        logger.info(f"Mise à jour: {data['code']} - {data['nom']}")
                        updated += 1
                    else:
                        pharmacy = Pharmacy(**pharmacy_data)
                        db.session.add(pharmacy)
                        logger.info(f"Ajoutée: {data['code']} - {data['nom']}")
                        imported += 1
                    
                except Exception as e:
                    logger.error(f"Erreur pour {data.get('code', '?')}: {e}")
                    continue
            
            db.session.commit()
            
            logger.info(f"\nRésumé: {imported} ajoutée(s), {updated} mise(s) à jour")
            return True, imported + updated
            
    except Exception as e:
        logger.error(f"Erreur lors de l'importation: {e}")
        import traceback
        traceback.print_exc()
        return False, 0


def main():
    print("\n" + "="*60)
    print("IMPORTATION DES PHARMACIES - UrgenceGabon.com")
    print("="*60)
    print(f"\nNombre de pharmacies à importer: {len(PHARMACIES_DATA)}")
    
    confirm = input("\nImporter les pharmacies? Tapez 'OUI' pour confirmer: ")
    
    if confirm.strip().upper() != 'OUI':
        print("Opération annulée.")
        sys.exit(0)
    
    success, count = import_pharmacies()
    
    print("\n" + "="*60)
    if success:
        print(f"Importation terminée: {count} pharmacie(s) traitée(s).")
        print("Note: Toutes les pharmacies sont NON VÉRIFIÉES.")
    else:
        print("Erreur lors de l'importation.")
    print("="*60 + "\n")
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
