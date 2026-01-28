"""
UrgenceGabon.com
By MOA Digital Agency LLC
Developed by: Aisance KALONJI
Contact: moa@myoneart.com
Website: www.myoneart.com

routes/admin/auth.py - Authentification administrateur
Ce fichier gère la connexion et déconnexion des administrateurs.
"""

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models.admin import Admin
from models.activity_log import ActivityLog
from routes.admin import admin_bp
from extensions import limiter


def get_client_ip():
    return request.headers.get('X-Forwarded-For', request.remote_addr)


@admin_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute", methods=['POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.admin_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            login_user(admin)
            try:
                ActivityLog.log_auth('LOGIN', f'Connexion réussie: {username}', 
                                   ip_address=get_client_ip(), admin_id=admin.id, success=True)
            except Exception as e:
                import logging
                logging.error(f"Failed to log login activity: {e}")
            return redirect(url_for('admin.admin_dashboard'))
        
        try:
            ActivityLog.log_auth('LOGIN_FAILED', f'Tentative échouée pour: {username}', 
                               ip_address=get_client_ip(), success=False)
        except Exception as e:
            import logging
            logging.error(f"Failed to log login failure: {e}")
        flash('Identifiants incorrects', 'error')
    
    return render_template('admin/login.html')


@admin_bp.route('/logout')
@login_required
def admin_logout():
    admin_id = current_user.id
    username = current_user.username
    logout_user()
    try:
        ActivityLog.log_auth('LOGOUT', f'Déconnexion: {username}', 
                            ip_address=get_client_ip(), admin_id=admin_id, success=True)
    except Exception as e:
        import logging
        logging.error(f"Failed to log logout activity: {e}")
    return redirect(url_for('public.index'))
