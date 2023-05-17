from flask import Blueprint, render_template, url_for
from . import db

main = Blueprint('main', __name__)

@main.route('/')
def welcome_page():
    return render_template('welcome.html')

@main.route('/profile')
def profile():
    return 'Profile'

@main.route('/second-page/<gender>')
def second_page(gender):
    return render_template('second_page.html', gender=gender)

@main.route('/home/')
def home_page():
    return render_template('home_page.html')
