from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .db_session import db



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

