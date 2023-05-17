from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100))
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    #gender = db.Column(db.String(100), nullable=False)
   # preference = db.Column(db.Text(10), nullable=False)
    #name = db.Column(db.String(1000))
