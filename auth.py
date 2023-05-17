from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db   ##means from __init__.py import db
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
import os
from faker import Faker
import random
import shutil

fake_user_id_counter = 100000
user_id_counter = 1
fake = Faker()


zodiac_list = {
    "Aquarius": [ "Aquarius", "Leo", "Taurus", "Gemini", "Virgo", "Libra", "Pisces"],
    "Pisces": ["Taurus", "Cancer", "Scorpio", "Sagittarius", "Capricorn", "Aquarius"],
    "Aries": ["Taurus", "Gemini", "Leo", "Libra"],
    "Taurus": ["Taurus", "Cancer", "Leo", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces", "Aries"],
    "Gemini": ["Gemini", "Aries", "Leo", "Sagittarius", "Aquarius"],
    "Cancer": ["Taurus", "Leo", "Virgo","Capricorn","Pisces"],
    "Leo": ["Leo", "Aries", "Taurus", "Gemini", "Cancer", "Sagittarius", "Aquarius"],
    "Virgo": ["Cancer", "Scorpio", "Aquarius"],
    "Libra": ["Libra", "Aries", "Capricorn", "Aquarius"],
    "Scorpio": ["Pisces", "Taurus", "Virgo", "Sagittarius", "Capricorn"],
    "Sagittarius": ["Scorpio", "Pisces", "Taurus", "Gemini", "Leo"],
    "Capricorn":["Scorpio", "Pisces", "Taurus", "Cancer", "Libra"]
}

zodiac_signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']


UPLOAD_EXTENSIONS= ['.jpg', '.jpeg', '.png', '.gif']
directory = os.getcwd()
UPLOAD_PATH = directory + '/website/static/profilePics' #gets current working directory + profilePic
SAVE_PATH = 'static/profilePics/'
auth = Blueprint('auth', __name__)

# Generate random interests
def generate_interests():
    interests_list = [
    'hiking', 'music', 'movies', 'sports', 'traveling', 'cooking', 'reading', 'gaming', 'photography', 'art',
    'dancing', 'writing', 'yoga', 'meditation', 'running', 'swimming', 'cycling', 'gardening', 'painting', 'drawing',
    'theater', 'fashion', 'crafts', 'woodworking', 'fishing', 'camping', 'rock climbing', 'skiing', 'snowboarding', 'surfing',
    'sailing', 'scuba diving', 'golf', 'tennis', 'volleyball', 'basketball', 'soccer', 'baseball', 'weightlifting', 'exercise',
    'collecting', 'blogging', 'podcasting', 'birdwatching', 'investing', 'technology', 'programming', 'wine tasting', 'brewing',
    'astrology', 'pets', 'animal welfare', 'volunteering', 'philanthropy']
    user_interests = random.sample(interests_list, random.randint(2, 6))
    return ', '.join(user_interests)

@auth.route('/')
def welcome_page():
    create_users = User.query.all() #query all users and add more dummy account if less than a certain number of accounts (500 here)
    count = len(create_users)
    
    global fake_user_id_counter
    flag = 0
    nbFakeUsers = 200
    malePath = directory + '/website/static/male-profile-pictures/'
    femalePath = directory + '/website/static/female-profile-pictures/'
    
    while flag < nbFakeUsers:
        fake_profile = {
            "user_id": int(fake_user_id_counter),
            "first_name": "",
            "last_name": fake.last_name(),
            "username": "first_name"+"123",
            "password": fake.password(),
            "gender": random.choice(['male', 'female', 'nb']),
            "preference": random.choice(['male', 'female', 'non-binary', 'all']),
            "age": random.randint(18, 65),
            "bio": fake.text(max_nb_chars=100),
            "email": fake.unique.ascii_free_email(),
            "location": fake.city(),
            "interests": generate_interests(),
            "zodiac_sign": random.choice(zodiac_signs),
            "profile_picture": ""
        }
        
        if fake_profile["gender"] == 'male':
            profile_pictures = os.listdir(malePath)
            fake_profile["profile_picture"] = 'static/male-profile-pictures/' + random.choice(profile_pictures)
            fake_profile["first_name"] = fake.first_name_male()
        if fake_profile["gender"] == 'female':
            profile_pictures = os.listdir(femalePath)
            fake_profile["profile_picture"] = 'static/female-profile-pictures/' + random.choice(profile_pictures)
            fake_profile["first_name"] = fake.first_name_female()
        if fake_profile["gender"] == 'nb':
            profile_pictures = os.listdir(directory + '/website/static/sampleProfiles/')
            fake_profile["profile_picture"] = 'static/sampleProfiles/' + random.choice(profile_pictures)
            fake_profile["first_name"] = fake.first_name()
    
        dummy_user = User(
            user_id=fake_profile["user_id"],
            firstName=fake_profile["first_name"],
            lastName=fake_profile["last_name"],
            userName=fake_profile["username"],
            password=generate_password_hash(fake_profile["password"], method='sha256'),
            gender=fake_profile["gender"],
            preference=fake_profile["preference"],
            age=fake_profile["age"],
            bio=fake_profile["bio"],
            email=fake_profile["email"],
            location=fake_profile["location"],
            interests=fake_profile["interests"],
            zodiacSign=fake_profile["zodiac_sign"], 
            profilePicture=fake_profile["profile_picture"]
        )
        db.session.add(dummy_user)
        db.session.commit()
        fake_user_id_counter=fake_user_id_counter+1
        flag=flag+1
    
    return render_template('welcome.html')

@auth.route('/about')
def about():
   return render_template('about.html')

@auth.route('/second-page/<gender>')
def second_page(gender):
    return render_template('second_page.html', gender=gender)

@auth.route('/third_page/<gender>/<preference>')
def third_page(gender, preference):
    return render_template('third_page.html', gender=gender, preference=preference)

@auth.route('/signup/<gender>/<preference>/<zodiac>', methods=['GET', 'POST'])
def sign_up(gender, preference, zodiac):
    global user_id_counter
    if request.method == 'POST':
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        username = request.form.get('username')
        email = request.form.get('email')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        uploaded_file = request.files['file']
        filename = secure_filename(uploaded_file.filename)
        zodiac = zodiac
        user_id = user_id_counter
        age = random.randint(18, 65)
       

        if password1 != password2:
            flash('passwords do not match')
        else:
            user_email = User.query.filter_by(email=email).first()
            
            if user_email:
                flash('The email is already used. Try loging in')
                return redirect(url_for('auth.sign_up')) #returns user back to signup if email is used to create account
                   
            new_user = User(user_id=user_id, firstName=firstname, lastName=lastname, gender=gender, preference=preference,
                            userName=username, email=email, password=generate_password_hash(password1, method='sha256'), 
                            zodiacSign=zodiac, age=age)
            
            db.session.add(new_user)
            db.session.commit() #creates a user in db
            flash(f'Successfully registered {new_user.userName} gender: {new_user.gender}, preference: {new_user.preference}.')
            print('succefully created account account')
            #return redirect(url_for('/')) #redirect to the login page
            
            if filename != "":
                file_ext = os.path.splitext(filename)[1]
                if file_ext not in UPLOAD_EXTENSIONS:
                    flash('unsupported file extension. need to upload another profile pic')
                        
                uploaded_file.save(os.path.join(UPLOAD_PATH, str(new_user.id)))
            
            new_user.profilePicture = SAVE_PATH + str(new_user.id)
            db.session.commit()
            
            return redirect(url_for('auth.login'))
            user_id_counter=user_id_counter+1


    return render_template('signup.html')



@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
       
        user = User.query.filter_by(email=email).first() 
        if not user: #or not check_password_hash(user_password, password):
            flash("wrong username or password")
            return redirect(url_for('auth.home'))
        else:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                flash('login in ...')
                return redirect(url_for('views.home_page')) 
            
    return render_template('login.html')
