"""
UrgenceGabon.com
By MOA Digital Agency LLC
Developed by: Aisance KALONJI
Contact: moa@myoneart.com
Website: www.myoneart.com

routes/admin/dashboard.py - Tableau de bord administrateur
Ce fichier affiche le dashboard avec statistiques, soumissions en attente,
graphiques de vues et activités récentes.
"""

import logging
from flask import render_template, flash
from flask_login import login_required
from models.pharmacy import Pharmacy
from models.submission import LocationSubmission, InfoSubmission, PharmacyView, Suggestion, PharmacyProposal, PageInteraction
from extensions import db
from datetime import datetime, timedelta
from sqlalchemy import func, case
from routes.admin import admin_bp

logger = logging.getLogger(__name__)


def safe_query(query_func, default=None):
    """Execute a query safely, returning default on error"""
    try:
        return query_func()
    except Exception as e:
        import traceback
        logger.error(f"Query error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        db.session.rollback()
        return default if default is not None else []


@admin_bp.route('/')
@login_required
def admin_dashboard():
    # Initialize variables with defaults
    pharmacies = []

    try:
        # Don't use safe_query for the main pharmacies list so we can see the error if it fails
        pharmacies = Pharmacy.query.order_by(Pharmacy.ville, Pharmacy.nom).all()
        # Debug: log pharmacy count
        logger.info(f"Dashboard loaded: {len(pharmacies)} pharmacies found")
    except Exception as e:
        import traceback
        logger.error(f"Error loading pharmacies: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        flash(f'Erreur lors du chargement des pharmacies: {str(e)}', 'error')
        pharmacies = []

    try:
        pending_locations = safe_query(
            lambda: LocationSubmission.query.filter_by(status='pending').order_by(LocationSubmission.created_at.desc()).all(),
            []
        )
        pending_infos = safe_query(
            lambda: InfoSubmission.query.filter_by(status='pending').order_by(InfoSubmission.created_at.desc()).all(),
            []
        )
        pending_suggestions = safe_query(
            lambda: Suggestion.query.filter_by(status='pending').order_by(Suggestion.created_at.desc()).all(),
            []
        )
        pending_proposals = safe_query(
            lambda: PharmacyProposal.query.filter_by(status='pending').order_by(PharmacyProposal.created_at.desc()).all(),
            []
        )
        
        top_pharmacies = safe_query(
            lambda: db.session.query(
                Pharmacy.id, Pharmacy.nom, Pharmacy.ville,
                func.count(PharmacyView.id).label('view_count')
            ).outerjoin(PharmacyView).group_by(Pharmacy.id).order_by(func.count(PharmacyView.id).desc()).limit(10).all(),
            []
        )
        
        recent_pharmacies = safe_query(
            lambda: Pharmacy.query.order_by(Pharmacy.updated_at.desc()).limit(5).all(),
            []
        )
        
        total_views = safe_query(
            lambda: db.session.query(func.count(PharmacyView.id)).scalar() or 0,
            0
        )
        
        views_by_city_query = safe_query(
            lambda: db.session.query(
                Pharmacy.ville,
                func.count(PharmacyView.id).label('view_count')
            ).join(PharmacyView, Pharmacy.id == PharmacyView.pharmacy_id).group_by(Pharmacy.ville).order_by(func.count(PharmacyView.id).desc()).all(),
            []
        )
        views_by_city = [{'ville': row.ville, 'view_count': row.view_count} for row in views_by_city_query]
        
        pharmacies_by_city_query = safe_query(
            lambda: db.session.query(
                Pharmacy.ville,
                func.count(Pharmacy.id).label('count')
            ).group_by(Pharmacy.ville).order_by(func.count(Pharmacy.id).desc()).all(),
            []
        )
        pharmacies_by_city = [{'ville': row.ville, 'count': row.count} for row in pharmacies_by_city_query]
        
        pharmacies_by_type_query = safe_query(
            lambda: db.session.query(
                Pharmacy.type_etablissement,
                func.count(Pharmacy.id).label('count')
            ).group_by(Pharmacy.type_etablissement).all(),
            []
        )
        pharmacies_by_type = [{'type': row.type_etablissement, 'count': row.count} for row in pharmacies_by_type_query]
        
        today = datetime.utcnow().date()
        day_names = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']
        
        start_7_days = datetime.combine(today - timedelta(days=6), datetime.min.time())
        views_7_days_query = safe_query(
            lambda: db.session.query(
                func.date(PharmacyView.viewed_at).label('view_date'),
                func.count(PharmacyView.id).label('count')
            ).filter(PharmacyView.viewed_at >= start_7_days).group_by(func.date(PharmacyView.viewed_at)).all(),
            []
        )
        views_7_days_dict = {str(row.view_date): row.count for row in views_7_days_query}
        
        views_last_7_days = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            views_last_7_days.append({
                'date': day.strftime('%d/%m'),
                'day_name': day_names[day.weekday()],
                'count': views_7_days_dict.get(str(day), 0)
            })
        
        start_30_days = datetime.combine(today - timedelta(days=29), datetime.min.time())
        views_30_days_query = safe_query(
            lambda: db.session.query(
                func.date(PharmacyView.viewed_at).label('view_date'),
                func.count(PharmacyView.id).label('count')
            ).filter(PharmacyView.viewed_at >= start_30_days).group_by(func.date(PharmacyView.viewed_at)).all(),
            []
        )
        views_30_days_dict = {str(row.view_date): row.count for row in views_30_days_query}
        
        views_last_30_days = []
        for i in range(29, -1, -1):
            day = today - timedelta(days=i)
            views_last_30_days.append({
                'date': day.strftime('%d/%m'),
                'count': views_30_days_dict.get(str(day), 0)
            })
        
        location_counts = safe_query(
            lambda: db.session.query(
                LocationSubmission.status,
                func.count(LocationSubmission.id)
            ).group_by(LocationSubmission.status).all(),
            []
        )
        location_stats = {status: count for status, count in location_counts}
        total_locations = sum(location_stats.values())
        approved_locations = location_stats.get('approved', 0)
        
        info_counts = safe_query(
            lambda: db.session.query(
                InfoSubmission.status,
                func.count(InfoSubmission.id)
            ).group_by(InfoSubmission.status).all(),
            []
        )
        info_stats = {status: count for status, count in info_counts}
        total_infos = sum(info_stats.values())
        approved_infos = info_stats.get('approved', 0)
        
        total_suggestions = safe_query(
            lambda: Suggestion.query.count(),
            0
        )
        
        proposal_counts = safe_query(
            lambda: db.session.query(
                PharmacyProposal.status,
                func.count(PharmacyProposal.id)
            ).group_by(PharmacyProposal.status).all(),
            []
        )
        proposal_stats = {status: count for status, count in proposal_counts}
        total_proposals = sum(proposal_stats.values())
        approved_proposals = proposal_stats.get('approved', 0)
        
        today_start = datetime.combine(today, datetime.min.time())
        week_start = datetime.combine(today - timedelta(days=today.weekday()), datetime.min.time())
        month_start = datetime.combine(today.replace(day=1), datetime.min.time())
        
        views_stats = safe_query(
            lambda: db.session.query(
                func.count(case((PharmacyView.viewed_at >= today_start, 1))),
                func.count(case((PharmacyView.viewed_at >= week_start, 1))),
                func.count(case((PharmacyView.viewed_at >= month_start, 1)))
            ).first(),
            None
        )
        views_today, views_this_week, views_this_month = views_stats or (0, 0, 0)
        
        interaction_stats = safe_query(
            lambda: db.session.query(
                func.count(case(((PageInteraction.interaction_type == 'page_load') & (PageInteraction.created_at >= today_start), 1))),
                func.count(case(((PageInteraction.interaction_type == 'tab_switch') & (PageInteraction.created_at >= today_start), 1))),
                func.count(case(((PageInteraction.interaction_type == 'search') & (PageInteraction.created_at >= today_start), 1))),
                func.count(case(((PageInteraction.interaction_type == 'city_filter') & (PageInteraction.created_at >= today_start), 1))),
                func.count(case((PageInteraction.created_at >= start_7_days, 1))),
                func.count(case((PageInteraction.created_at >= start_30_days, 1))),
                func.count(PageInteraction.id)
            ).first(),
            None
        )
        
        page_loads, tab_switches, searches, filters, interactions_7_days, interactions_30_days, total_interactions = interaction_stats or (0, 0, 0, 0, 0, 0, 0)
        
        interactions_today = page_loads + tab_switches + searches + filters
        
        return render_template('admin/dashboard.html', 
            pharmacies=pharmacies,
            pending_locations=pending_locations,
            pending_infos=pending_infos,
            pending_suggestions=pending_suggestions,
            pending_proposals=pending_proposals,
            top_pharmacies=top_pharmacies,
            recent_pharmacies=recent_pharmacies,
            total_views=total_views,
            views_by_city=views_by_city,
            pharmacies_by_city=pharmacies_by_city,
            pharmacies_by_type=pharmacies_by_type,
            views_last_7_days=views_last_7_days,
            views_last_30_days=views_last_30_days,
            total_locations=total_locations,
            approved_locations=approved_locations,
            total_infos=total_infos,
            approved_infos=approved_infos,
            total_suggestions=total_suggestions,
            total_proposals=total_proposals,
            approved_proposals=approved_proposals,
            views_today=views_today,
            views_this_week=views_this_week,
            views_this_month=views_this_month,
            page_loads=page_loads,
            tab_switches=tab_switches,
            searches=searches,
            filters=filters,
            total_interactions=total_interactions,
            interactions_today=interactions_today,
            interactions_7_days=interactions_7_days,
            interactions_30_days=interactions_30_days
        )
        
    except Exception as e:
        import traceback
        logger.error(f"Dashboard error: {e}")
        logger.error(f"Dashboard traceback: {traceback.format_exc()}")
        db.session.rollback()
        # Include detailed error in flash message for debugging
        flash(f'Erreur lors du chargement: {str(e)}', 'error')
        # If the main try block fails, we still need to render the template
        # but with empty data. However, individual try blocks above should handle most cases.
        return render_template('admin/dashboard.html', 
            pharmacies=[],
            pending_locations=[],
            pending_infos=[],
            pending_suggestions=[],
            pending_proposals=[],
            top_pharmacies=[],
            recent_pharmacies=[],
            total_views=0,
            views_by_city=[],
            pharmacies_by_city=[],
            pharmacies_by_type=[],
            views_last_7_days=[],
            views_last_30_days=[],
            total_locations=0,
            approved_locations=0,
            total_infos=0,
            approved_infos=0,
            total_suggestions=0,
            total_proposals=0,
            approved_proposals=0,
            views_today=0,
            views_this_week=0,
            views_this_month=0,
            page_loads=0,
            tab_switches=0,
            searches=0,
            filters=0,
            total_interactions=0,
            interactions_today=0,
            interactions_7_days=0,
            interactions_30_days=0
        )
