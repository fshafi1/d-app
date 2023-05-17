from flask import Blueprint, render_template, request, flash, jsonify, url_for, redirect, current_app, session
from flask_login import login_required, current_user
from .models import Post, User, LikedDislikedProfile
from . import db
from flask_wtf import FlaskForm
from flask import send_from_directory
from wtforms import StringField, IntegerField, TextAreaField, PasswordField, SubmitField, SelectField, FileField, BooleanField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask_wtf.file import FileAllowed, FileRequired
from werkzeug.utils import secure_filename
from faker import Faker
#from dotenv import load_dotenv
import json
import base64
import os
import sys
import random
import openai


#load_dotenv()

openai.api_key = "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"


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

zodiac_description = {
    "Aquarius": "Life isn't always rainbows and sunshines",
    "Pisces":  "Nothing is out of my reach",
    "Aries": "The one who rules",
    "Taurus": "The one who strikes your heart",
    "Gemini": "I shine like a star",
    "Cancer": "Shooting for the moons",
    "Leo": "The one who is made of sunshine",
    "Virgo": "Based",
    "Libra": "Love me some love",
    "Scorpio": "Player",
    "Sagittarius": "I am all in for the adventure",
    "Capricorn": "I am popin"
}

#source for zodiac one liner https://www.yourtango.com/2017304032/perfect-description-your-zodiac-sign-one-sentence


views = Blueprint('views', __name__)

class QuizForm(FlaskForm):
    zodiac_sign = SelectField('Zodiac Sign', choices=[('all', 'All'), ('Aries', 'Aries'), ('Taurus', 'Taurus'), ('Gemini', 'Gemini'), ('Cancer', 'Cancer'), ('Leo', 'Leo'), 
    ('Virgo', 'Virgo'), ('Libra', 'Libra'), ('Scorpio', 'Scorpio'),  ('Sagittarius', 'Sagittarius'), ('Capricorn', 'Capricorn'), ('Aquarius', 'Aquarius'), ('Pisces', 'Pisces')])
    gender = SelectField('Gender Preference', choices=[('male', 'Male'), ('female', 'Female'), ('non-binary', 'Non-binary'), ('all', 'All')])
    min_age = IntegerField('Minimum Age', validators=[DataRequired()], default=18)
    max_age = IntegerField('Maximum Age', validators=[DataRequired()], default=18)
    submit = SubmitField('Find Matches')

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
    
    return render_template('home_page.html', user=current_user, accounts=matches)

@login_required
@views.route('/album', methods=['GET', 'POST'])
def album_page():
    image_folder = 'website/static/album_images'
    image_files = [f for f in os.listdir(image_folder) if f.endswith(('.jpg', '.jpeg', '.png', '.gif'))]
    # Read image files and convert them to base64
    image_data = []
    for image in image_files:
        with open(os.path.join(image_folder, image), 'rb') as f:
            encoded_image = base64.b64encode(f.read()).decode('utf-8')
            image_data.append((image, encoded_image))
    if request.method == 'POST':
        file = request.files['file']
        filename = file.filename
        file.save(os.path.join(image_folder, filename))
    return render_template('album_page.html', user=current_user, image_data=image_data)

@login_required
@views.route('/album-edit', methods=['GET', 'POST'])
def album_edit():
    image_folder = 'website/static/album_images'
    image_files = [os.path.join(image_folder, f) for f in os.listdir(image_folder) if os.path.isfile(os.path.join(image_folder, f))]
    return render_template('album_edit_page.html', user=current_user, image_files=image_files)

@login_required
@views.route('album/edit/<path:image_path>', methods=['POST'])
def album_delete(image_path):
    image_folder = 'website/static/album_images'
    file_path = os.path.join(image_folder, image_path)
    if os.path.exists(file_path):
        os.remove(file_path)
    return redirect(url_for('views.album_edit'))

#@views.route('/')
#def welcome_page():
#    return render_template('welcome.html')
    
