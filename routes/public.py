"""
UrgenceGabon.com
By MOA Digital Agency LLC
Developed by: Aisance KALONJI
Contact: moa@myoneart.com
Website: www.myoneart.com

routes/public.py - Routes publiques
Ce fichier définit les routes accessibles au public: page d'accueil, API pharmacies,
soumissions de localisation/info, suggestions, popups et publicités.
"""

from flask import Blueprint, render_template, jsonify, request, abort, Response, url_for
from markupsafe import Markup
from services.pharmacy_service import PharmacyService
from models.submission import LocationSubmission, InfoSubmission, PharmacyView, Suggestion, PharmacyProposal, PageInteraction, UserAction
from models.pharmacy import Pharmacy
from models.emergency_contact import EmergencyContact
from models.site_settings import PopupMessage, SiteSettings
from models.advertisement import Advertisement, AdSettings
from extensions import db, csrf, limiter
from datetime import datetime
from sqlalchemy import func

public_bp = Blueprint('public', __name__)


def get_json_or_400():
    """Safely get JSON from request, return 400 if invalid."""
    try:
        data = request.get_json(force=False, silent=True)
        if data is None:
            abort(400, description='Invalid JSON data')
        return data
    except Exception:
        abort(400, description='Invalid JSON data')


def is_admin_path(url_path):
    """Check if URL path is an admin page (blocks /admin and all its subpages)."""
    path = url_path.lower()
    return path.startswith('/admin/') or path == '/admin'


def generate_sitemap():
    """
    Generate comprehensive dynamic sitemap for SEO.
    Includes:
    - Homepage with all tabs (pharmacies, garde, carte, urgence, suggestions)
    - Individual pharmacy anchors
    - City-specific views
    Excludes all admin pages.
    """
    try:
        base_url = request.url_root.rstrip('/')
        now = datetime.utcnow()
        
        sitemap_entries = []
        
        # Homepage - highest priority
        sitemap_entries.append({
            'url': base_url + '/',
            'lastmod': now.strftime('%Y-%m-%d'),
            'priority': '1.0',
            'changefreq': 'daily'
        })
        
        # Main tab sections (using hash anchors for SPA-like navigation)
        tabs = [
            {'path': '/#toutes-pharmacies', 'priority': '0.9', 'changefreq': 'daily'},
            {'path': '/#pharmacies-garde', 'priority': '0.95', 'changefreq': 'daily'},
            {'path': '/#carte', 'priority': '0.7', 'changefreq': 'weekly'},
            {'path': '/#numeros-urgence', 'priority': '0.8', 'changefreq': 'monthly'},
            {'path': '/#suggestions', 'priority': '0.5', 'changefreq': 'monthly'},
        ]
        
        for tab in tabs:
            sitemap_entries.append({
                'url': base_url + tab['path'],
                'lastmod': now.strftime('%Y-%m-%d'),
                'priority': tab['priority'],
                'changefreq': tab['changefreq']
            })
        
        # City-specific filters
        try:
            cities = db.session.query(Pharmacy.ville).distinct().all()
            for (city,) in cities:
                if city:
                    sitemap_entries.append({
                        'url': base_url + f'/?ville={city}',
                        'lastmod': now.strftime('%Y-%m-%d'),
                        'priority': '0.7',
                        'changefreq': 'weekly'
                    })
        except Exception:
            pass
        
        # Individual pharmacies
        try:
            pharmacies = Pharmacy.query.all()
            for pharmacy in pharmacies:
                lastmod = pharmacy.updated_at or pharmacy.created_at or now
                lastmod_str = lastmod.strftime('%Y-%m-%d') if hasattr(lastmod, 'strftime') else str(lastmod)[:10]
                
                # Pharmacy anchor
                sitemap_entries.append({
                    'url': base_url + f'/#pharmacy-{pharmacy.id}',
                    'lastmod': lastmod_str,
                    'priority': '0.6',
                    'changefreq': 'weekly'
                })
        except Exception:
            pass
        
        # Generate XML
        xml_lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
            '        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"',
            '        xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9',
            '        http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">'
        ]
        
        for entry in sitemap_entries:
            xml_lines.append('  <url>')
            xml_lines.append(f'    <loc>{entry["url"]}</loc>')
            xml_lines.append(f'    <lastmod>{entry["lastmod"]}</lastmod>')
            xml_lines.append(f'    <changefreq>{entry["changefreq"]}</changefreq>')
            xml_lines.append(f'    <priority>{entry["priority"]}</priority>')
            xml_lines.append('  </url>')
        
        xml_lines.append('</urlset>')
        
        return '\n'.join(xml_lines)
    except Exception:
        return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"></urlset>'


