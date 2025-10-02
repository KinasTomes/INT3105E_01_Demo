from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from app.models import db
from app.blueprints.main import main_bp
from app.blueprints.books import books_bp
from app.blueprints.members import members_bp
from app.blueprints.loans import loans_bp
from app.blueprints.api import api_bp

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'dev-secret'

    db.init_app(app)

    with app.app_context():
        db.create_all()

    app.register_blueprint(main_bp)
    app.register_blueprint(books_bp, url_prefix='/books')
    app.register_blueprint(members_bp, url_prefix='/members')
    app.register_blueprint(loans_bp, url_prefix='/loans')
    app.register_blueprint(api_bp, url_prefix='/api')

    return app