from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .db_session import db
from datetime import datetime


class Password_inkognito:
    def encrypt_password(self, password):
        return generate_password_hash(password)

    def verify_password(self, hashed_password, input_password):
        return check_password_hash(hashed_password, input_password)


pw_secure = Password_inkognito()

names_cache = {}


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(200), nullable=False)


class List(db.Model):
    __tablename__ = 'list'

    id = db.Column(db.Integer, primary_key=True)
    math = db.Column(db.Integer, default=0)
    russian = db.Column(db.Integer, default=0)
    physic = db.Column(db.Integer, default=0)
    inf = db.Column(db.Integer, default=0)
    summ = db.Column(db.Integer, default=0)
    achievements = db.Column(db.Integer, default=0)
    consent = db.Column(db.Boolean, default=False)


class Programs(db.Model):
    __tablename__ = 'programs'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    budget = db.Column(db.Integer)


class Applications(db.Model):
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    applicants_id = db.Column(db.Integer, db.ForeignKey('list.id'), unique=True)
    program_id = db.Column(db.Integer, db.ForeignKey('programs.id'), unique=True)
    priority = db.Column(db.Integer)


class History(db.Model):
    __tablename__ = 'history'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.now)
    program_id = db.Column(db.Integer, db.ForeignKey('programs.id'), unique=True)
    passing_score = db.Column(db.Integer, default=0)
    is_shortage = db.Column(db.Boolean, default=False)
