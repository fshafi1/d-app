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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    firstName = db.Column(db.String(150))
    lastName = db.Column(db.String(150))
    userName = db.Column(db.String(150))
    password = db.Column(db.String(150))
    gender = db.Column(db.String(150))
    preference = db.Column(db.String(150))
    age = db.Column(db.Integer, nullable=False)
    bio = db.Column(db.String(500), nullable=True)
    email = db.Column(db.String(150), unique=True)
    location = db.Column(db.String(150), unique=False)
    interests = db.Column(db.String(500), nullable=True)
    zodiacSign = db.Column(db.String(150))
    profilePicture = db.Column(db.String(3000))
    coverPicture = db.Column(db.String(3000)) 
    posts = db.relationship('Post')
    liked_disliked_profiles = db.relationship('LikedDislikedProfile', back_populates='user', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'first_name': self.firstName,
            'last_name': self.lastName,
            'username': self.userName,
            'password': self.password,
            'gender': self.gender,
            'preference': self.preference,
            'age': self.age,
            'bio': self.bio,
            'email': self.email,
            'location': self.location,
            'zodiac_sign': self.zodiacSign,
            'interests': self.interests,
            'profilePicture': self.profilePicture,
            'coverPicture': self.coverPicture
            #'liked_disliked_profiles': [p.to_dict() for p in self.liked_disliked_profiles],
        }
        
        
class LikedDislikedProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    profile_id = db.Column(db.Integer, nullable=False)
    liked = db.Column(db.Boolean, nullable=False) # True if liked, False if disliked
    seed = db.Column(db.Integer, nullable=True)
    user = db.relationship("User", back_populates="liked_disliked_profiles")

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'profile_id': self.profile_id,
            'liked': self.liked,
            'seed': self.seed,
            'user': self.user
        }

    
    
   
    
    