def generate_robots_txt():
    """
    Generate dynamic robots.txt with comprehensive crawler rules.
    - Allows all major search engines and AI crawlers
    - Blocks admin pages and sensitive endpoints
    - References sitemap for indexing
    """
    try:
        base_url = request.url_root.rstrip('/')
        sitemap_url = base_url + '/sitemap.xml'
        
        robots_lines = [
            '# ============================================',
            '# UrgenceGabon.com - Robots.txt Configuration',
            '# Annuaire des pharmacies au Gabon',
            '# ============================================',
            '',
            '# -----------------------------------------',
            '# SEARCH ENGINE CRAWLERS (Allowed)',
            '# -----------------------------------------',
            'User-agent: Googlebot',
            'Allow: /',
            'Disallow: /admin',
            'Disallow: /admin/',
            '',
            'User-agent: Bingbot',
            'Allow: /',
            'Disallow: /admin',
            'Disallow: /admin/',
            '',
            'User-agent: Yandex',
            'Allow: /',
            'Disallow: /admin',
            'Disallow: /admin/',
            '',
            'User-agent: Baiduspider',
            'Allow: /',
            'Disallow: /admin',
            'Disallow: /admin/',
            '',
            'User-agent: DuckDuckBot',
            'Allow: /',
            'Disallow: /admin',
            'Disallow: /admin/',
            '',
            '# -----------------------------------------',
            '# AI CRAWLERS (Allowed for training/search)',
            '# -----------------------------------------',
            '# OpenAI / ChatGPT',
            'User-agent: GPTBot',
            'Allow: /',
            'Disallow: /admin',
            'Disallow: /admin/',
            '',
            'User-agent: ChatGPT-User',
            'Allow: /',
            'Disallow: /admin',
            'Disallow: /admin/',
            '',
            '# Anthropic / Claude',
            'User-agent: anthropic-ai',
            'Allow: /',
            'Disallow: /admin',
            'Disallow: /admin/',
            '',
            'User-agent: Claude-Web',
            'Allow: /',
            'Disallow: /admin',
            'Disallow: /admin/',
            '',
            '# Google AI (Bard/Gemini)',
            'User-agent: Google-Extended',
            'Allow: /',
            'Disallow: /admin',
            'Disallow: /admin/',
            '',
            '# Perplexity AI',
            'User-agent: PerplexityBot',
            'Allow: /',
            'Disallow: /admin',
            'Disallow: /admin/',
            '',
            '# Cohere AI',
            'User-agent: cohere-ai',
            'Allow: /',
            'Disallow: /admin',
            'Disallow: /admin/',
            '',
            '# Meta AI',
            'User-agent: FacebookBot',
            'Allow: /',
            'Disallow: /admin',
            'Disallow: /admin/',
            '',
            'User-agent: Meta-ExternalAgent',
            'Allow: /',
            'Disallow: /admin',
            'Disallow: /admin/',
            '',
            '# -----------------------------------------',
            '# DEFAULT RULES (All other bots)',
            '# -----------------------------------------',
            'User-agent: *',
            'Allow: /',
            '',
            '# Block admin panel and all subpages',
            'Disallow: /admin',
            'Disallow: /admin/',
            '',
            '# Block API endpoints (internal use only)',
            'Disallow: /api/',
            '',
            '# Block form submission endpoints',
            'Disallow: /submit-location',
            'Disallow: /submit-info',
            'Disallow: /submit-suggestion',
            'Disallow: /propose-pharmacy',
            'Disallow: /track-',
            '',
            '# -----------------------------------------',
            '# BLOCKED BOTS (Scrapers/Bad actors)',
            '# -----------------------------------------',
            'User-agent: AhrefsBot',
            'Disallow: /',
            '',
            'User-agent: SemrushBot',
            'Disallow: /',
            '',
            'User-agent: MJ12bot',
            'Disallow: /',
            '',
            'User-agent: DotBot',
            'Disallow: /',
            '',
            '# -----------------------------------------',
            '# CRAWL SETTINGS',
            '# -----------------------------------------',
            'Crawl-delay: 1',
            '',
            '# Sitemap location',
            f'Sitemap: {sitemap_url}'
        ]
        
        return '\n'.join(robots_lines)
    except Exception:
        return 'User-agent: *\nAllow: /\nDisallow: /admin/\nDisallow: /admin'


