from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class Post(db.Model): #store each post
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    string = db.Column(db.String(1000))  #stores the text part of the post
    
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(150))
    lastName = db.Column(db.String(150))
    userName = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    posts = db.relationship('Post')
    gender = db.Column(db.String(150))
    preference = db.Column(db.String(150))
    zodiacSign = db.Column(db.String(150))
    profilePicture = db.Column(db.String(3000))
    coverPicture = db.Column(db.String(3000)) 
    
   
    
    