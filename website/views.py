from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from .models import Post, User
from werkzeug.utils import secure_filename
from . import db
import os


UPLOAD_EXTENSIONS= ['.jpg', '.png', '.gif'] #allowed file extentions to upload
directory = os.getcwd()
UPLOAD_PATH = directory + '/website/static/profilePics' #gets current working directory + profilePic
SAVE_PATH = 'static/profilePics/'

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

zodiac_description = {
    "aquarius": "Life isn't always rainbows and sunshines",
    "pisces":  "Nothing is out of my reach",
    "aries": "The one who rules",
    "taurus": "The one who strikes your heart",
    "gemini": "I shine like a star",
    "cancer": "Shooting for the moons",
    "leo": "The one who is made of sunshine",
    "virgo": "Based",
    "libra": "love me some love",
    "scorpio": "Player",
    "sagittarius": "I am all in for the adventure",
    "capricorn": "I am popin"
}

#source for zodiac one liner https://www.yourtango.com/2017304032/perfect-description-your-zodiac-sign-one-sentence


views = Blueprint('views', __name__)

@login_required
@views.route('/home_page', methods=['GET', 'POST'])
def home_page():
    #this filter users based on gender preference 
    if current_user.preference != 'pass':
        accounts = User.query.filter_by(gender=current_user.preference)
    else:
        accounts = User.query.all()
    
    #this filters based on zodiac
    matches = []
    for account in accounts:
        if account.zodiacSign in zodiac_list[current_user.zodiacSign]:
            matches.append(account)
    
    return render_template('home_page.html', user=current_user, accounts = matches)


@views.route('/profile_edit', methods=['GET', 'POST'])
def profile_edit():
    if request.method == 'POST': 
        current_user.firstName = request.form.get('firstname') if request.form.get('firstname') else current_user.firstName
        current_user.lastName = request.form.get('lastname') if request.form.get('lastname') else current_user.lastName
        current_user.userName = request.form.get('username') if request.form.get('username') else current_user.userName
        current_user.email = request.form.get('email') if request.form.get('email') else current_user.email
        current_user.gender = request.form.get('gender') if request.form.get('gender') else current_user.gender
        current_user.preference = request.form.get('preference') if request.form.get('preference') else current_user.preference 
        uploaded_file = request.files['file'] 
        filename = secure_filename(uploaded_file.filename) if secure_filename(uploaded_file.filename) else current_user.profilePicture
        
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in UPLOAD_EXTENSIONS:
            print('File extention not supported')
        uploaded_file.save(os.path.join(UPLOAD_PATH, str(current_user.id)))
            
        current_user.profilePicture = SAVE_PATH + str(current_user.id)
        db.session.commit()
        return redirect(url_for('views.home_page')) 
    
    return render_template('profile_edit.html', user=current_user)

@views.route('/payment', methods=['GET', 'POST'])
def payment():
    return render_template('payment.html')