@public_bp.route('/sitemap.xml')
def sitemap():
    """Serve dynamic sitemap XML (excluding /admin)."""
    sitemap_xml = generate_sitemap()
    return Response(sitemap_xml, mimetype='application/xml')


@public_bp.route('/robots.txt')
def robots():
    """Serve dynamic robots.txt (excluding /admin)."""
    robots_txt = generate_robots_txt()
    return Response(robots_txt, mimetype='text/plain')


@public_bp.route('/manifest.json')
def manifest():
    """Serve dynamic manifest.json based on PWA settings."""
    pwa_enabled = SiteSettings.get('pwa_enabled') == 'true'

    if not pwa_enabled:
        return jsonify({}), 404

    mode = SiteSettings.get('pwa_mode', 'default')

    # Default values
    name = SiteSettings.get('site_name', 'UrgenceGabon.com')
    short_name = name

    # Icons list
    icons = []

    # Handle Custom Mode
    if mode == 'custom':
        custom_name = SiteSettings.get('pwa_custom_name')
        if custom_name:
            name = custom_name
            short_name = custom_name

        custom_icon = SiteSettings.get('pwa_custom_icon_filename')
        if custom_icon:
            # We assume the uploaded icon is high res
            icons.append({
                "src": f"/static/uploads/settings/{custom_icon}",
                "sizes": "192x192 512x512",
                "type": "image/png"
            })

    # Fallback/Default Icons if no custom icon or mode is default
    if not icons:
        # Try to use site logo if available for larger icon
        logo = SiteSettings.get('site_logo_filename')
        if logo:
            icons.append({
                "src": f"/static/uploads/settings/{logo}",
                "sizes": "192x192 512x512",
                "type": "image/png"
            })

        # Use favicon
        favicon = SiteSettings.get('site_favicon_filename')
        if favicon:
             icons.append({
                "src": f"/static/uploads/settings/{favicon}",
                "sizes": "64x64 32x32",
                "type": "image/png"
            })
        else:
             icons.append({
                "src": "/static/favicon.svg",
                "sizes": "any",
                "type": "image/svg+xml"
            })

    # Basic manifest structure
    manifest_data = {
        "name": name,
        "short_name": short_name,
        "start_url": "/",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": "#059669", # Primary-600
        "icons": icons,
        "orientation": "portrait-primary"
    }

    return jsonify(manifest_data)


