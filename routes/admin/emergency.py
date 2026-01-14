"""
UrgenceGabon.com
By MOA Digital Agency LLC
Developed by: Aisance KALONJI
Contact: moa@myoneart.com
Website: www.myoneart.com

routes/admin/emergency.py - Gestion des contacts d'urgence
Ce fichier gère le CRUD des contacts d'urgence: police, pompiers,
hôpitaux et autres services d'urgence par ville.
"""

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from models.emergency_contact import EmergencyContact, EMERGENCY_SERVICE_TYPES
from utils.helpers import CITY_COORDINATES
from extensions import db
from routes.admin import admin_bp
import logging

logger = logging.getLogger(__name__)


@admin_bp.route('/emergency-contacts')
@login_required
def list_emergency_contacts():
    contacts = EmergencyContact.query.order_by(EmergencyContact.ordering).all()
    return render_template('admin/emergency_contacts.html', 
                          contacts=contacts, 
                          service_types=EMERGENCY_SERVICE_TYPES,
                          cities=list(CITY_COORDINATES.keys()))


@admin_bp.route('/emergency-contact/add', methods=['GET', 'POST'])
@login_required
def add_emergency_contact():
    if request.method == 'POST':
        try:
            service_type = request.form.get('service_type')
            label = request.form.get('label')
            phone_numbers = request.form.get('phone_numbers')
            
            if not service_type:
                flash('Le type de service est obligatoire', 'error')
                return render_template('admin/emergency_contact_form.html', 
                                      contact=None, 
                                      service_types=EMERGENCY_SERVICE_TYPES,
                                      cities=list(CITY_COORDINATES.keys()))
            
            if not label:
                flash('Le libellé est obligatoire', 'error')
                return render_template('admin/emergency_contact_form.html', 
                                      contact=None, 
                                      service_types=EMERGENCY_SERVICE_TYPES,
                                      cities=list(CITY_COORDINATES.keys()))
            
            if not phone_numbers:
                flash('Au moins un numéro de téléphone est obligatoire', 'error')
                return render_template('admin/emergency_contact_form.html', 
                                      contact=None, 
                                      service_types=EMERGENCY_SERVICE_TYPES,
                                      cities=list(CITY_COORDINATES.keys()))
            
            contact = EmergencyContact(
                ville=request.form.get('ville') or None,
                service_type=service_type,
                label=label,
                phone_numbers=phone_numbers,
                address=request.form.get('address', ''),
                notes=request.form.get('notes', ''),
                is_national=request.form.get('is_national') == 'on',
                is_active=request.form.get('is_active') == 'on',
                ordering=int(request.form.get('ordering', 0) or 0)
            )
            db.session.add(contact)
            db.session.commit()
            flash('Contact d\'urgence ajouté avec succès', 'success')
            return redirect(url_for('admin.list_emergency_contacts'))
        except ValueError as e:
            db.session.rollback()
            flash(f'Erreur de format: {str(e)}', 'error')
            logger.error(f"ValueError in add_emergency_contact: {e}")
        except Exception as e:
            db.session.rollback()
            flash('Erreur lors de l\'enregistrement. Veuillez vérifier les données.', 'error')
            logger.error(f"Error in add_emergency_contact: {e}")
    
    return render_template('admin/emergency_contact_form.html', 
                          contact=None, 
                          service_types=EMERGENCY_SERVICE_TYPES,
                          cities=list(CITY_COORDINATES.keys()))


@admin_bp.route('/emergency-contact/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_emergency_contact(id):
    contact = EmergencyContact.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            service_type = request.form.get('service_type')
            label = request.form.get('label')
            phone_numbers = request.form.get('phone_numbers')
            
            if not service_type:
                flash('Le type de service est obligatoire', 'error')
                return render_template('admin/emergency_contact_form.html', 
                                      contact=contact, 
                                      service_types=EMERGENCY_SERVICE_TYPES,
                                      cities=list(CITY_COORDINATES.keys()))
            
            if not label:
                flash('Le libellé est obligatoire', 'error')
                return render_template('admin/emergency_contact_form.html', 
                                      contact=contact, 
                                      service_types=EMERGENCY_SERVICE_TYPES,
                                      cities=list(CITY_COORDINATES.keys()))
            
            if not phone_numbers:
                flash('Au moins un numéro de téléphone est obligatoire', 'error')
                return render_template('admin/emergency_contact_form.html', 
                                      contact=contact, 
                                      service_types=EMERGENCY_SERVICE_TYPES,
                                      cities=list(CITY_COORDINATES.keys()))
            
            contact.ville = request.form.get('ville') or None
            contact.service_type = service_type
            contact.label = label
            contact.phone_numbers = phone_numbers
            contact.address = request.form.get('address', '')
            contact.notes = request.form.get('notes', '')
            contact.is_national = request.form.get('is_national') == 'on'
            contact.is_active = request.form.get('is_active') == 'on'
            contact.ordering = int(request.form.get('ordering', 0) or 0)
            
            db.session.commit()
            flash('Contact d\'urgence mis à jour', 'success')
            return redirect(url_for('admin.list_emergency_contacts'))
        except ValueError as e:
            db.session.rollback()
            flash(f'Erreur de format: {str(e)}', 'error')
            logger.error(f"ValueError in edit_emergency_contact: {e}")
        except Exception as e:
            db.session.rollback()
            flash('Erreur lors de la mise à jour. Veuillez vérifier les données.', 'error')
            logger.error(f"Error in edit_emergency_contact: {e}")
    
    return render_template('admin/emergency_contact_form.html', 
                          contact=contact, 
                          service_types=EMERGENCY_SERVICE_TYPES,
                          cities=list(CITY_COORDINATES.keys()))


@admin_bp.route('/emergency-contact/<int:id>/delete', methods=['POST'])
@login_required
def delete_emergency_contact(id):
    try:
        contact = EmergencyContact.query.get_or_404(id)
        db.session.delete(contact)
        db.session.commit()
        flash('Contact d\'urgence supprimé', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erreur lors de la suppression', 'error')
        logger.error(f"Error in delete_emergency_contact: {e}")
    return redirect(url_for('admin.list_emergency_contacts'))