@views.route('/matches', methods=['POST'])
@login_required
def matches():
    form = QuizForm(request.form)
    if form.validate():
        zodiac_sign = form.zodiac_sign.data
        gender = form.gender.data
        min_age = form.min_age.data
        max_age = form.max_age.data
        matches = find_matches(zodiac_sign, gender, min_age, max_age)

        # Store the matches in the session
        session['matches'] = [match.to_dict() for match in matches]
        session['liked_profiles'] = []
        session['disliked_profiles'] = []

        return render_template('matches.html', matches=matches)
    else:
        flash('Invalid input. Please try again.', 'error')
        return redirect(url_for('views.quiz'))
        
def find_matches(zodiac_sign, gender, min_age, max_age):
    all_profiles = User.query.all()
    matches = [profile for profile in all_profiles if (profile.zodiacSign == zodiac_sign or zodiac_sign == 'all') 
    and (profile.gender == gender or gender == 'all') and profile.age >= min_age and profile.age <= max_age]
    return matches
    
@views.route('/matches')
@login_required
def potential_matches():
    matches = session.get('matches', [])
    print("}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}", matches)
    return render_template('matches.html', matches=matches)
    
@views.route('/browse_profiles')
@login_required
def browse_profiles():
    profiles = User.query.all()  # Query all the existing users and show all of them
    return render_template('browse_profiles.html', profiles=profiles)

@views.route('/view_profile', methods=['POST'])
@login_required
def view_profile():
    profile_id = request.form.get('profile_id')
    profiles = User.query.all()
    profile = next((profile for profile in profiles if str(profile.user_id) == profile_id), None)
    return render_template('view_profile.html', profile=profile)

    
@views.route('/quiz')
@login_required
def quiz():
    form = QuizForm()
    return render_template('quiz.html', form=form)
    
@views.route('/like_profile', methods=['POST'])
@login_required
def like_profile():
    liked_user_id = request.form.get('liked_user_id')
    
    profile_liked = None
    for liked_user in session.get('matches', []):
        if liked_user['user_id'] == int(liked_user_id):
            profile_liked = liked_user
            break
    if 'liked_profiles' not in session:
        session['liked_profiles'] = []
    session['liked_profiles'].append(profile_liked)
    #print("TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT", session['liked_profiles'])
    
    liked_profile = LikedDislikedProfile(
        user_id=current_user.id,
        profile_id=liked_user_id,
        liked=True
    )
    db.session.add(liked_profile)
    db.session.commit()

    # Remove the liked profile from the list of potential matches
    if 'matches' in session:
        session['matches'] = [profile for profile in session.get('matches', []) if profile['user_id'] != int(liked_user_id)]
        
        

    flash("Profile liked!", "success")
    return redirect(url_for('views.liked_profiles'))


@views.route('/dislike_profile', methods=['POST'])
@login_required
def dislike_profile():
    disliked_user_id = request.form.get('disliked_user_id')
    #print("DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD", disliked_user_id)
    profile_disliked = None
    for disliked_user in session.get('matches', []):
        if disliked_user['user_id'] == int(disliked_user_id):
            profile_disliked = disliked_user
            break
    if 'disliked_profiles' not in session:
        session['disliked_profiles'] = []
    session['disliked_profiles'].append(profile_disliked)
    
    disliked_profile = LikedDislikedProfile(
        user_id=current_user.id,
        profile_id=disliked_user_id,
        liked=False
    )
    db.session.add(disliked_profile)
    db.session.commit()

    # Remove the disliked profile from the list of potential matches
    if 'matches' in session:
        session['matches'] = [profile for profile in session.get('matches', []) if profile['user_id'] != int(disliked_user_id)]
        

    flash("Profile disliked!", "success")
    return redirect(url_for('views.disliked_profiles'))
    
@views.route('/liked_profiles')
@login_required
def liked_profiles():
    liked_profiles = get_liked_profiles() # function to get the liked profiles from the session
    #print("YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY", liked_profiles[0].get("first_name"))
    return render_template('liked_profiles.html', liked_profiles=liked_profiles)

