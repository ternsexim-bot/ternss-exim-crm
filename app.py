from flask import Flask, jsonify, render_template, send_from_directory, request, redirect, url_for
import json
import os
import re
import sys
import threading
import time
import urllib.request

from leads import save_lead, send_whatsapp_alert

app = Flask(__name__)

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000

BASE_URL = os.environ.get('BASE_URL', 'https://ternsexim.com').rstrip('/')

@app.context_processor
def inject_seo():
    path = request.path.rstrip('/') or '/'
    return {'canonical_url': BASE_URL + path}


# ── Static asset routes ───────────────────────────────────────────────────────

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static', 'images'),
        'favicon.png', mimetype='image/png'
    )

@app.route('/robots.txt')
def robots():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'robots.txt', mimetype='text/plain'
    )

@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'sitemap.xml', mimetype='application/xml'
    )


# ── Page routes ───────────────────────────────────────────────────────────────

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/products')
def products():
    return render_template('products.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/hex-bolts')
def hex_bolts():
    return render_template('hex_bolts.html')

@app.route('/anchor-bolts')
def anchor_bolts():
    return render_template('anchor_bolts.html')

@app.route('/foundation-bolts')
def foundation_bolts():
    return render_template('foundation_bolts.html')

@app.route('/nuts')
def nuts():
    return render_template('nuts.html')

@app.route('/washers')
def washers():
    return render_template('washers.html')

@app.route('/threaded-rods')
def threaded_rods():
    return render_template('threaded_rods.html')

@app.route('/thank-you')
def thank_you():
    return render_template('thank_you.html')


# ── Health check ──────────────────────────────────────────────────────────────

@app.route('/health')
def health():
    return jsonify({'status': 'ok'}), 200


# ── Lead capture ──────────────────────────────────────────────────────────────

_PHONE_RE = re.compile(r'^[\d\s+\-()\+]+$')
_EMAIL_RE  = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')

def _valid_phone(phone):
    if not _PHONE_RE.match(phone):
        return False
    return 7 <= len(re.sub(r'\D', '', phone)) <= 15

_CRM_API_URL = 'https://terns-exim-api.onrender.com/leads'

def _forward_to_crm(name, phone, email, product, message, company='', country=''):
    """Forward lead to CRM API (primary persistent storage). One retry on failure."""
    payload = json.dumps({
        'name':             name,
        'phone':            phone,
        'email':            email,
        'company':          company,
        'country':          country,
        'product_interest': product,
        'message':          message,
        'source':           'Website',
        'status':           'New',
    }).encode('utf-8')

    def _attempt():
        req = urllib.request.Request(
            _CRM_API_URL,
            data=payload,
            headers={'Content-Type': 'application/json'},
            method='POST',
        )
        urllib.request.urlopen(req, timeout=10)

    try:
        _attempt()
        print(f'[CRM] Lead saved: {name}')
        return
    except Exception as exc:
        print(f'[CRM WARNING] Attempt 1 failed for "{name}": {exc}', file=sys.stderr)

    time.sleep(2)

    try:
        _attempt()
        print(f'[CRM] Lead saved on retry: {name}')
    except Exception as exc:
        print(
            f'[CRM ERROR] Retry failed for "{name}": {exc}. Lead in CSV backup.',
            file=sys.stderr,
        )

@app.route('/submit-lead', methods=['POST'])
def submit_lead():
    name    = request.form.get('name',    '').strip()
    email   = request.form.get('email',   '').strip()
    phone   = request.form.get('phone',   '').strip()
    company = request.form.get('company', '').strip()
    country = request.form.get('country', '').strip()
    product = request.form.get('product', '').strip()
    message = request.form.get('message', '').strip()

    if (not name or len(name) < 2
            or not email or not _EMAIL_RE.match(email)
            or not phone or not _valid_phone(phone)
            or not company
            or not country):
        return redirect(url_for('contact'))

    lead = save_lead(name, phone, email, product, message,
                     company=company, country=country)
    send_whatsapp_alert(lead)
    threading.Thread(
        target=_forward_to_crm,
        args=(name, phone, email, product, message),
        kwargs={'company': company, 'country': country},
        daemon=True,
    ).start()
    return redirect(url_for('thank_you'))


# ── Security headers ──────────────────────────────────────────────────────────

@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "script-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https://flagcdn.com https://ternsexim.com; "
        "connect-src 'self';"
    )
    return response


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
