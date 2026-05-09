from flask import Flask, request, redirect, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
import random
import string
import os

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///urls.db")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable=False)
    short_code = db.Column(db.String(10), unique=True, nullable=False)

def generate_code(length=5):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/shorten', methods=['POST'])
def shorten():
    original_url = request.form['url']

    short_code = generate_code()

    new_url = URL(
        original_url=original_url,
        short_code=short_code
    )

    db.session.add(new_url)
    db.session.commit()

    short_url = request.host_url + short_code

    return render_template(
        'index.html',
        short_url=short_url
    )

@app.route('/<short_code>')
def redirect_url(short_code):
    url = URL.query.filter_by(short_code=short_code).first()

    if url:
        return redirect(url.original_url)

    return "URL tidak ditemukan"

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy"
    })

with app.app_context():
    db.create_all()

@app.route('/api/urls')
def get_urls():
    urls = URL.query.all()

    data = []

    for url in urls:
        data.append({
            "id": url.id,
            "original_url": url.original_url,
            "short_code": url.short_code,
            "short_url": request.host_url + url.short_code
        })

    return jsonify(data)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)