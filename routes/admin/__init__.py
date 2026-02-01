"""
UrgenceGabon.com
By MOA Digital Agency LLC
Developed by: Aisance KALONJI
Contact: moa@myoneart.com
Website: www.myoneart.com

routes/admin/__init__.py - Module administration
Ce fichier initialise le blueprint admin et fournit les fonctions utilitaires
pour l'upload de fichiers et la validation des données.
"""

import os
import uuid
from flask import Blueprint, request, abort
from werkzeug.utils import secure_filename

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg', 'ico'}


def get_json_or_400():
    try:
        data = request.get_json(force=False, silent=True)
        if data is None:
            abort(400, description='Invalid JSON data')
        return data
    except Exception:
        abort(400, description='Invalid JSON data')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_upload_path(subfolder='popups'):
    upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'static', 'uploads', subfolder)
    os.makedirs(upload_dir, exist_ok=True)
    return upload_dir


def safe_delete_upload(filename, subfolder='popups'):
    if not filename or '..' in filename or '/' in filename or '\\' in filename:
        return
    upload_dir = get_upload_path(subfolder)
    file_path = os.path.join(upload_dir, filename)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        os.remove(file_path)


def save_upload_file(file, subfolder='popups', prefix=''):
    if not file or not file.filename or not allowed_file(file.filename):
        return None
    original_filename = secure_filename(file.filename)
    ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'jpg'
    new_filename = f"{prefix}{uuid.uuid4().hex}.{ext}"
    upload_dir = get_upload_path(subfolder)
    file.save(os.path.join(upload_dir, new_filename))
    return new_filename


from routes.admin import auth
from routes.admin import dashboard
from routes.admin import pharmacy
from routes.admin import submissions
from routes.admin import emergency
from routes.admin import settings
from routes.admin import ads
from routes.admin import logs

@admin_bp.context_processor
def inject_admin_stats():
    """
    Ensure all statistical variables used in the admin dashboard are always defined.
    This provides safe default values for all admin templates.
    """
    return {
        'pharmacies': None,
        'garde_pharmacies': [],
        'total_pharmacies_count': 0,
        'garde_pharmacies_count': 0,
        'gps_pharmacies_count': 0,
        'validated_gps_count': 0,
        'verified_pharmacies_count': 0,
        'pending_locations': [],
        'pending_infos': [],
        'pending_suggestions': [],
        'pending_proposals': [],
        'top_pharmacies': [],
        'recent_pharmacies': [],
        'total_views': 0,
        'views_by_city': [],
        'pharmacies_by_city': [],
        'pharmacies_by_type': [],
        'views_last_7_days': [],
        'views_last_30_days': [],
        'total_locations': 0,
        'approved_locations': 0,
        'total_infos': 0,
        'approved_infos': 0,
        'total_suggestions': 0,
        'total_proposals': 0,
        'approved_proposals': 0,
        'views_today': 0,
        'views_this_week': 0,
        'views_this_month': 0,
        'page_loads': 0,
        'tab_switches': 0,
        'searches': 0,
        'filters': 0,
        'total_interactions': 0,
        'interactions_today': 0,
        'interactions_7_days': 0,
        'interactions_30_days': 0
    }