@public_bp.route('/')
def index():
    villes = PharmacyService.get_distinct_cities()
    total_pharmacies = Pharmacy.query.count()
    
    national_contacts = EmergencyContact.query.filter_by(is_national=True, is_active=True).order_by(EmergencyContact.ordering).all()
    city_contacts = EmergencyContact.query.filter_by(is_national=False, is_active=True).order_by(EmergencyContact.ordering).all()
    
    contacts_by_city = {}
    for contact in city_contacts:
        if contact.ville not in contacts_by_city:
            contacts_by_city[contact.ville] = []
        contacts_by_city[contact.ville].append(contact)
    
    header_code = SiteSettings.get('header_code', '')
    footer_code = SiteSettings.get('footer_code', '')
    favicon_url = SiteSettings.get_favicon_url()
    logo_url = SiteSettings.get_logo_url()
    og_image_url = SiteSettings.get_og_image_url()
    site_name = SiteSettings.get('site_name', 'UrgenceGabon.com')
    og_title = SiteSettings.get('og_title', 'UrgenceGabon.com - Trouvez votre pharmacie')
    og_description = SiteSettings.get('og_description', 'Annuaire complet des pharmacies au Gabon')
    og_type = SiteSettings.get('og_type', 'website')
    og_locale = SiteSettings.get('og_locale', 'fr_FR')
    meta_description = SiteSettings.get('meta_description', og_description)
    meta_keywords = SiteSettings.get('meta_keywords', 'pharmacie gabon, pharmacie garde, urgence gabon')
    meta_author = SiteSettings.get('meta_author', 'MOA Digital Agency LLC')
    twitter_card = SiteSettings.get('twitter_card', 'summary_large_image')
    twitter_handle = SiteSettings.get('twitter_handle', '')
    twitter_title = SiteSettings.get('twitter_title', og_title)
    twitter_description = SiteSettings.get('twitter_description', og_description)
    canonical_url = SiteSettings.get('canonical_url', '')
    google_site_verification = SiteSettings.get('google_site_verification', '')
    structured_data = SiteSettings.get('structured_data', '')
    
    pwa_enabled = SiteSettings.get('pwa_enabled') == 'true'

    return render_template('index.html', 
                          villes=villes, 
                          total_pharmacies=total_pharmacies,
                          national_contacts=national_contacts,
                          contacts_by_city=contacts_by_city,
                          header_code=Markup(header_code) if header_code else '',
                          footer_code=Markup(footer_code) if footer_code else '',
                          favicon_url=favicon_url,
                          logo_url=logo_url,
                          og_image_url=og_image_url,
                          site_name=site_name,
                          og_title=og_title,
                          og_description=og_description,
                          og_type=og_type,
                          og_locale=og_locale,
                          meta_description=meta_description,
                          meta_keywords=meta_keywords,
                          meta_author=meta_author,
                          twitter_card=twitter_card,
                          twitter_handle=twitter_handle,
                          twitter_title=twitter_title,
                          twitter_description=twitter_description,
                          canonical_url=canonical_url,
                          google_site_verification=google_site_verification,
                          structured_data=Markup(structured_data) if structured_data else '',
                          pwa_enabled=pwa_enabled)


@public_bp.route('/api/pharmacies')
def get_pharmacies():
    search = request.args.get('search', '').lower()
    ville = request.args.get('ville', '')
    garde_only = request.args.get('garde', '') == 'true'
    gare_only = request.args.get('gare', '') == 'true'
    
    pharmacies = PharmacyService.get_all_pharmacies(
        search=search,
        ville=ville,
        garde_only=garde_only,
        gare_only=gare_only
    )
    
    return jsonify([p.to_dict() for p in pharmacies])




@public_bp.route('/api/pharmacy/<int:id>/view', methods=['POST'])
@csrf.exempt
def record_view(id):
    pharmacy = Pharmacy.query.get_or_404(id)
    try:
        view = PharmacyView(pharmacy_id=pharmacy.id)
        db.session.add(view)
        db.session.commit()
        return jsonify({'success': True})
    except Exception:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Erreur lors de l\'enregistrement'}), 500