@views.route('/disliked_profiles')
@login_required
def disliked_profiles():
    disliked_profiles = get_disliked_profiles() # function to get the disliked profiles from the session
    return render_template('disliked_profiles.html', disliked_profiles=disliked_profiles)
    
def get_liked_profiles():
    if 'liked_profiles' in session:
        return [lp_dict for lp_dict in session['liked_profiles']]
    else:
        return []

def get_disliked_profiles():
    if 'disliked_profiles' in session:
        return [dp_dict for dp_dict in session['disliked_profiles']]
    else:
        return []
        
def get_profile_by_user_id(user_id):
    return Profile.query.filter_by(user_id=user_id).first()
    
@views.route('/liked_disliked_profiles')
@login_required
def liked_disliked_profiles():
    count = 0
    j = 0
    liked_profiles = LikedDislikedProfile.query.filter_by(user_id=current_user.id, liked=True).all()
    for i in liked_profiles:
    	count+=1
    	
    #print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$", count)
    for j in liked_profiles:
    	print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", j.to_dict())
    	
    
    disliked_profiles = LikedDislikedProfile.query.filter_by(user_id=current_user.id, liked=False).all()
    #print("BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB", disliked_profiles[3].to_dict())
    return render_template('liked_disliked_profiles.html', liked_profiles=liked_profiles, disliked_profiles=disliked_profiles)
    
# CHATBOT
def generate_chatbot_response(prompt, max_tokens=50):
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=max_tokens,
        n=1,
        stop=None,
        temperature=0.8,
    )
    message = response.choices[0].text.strip()
    return message

@views.route('/chatbot', methods=['GET', 'POST'])
@login_required
def chatbot():
    user_profile = None
    chatbot_response = None
    chat_histories = session.get('chat_histories', {})
    profile_id = request.args.get('profile_id', None) if request.method == 'GET' else request.form.get('profile_id', None)
    #print("MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM", profile_id)
    if not profile_id:
        flash('Profile ID not found.', 'error')
        return redirect(url_for('views.matches'))

    for liked_user in session['liked_profiles']:
        if liked_user['user_id'] == int(profile_id):
            user_profile = liked_user
            break

    if not user_profile:
        flash('Profile not found.', 'error')
        return redirect(url_for('views.matches'))

    chat_history = chat_histories.get(str(profile_id), [])
        
    if request.method == 'POST':
        profile_id = request.form.get('profile_id', None)       
        user_message = request.form.get('message')
        location = request.form.get('location')
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~", location)
        if location:
            location_data = json.loads(location)
            lat = location_data.get('lat')
            lng = location_data.get('lng')
            print("///////////////////////////////////////////////////////", lng)
            user_message = f"Meeting location: {lat}, {lng}. View on Google Maps: https://www.google.com/maps/?q={lat},{lng}"
        if user_message:
            chatbot_response = generate_chatbot_response(user_message)
            chat_history.append({'message': user_message, 'response': chatbot_response})
            chat_histories[str(profile_id)] = chat_history
            session['chat_histories'] = chat_histories
        for liked_user in session['liked_profiles']:
           if liked_user['user_id'] == int(profile_id):
              user_profile = liked_user
              break
           if not user_profile:
              flash('Profile not found.', 'error')
              return redirect(url_for('views.matches'))
    return render_template('chatbot.html', user=user_profile, chat_history=chat_history)
    
@views.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(main.config['UPLOAD_FOLDER'], filename)

# Profile Page
@views.route('/profile/<int:user_id>', methods=['GET', 'POST'])
#@login_required #REMOVED FOR TESTING
def profile(user_id):
    user_profile = User.query.get(user_id)  # get current user

    if user_profile is None:
        flash('Please create your profile first.', 'warning')
        return redirect(url_for('views.signup'))
    
    return render_template('profile_page.html', user_profile=user_profile)

# Profile Edit
@views.route('/profile_edit', methods=['GET', 'POST'])
def profile_edit():
    if request.method == 'POST':
         pass
    return render_template('profile_edit.html', user=current_user)

# Payment Method
@views.route('/payment', methods=['GET', 'POST'])
def payment():
    return render_template('payment.html')
