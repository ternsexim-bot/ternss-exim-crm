from flask import Flask, render_template, send_from_directory, request
import os

app = Flask(__name__)

# Cache static files for 1 year in production
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000

BASE_URL = os.environ.get('BASE_URL', 'https://ternsexim.com').rstrip('/')

@app.context_processor
def inject_seo():
    """Inject canonical_url into every template automatically."""
    path = request.path.rstrip('/') or '/'
    return {'canonical_url': BASE_URL + path}

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

@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    # Allow images from flagcdn for country flags
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
    app.run(debug=False)
