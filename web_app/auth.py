from flask import Blueprint, render_template, redirect, url_for, request, flash
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user
from .user_model import User

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        if not email:
            flash('Email is required! Try again.')
        elif not username:
            flash('Username is required! Try again.')
        elif not password:
            flash('Password is required! Try again.')
        else:
            user = User.query.filter_by(username=username).first()

            if not user or not check_password_hash(user.password, password):
                flash('You have either entered wrong username or password. Try again.')
                return redirect(url_for('auth.login'))
            login_user(user, remember=remember)
            return redirect(url_for('main.home_page'))
    return render_template('login.html')

@auth.route('/signup/<gender>/<preference>', methods=['GET', 'POST'])
def sign_up(gender, preference):
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')

        if not email:
            flash('Email is required! Try again.')
        elif not username:
            flash('Username is required! Try again.')
        elif not password:
            flash('Password is required! Try again.')
        else:
            user = User.query.filter_by(username=username).first()

            if user:
                flash('Username already exists. Try loging in.')
                return redirect(url_for('auth.login'))

            new_user = User(email=email, username=username, password=generate_password_hash(password, method='sha256'))

            db.session.add(new_user)
            db.session.commit()
            flash(f'Successfully registered {new_user.username}.')
            return redirect(url_for('auth.login'))
    return render_template('sign_up.html')

@auth.route('/logout')
def logout():
    return 'Logout'

