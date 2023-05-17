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

#from tkinter import *
#import tkinter.messagebox

zodiac_list = {
    "aquarius": [ "aquarius", "leo", "taurus", "gemini", "virgo", "libra", "pisces"],
    "pisces": ["taurus", "cancer", "scorpio", "sagittarius", "capricorn", "aquarius"],
    "aries": ["taurus", "gemini", "leo", "libra"],
    "taurus": ["taurus", "cancer", "leo", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces", "aries"],
    "gemini": ["gemini", "aries", "leo", "sagittarius", "aquarius"],
    "cancer": ["taurus", "leo", "virgo","capricorn","pisces"],
    "leo": ["leo", "aries", "taurus", "gemini", "cancer", "sagittarius", "aquarius"],
    "virgo": ["cancer", "scorpio", "aquarius"],
    "libra": ["libra", "aries", "capricorn", "aquarius"],
    "scorpio": ["pisces", "taurus", "virgo", "sagittarius", "capricorn"],
    "sagittarius": ["scorpio", "pisces", "taurus", "gemini", "leo"],
    "capricorn":["scorpio", "pisces", "taurus", "cancer", "libra"]
}

zodiac_signs = ['aries', 'taurus', 'gemini', 'cancer', 'leo', 'virgo', 'libra', 'scorpio', 'sagittarius', 'capricorn', 'aquarius', 'pisces']


UPLOAD_EXTENSIONS= ['.jpg', '.png', '.gif']
directory = os.getcwd()
UPLOAD_PATH = directory + '/website/static/profilePics' #gets current working directory + profilePic
SAVE_PATH = 'static/profilePics/'
auth = Blueprint('auth', __name__)

@auth.route('/')
def welcome_page():
    create_users = User.query.all() #query all users and add more dummy account if less thatn 200 accounts
    count = len(create_users)
 

    while count < 200:
        fake = Faker()
        malePath = directory + '/website/static/male-profile-pictures/'
        femalePath = directory + '/website/static/female-profile-pictures/'
        
        firstname = fake.first_name()
        lastname = fake.last_name()
        username = firstname + '123'
        gender = random.choice(['male', 'female', 'nb'])
        email = fake.email()
        password = fake.password()
        zodiac =  random.choice(zodiac_signs) 
        
        if gender == 'male':
            profile_pictures = os.listdir(malePath)
            profile_picture =  'static/male-profile-pictures/' + random.choice(profile_pictures)
        if gender == 'female':
            profile_pictures = os.listdir(femalePath)
            profile_picture =  'static/female-profile-pictures/' + random.choice(profile_pictures)
        if gender == 'nb':
             profile_pictures = os.listdir(directory + '/website/static/sampleProfiles/')
             profile_picture =  'static/sampleProfiles/' + random.choice(profile_pictures)
             
        preference = random.choice(['male', 'female', 'nb'])

        dummy_user = User(firstName=firstname, lastName=lastname,  userName=username, email=email,  password=generate_password_hash(password, method='sha256'),
                      gender=gender, preference=preference, zodiacSign=zodiac, 
                      profilePicture=profile_picture)
        db.session.add(dummy_user)
        db.session.commit() 
        count = count + 1
    
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

def check_password(password):
    is_valid = False
    special_characters = ['.', '!', '&', '#']

    if len(password) >= 8 and password[0].isupper() and any(char in special_characters for char in password):
        is_valid = True

    #if password[0].islower():

    return is_valid

@auth.route('/signup/<gender>/<preference>/<zodiac>', methods=['GET', 'POST'])
def sign_up(gender, preference, zodiac):
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

        # NEW.....
        if not firstname:
            flash('First name is required! Try again.')
        elif not lastname:
            flash('Last name is required! Try again.')
        elif not username:
            flash('Username is required! Try again.')
        elif not email:
            flash('Email is required! Try again.')
        elif not password1:
            flash('Password is required! Try again.')
        elif not password2:
            flash('Confirm password is required! Try again.')
        elif password1 != password2:
            flash('Passwords entered do not match. Try again.')
        elif not check_password(password1):
            flash('Your password does not meet the requirements (8 characters, 1st letter is uppercase, and 1 special character). Try again.')
        else:
            user_email = User.query.filter_by(email=email).first()

            if user_email:
                # NEW.....
                flash('The email is already used. Try loging in')
                return redirect(url_for('auth.login'))

            new_user = User(firstName=firstname, lastName=lastname, gender=gender, preference=preference,
                            userName=username, email=email,
                            password=generate_password_hash(password1, method='sha256'),
                            zodiacSign=zodiac)

            db.session.add(new_user)
            db.session.commit() #creates a user in db

            # NEW......
            flash(f'Successfully registered {new_user.userName}!')
            print('succefully created account account')

            if filename != "":
                file_ext = os.path.splitext(filename)[1]
                if file_ext not in UPLOAD_EXTENSIONS:
                    # NEW....
                    flash('You have entered an unsupported file extension. Try again.')

                uploaded_file.save(os.path.join(UPLOAD_PATH, str(new_user.id)))

            new_user.profilePicture = SAVE_PATH + str(new_user.id)
            db.session.commit()

            return redirect(url_for('auth.login'))


    return render_template('signup.html')



@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')


        # NEW...
        if not email:
            flash('Email is required! Try again.')
        elif not password:
            flash('Password is required! Try again.')
        else:

            user = User.query.filter_by(email=email).first()
            # NEW....
            if not user or not check_password_hash(user.password, password):
                flash('You have either entered wrong username or password. Try again.')
                return redirect(url_for('auth.home'))
            else:
                if check_password_hash(user.password, password):
                    login_user(user, remember=True)
                    #flash('login in ...')
                    return redirect(url_for('views.home_page')) 

    return render_template('login.html')
