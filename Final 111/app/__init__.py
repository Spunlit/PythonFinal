from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()  # Инициализируем Flask-Migrate

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)  # Связываем Flask-Migrate с приложением и базой данных

    with app.app_context():
        from . import models
        db.create_all()
        initialize_tickets()

    from .views import views
    app.register_blueprint(views)

    return app

def initialize_tickets():
    from .models import Ticket
    if not Ticket.query.first():
        tickets = [
            Ticket(type="Standard", price=10, min_win=1, max_win=100),
            Ticket(type="Premium", price=100, min_win=5, max_win=1000),
            Ticket(type="VIP", price=1000, min_win=500, max_win=10000)
        ]
        db.session.bulk_save_objects(tickets)
        db.session.commit()
        print("Standard tickets added to the database")