@public_bp.route('/api/pharmacy/<int:id>/submit-location', methods=['POST'])
@csrf.exempt
@limiter.limit("20 per hour")
def submit_location(id):
    pharmacy = Pharmacy.query.get_or_404(id)
    data = get_json_or_400()
    
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    
    if latitude is None or longitude is None:
        return jsonify({'success': False, 'error': 'Coordonnées manquantes'}), 400
    
    try:
        submission = LocationSubmission(
            pharmacy_id=pharmacy.id,
            latitude=float(latitude),
            longitude=float(longitude),
            submitted_by_name=data.get('name', ''),
            submitted_by_phone=data.get('phone', ''),
            comment=data.get('comment', '')
        )
        db.session.add(submission)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Localisation soumise avec succès'})
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Coordonnées invalides'}), 400
    except Exception:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Erreur lors de la soumission'}), 500


@public_bp.route('/api/pharmacy/<int:id>/submit-info', methods=['POST'])
@csrf.exempt
@limiter.limit("20 per hour")
def submit_info(id):
    pharmacy = Pharmacy.query.get_or_404(id)
    data = get_json_or_400()
    
    field_name = data.get('field_name')
    proposed_value = data.get('proposed_value')
    
    if not field_name or not proposed_value:
        return jsonify({'success': False, 'error': 'Informations manquantes'}), 400
    
    try:
        current_value = getattr(pharmacy, field_name, '') or ''
        
        submission = InfoSubmission(
            pharmacy_id=pharmacy.id,
            field_name=field_name,
            current_value=str(current_value),
            proposed_value=proposed_value,
            submitted_by_name=data.get('name', ''),
            submitted_by_phone=data.get('phone', ''),
            comment=data.get('comment', '')
        )
        db.session.add(submission)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Information soumise avec succès'})
    except Exception:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Erreur lors de la soumission'}), 500


@public_bp.route('/api/suggestions', methods=['POST'])
@csrf.exempt
@limiter.limit("100 per hour")
def submit_suggestion():  # Rate limited: 100/hour
    data = get_json_or_400()
    
    category = data.get('category')
    subject = data.get('subject')
    message = data.get('message')
    
    if not category or not subject or not message:
        return jsonify({'success': False, 'error': 'Veuillez remplir tous les champs obligatoires'}), 400
    
    try:
        suggestion = Suggestion(
            category=category,
            subject=subject,
            message=message,
            submitted_by_name=data.get('name', ''),
            submitted_by_email=data.get('email', ''),
            submitted_by_phone=data.get('phone', '')
        )
        db.session.add(suggestion)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Suggestion envoyée avec succès'})
    except Exception:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Erreur lors de l\'envoi'}), 500


@public_bp.route('/api/pharmacy-proposal', methods=['POST'])
@csrf.exempt
@limiter.limit("10 per hour")
def submit_pharmacy_proposal():
    data = get_json_or_400()
    
    nom = data.get('nom')
    ville = data.get('ville')
    
    if not nom or not ville:
        return jsonify({'success': False, 'error': 'Le nom et la ville sont obligatoires'}), 400
    
    try:
        proposal = PharmacyProposal(
            nom=nom,
            ville=ville,
            quartier=data.get('quartier', ''),
            telephone=data.get('telephone', ''),
            bp=data.get('bp', ''),
            horaires=data.get('horaires', ''),
            services=data.get('services', ''),
            proprietaire=data.get('proprietaire', ''),
            type_etablissement=data.get('type_etablissement', 'pharmacie_generale'),
            categorie_emplacement=data.get('categorie_emplacement', 'standard'),
            is_garde=data.get('is_garde', False),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            submitted_by_name=data.get('name', ''),
            submitted_by_email=data.get('email', ''),
            submitted_by_phone=data.get('phone', ''),
            comment=data.get('comment', '')
        )
        db.session.add(proposal)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Proposition de pharmacie envoyée avec succès'})
    except Exception:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Erreur lors de l\'envoi'}), 500


@public_bp.route('/api/popups')
def get_active_popups():
    popups = PopupMessage.query.filter_by(is_active=True).order_by(PopupMessage.ordering).all()
    return jsonify([p.to_dict() for p in popups])


