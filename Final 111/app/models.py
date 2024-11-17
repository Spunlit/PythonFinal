# models.py

from . import db
import hashlib
import uuid

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(64), nullable=False)
    token = db.Column(db.String(64), unique=True, nullable=False)
    balance = db.Column(db.Float, default=0)

    def set_password(self, password):
        self.password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

    def check_password(self, password):
        return self.password_hash == hashlib.sha256(password.encode('utf-8')).hexdigest()

    @staticmethod
    def generate_token():
        return hashlib.sha256(uuid.uuid4().hex.encode('utf-8')).hexdigest()

class Ticket(db.Model):
    __tablename__ = 'ticket'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    min_win = db.Column(db.Float, nullable=False)
    max_win = db.Column(db.Float, nullable=False)

class Purchase(db.Model):
    __tablename__ = 'purchase'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)

    user = db.relationship('User', backref=db.backref('purchases', lazy=True))
    ticket = db.relationship('Ticket')


class HistoryUser(db.Model):
    __tablename__ = 'history_users'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ticket_type = db.Column(db.String(50), nullable=False)
    win_amount = db.Column(db.Float, nullable=False)
    previous_balance = db.Column(db.Float, nullable=False)
    current_balance = db.Column(db.Float, nullable=False)
    result_type = db.Column(db.String(10), nullable=False)  # "loss", "break_even", "win"
    ticket_cost = db.Column(db.Float, nullable=False)

    user = db.relationship('User', backref=db.backref('history', lazy=True))

