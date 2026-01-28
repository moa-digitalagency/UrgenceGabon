"""
UrgenceGabon.com
By MOA Digital Agency LLC
Developed by: Aisance KALONJI
Contact: moa@myoneart.com
Website: www.myoneart.com

extensions.py - Extensions Flask
Ce fichier initialise les extensions Flask partagées: SQLAlchemy pour la base de données,
LoginManager pour l'authentification et CSRFProtect pour la sécurité.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'admin.admin_login'
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address, storage_uri="memory://")
