from flask import Flask, request, redirect, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
import random
import string
import os

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///urls.db")

# Fix Railway PostgreSQL URL format (postgres:// → postgresql://)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable=False)
    short_code = db.Column(db.String(10), unique=True, nullable=False)
    click_count = db.Column(db.Integer, default=0)  # bonus: lacak jumlah klik

    def __repr__(self):
        return f'<URL {self.short_code} → {self.original_url}>'


def generate_code(length=6):
    """Generate kode acak unik yang belum ada di database."""
    characters = string.ascii_letters + string.digits
    while True:
        code = ''.join(random.choice(characters) for _ in range(length))
        # Pastikan kode belum dipakai
        if not URL.query.filter_by(short_code=code).first():
            return code


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/shorten', methods=['POST'])
def shorten():
    original_url = request.form.get('url', '').strip()

    # Validasi URL tidak kosong
    if not original_url:
        return render_template('index.html', error="URL tidak boleh kosong.")

    # Tambahkan http:// jika tidak ada skema
    if not original_url.startswith(('http://', 'https://')):
        original_url = 'https://' + original_url

    # Cek apakah URL ini sudah pernah disingkat
    existing = URL.query.filter_by(original_url=original_url).first()
    if existing:
        short_url = request.host_url + existing.short_code
        return render_template('index.html', short_url=short_url, original_url=original_url)

    short_code = generate_code()
    new_url = URL(original_url=original_url, short_code=short_code)
    db.session.add(new_url)
    db.session.commit()

    short_url = request.host_url + short_code
    return render_template('index.html', short_url=short_url, original_url=original_url)


@app.route('/<short_code>')
def redirect_url(short_code):
    # Hindari konflik dengan route lain seperti /health
    if short_code in ('health', 'favicon.ico', 'robots.txt'):
        return "Not found", 404

    url = URL.query.filter_by(short_code=short_code).first()
    if url:
        # Update click count
        url.click_count += 1
        db.session.commit()
        return redirect(url.original_url)

    return render_template('index.html', error=f"Short URL '/{short_code}' tidak ditemukan.")


@app.route('/health')
def health():
    """Endpoint health check untuk monitoring PaaS."""
    try:
        # Cek koneksi database
        db.session.execute(db.text('SELECT 1'))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return jsonify({
        "status": "healthy",
        "database": db_status,
        "total_urls": URL.query.count()
    })


@app.route('/api/urls')
def list_urls():
    """Endpoint tambahan: daftar semua URL yang sudah disingkat."""
    urls = URL.query.order_by(URL.id.desc()).limit(10).all()
    return jsonify({
        "urls": [
            {
                "short_code": u.short_code,
                "original_url": u.original_url,
                "click_count": u.click_count,
                "short_url": request.host_url + u.short_code
            }
            for u in urls
        ]
    })


if __name__ == '__main__':
    with app.app_context():
    db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)