@public_bp.route('/api/ads/settings')
def get_ad_settings():
    settings = AdSettings.get_settings()
    return jsonify(settings.to_dict())


@public_bp.route('/api/ads/random')
def get_random_ad():
    import random
    from datetime import datetime
    
    now = datetime.utcnow()
    active_ads = Advertisement.query.filter(
        Advertisement.is_active == True,
        db.or_(Advertisement.start_date == None, Advertisement.start_date <= now),
        db.or_(Advertisement.end_date == None, Advertisement.end_date >= now)
    ).all()
    
    if not active_ads:
        return jsonify(None)
    
    weighted_ads = []
    for ad in active_ads:
        weight = max(1, ad.priority + 1)
        weighted_ads.extend([ad] * weight)
    
    selected_ad = random.choice(weighted_ads)
    
    settings = AdSettings.get_settings()
    skip_delay = selected_ad.skip_delay if selected_ad.skip_delay > 0 else settings.default_skip_delay
    
    ad_data = selected_ad.to_dict()
    ad_data['skip_delay'] = skip_delay
    
    return jsonify(ad_data)


@public_bp.route('/api/ads/<int:id>/view', methods=['POST'])
@csrf.exempt
def record_ad_view(id):
    ad = Advertisement.query.get_or_404(id)
    try:
        ad.view_count = (ad.view_count or 0) + 1
        db.session.commit()
        return jsonify({'success': True})
    except Exception:
        db.session.rollback()
        return jsonify({'success': False}), 500


@public_bp.route('/api/ads/<int:id>/click', methods=['POST'])
@csrf.exempt
def record_ad_click(id):
    ad = Advertisement.query.get_or_404(id)
    try:
        ad.click_count = (ad.click_count or 0) + 1
        db.session.commit()
        return jsonify({'success': True})
    except Exception:
        db.session.rollback()
        return jsonify({'success': False}), 500


@public_bp.route('/api/emergency-contacts')
def get_emergency_contacts():
    """Get all active emergency contacts, sorted by national first, then by city."""
    national_contacts = EmergencyContact.query.filter_by(is_national=True, is_active=True).order_by(EmergencyContact.ordering).all()
    city_contacts = EmergencyContact.query.filter_by(is_national=False, is_active=True).order_by(EmergencyContact.ordering).all()
    
    contacts_data = {
        'national': [c.to_dict() for c in national_contacts],
        'by_city': {}
    }
    
    for contact in city_contacts:
        ville = contact.ville or 'Unknown'
        if ville not in contacts_data['by_city']:
            contacts_data['by_city'][ville] = []
        contacts_data['by_city'][ville].append(contact.to_dict())
    
    return jsonify(contacts_data)


@public_bp.route('/api/track', methods=['POST'])
@csrf.exempt
def track_interaction():
    """Track page interactions, searches, filters, and tab switches."""
    data = get_json_or_400()
    
    try:
        interaction = PageInteraction(
            interaction_type=data.get('type', 'page_view'),
            page=data.get('page', ''),
            search_query=data.get('search_query'),
            filter_value=data.get('filter_value'),
            tab_name=data.get('tab_name')
        )
        db.session.add(interaction)
        db.session.commit()
        return jsonify({'success': True})
    except Exception:
        db.session.rollback()
        return jsonify({'success': False}), 500


@public_bp.route('/api/action/<action_type>', methods=['POST'])
@csrf.exempt
def track_action(action_type):
    """Track user actions like button clicks."""
    data = get_json_or_400()
    
    try:
        action = UserAction(
            action_type=action_type,
            pharmacy_id=data.get('pharmacy_id'),
            ad_id=data.get('ad_id')
        )
        db.session.add(action)
        db.session.commit()
        return jsonify({'success': True})
    except Exception:
        db.session.rollback()
        return jsonify({'success': False}), 500
