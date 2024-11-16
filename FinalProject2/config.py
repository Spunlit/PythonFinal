import os
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-secret'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///lottery.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
