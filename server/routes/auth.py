from flask import  Blueprint, render_template, redirect, url_for, request, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity

from ..models import User
from .. import db
from ..common import *
from ..decorators import api_auth_required, logout_required, api_unconfirmed_required

from ..token_generator import generate_token, confirm_token

import re

EMAIL_REGEX=r"[^@]+@[^@]+\.[^@]+"

auth = Blueprint('auth', __name__)

@auth.route('/login')
@logout_required
def login():
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
@logout_required
def login_post():
    # login code goes here
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login')) # if the user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for('main.profile'))

@auth.route('/signup')
@logout_required
def signup():
    return render_template('signup.html')

@auth.route('/signup', methods=['POST'])
@logout_required
def signup_post():
    # code to validate and add user to database goes here
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

    if user: # if a user is found, we want to redirect back to signup page so user can try again
        flash('Email address already exists')
        return redirect(url_for('auth.signup'))

    # check if the email is valid
    if not re.match(EMAIL_REGEX, email):
        flash('Invalid email')
        return redirect(url_for('auth.signup'))
    # check if the password is valid
    pw_check = password_check(password)
    if not pw_check["password_ok"]:
        if pw_check["length_error"]:
            flash("Password must have at least 8 characters")
        elif pw_check["digit_error"]:
            flash("Password must have at least 1 number")
        elif pw_check["uppercase_error"]:
            flash("Password must have at least 1 uppercase letter")
        elif pw_check["lowercase_error"]:
            flash("Password must have at least 1 lowercase letter")
        elif pw_check["symbol_error"]:
            flash("Password must have at least 1 symbol")
        return redirect(url_for('auth.signup'))

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = User(email=email, name=name, password=generate_password_hash(password, method='pbkdf2:sha512'), is_confirmed=False)
    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    # sign the user in
    login_user(new_user)

    # generate a token
    token = generate_token(new_user.email)
    # create the confirm URL
    confirm_url = url_for("auth.confirm_email", token=token, _external=True)
    # render the registration email template
    html = render_template("email_reg.html", confirm_url=confirm_url)
    subject = "Avoor: Please confirm your email"
    # send the email
    send_email(new_user.email, subject, html)

    flash("Please check your email.")
    return redirect(url_for('main.index'))

@auth.route("/confirm/<token>")
@login_required
def confirm_email(token):
    if current_user.is_confirmed:
        flash("Account already confirmed.", "success")
        return redirect(url_for("main.index"))
    email = confirm_token(token)
    user = User.query.filter_by(email=current_user.email).first_or_404()
    if user.email == email:
        user.is_confirmed = True
        #user.confirmed_on = datetime.now()
        db.session.add(user)
        db.session.commit()
        flash("You have confirmed your account. Thanks!", "success")
    else:
        flash("The confirmation link is invalid or has expired.", "danger")
    return redirect(url_for("main.index"))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


# --- API methods ---

@auth.route('/api/login', methods=['POST'])
def login_api():
    # login code goes here
    content = request.json
    email = content["email"]
    password = content["password"]

    user = User.query.filter_by(email=email).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        return {"msg":'Please check your login details and try again.'}, 400

    # if the above check passes, then we know the user has the right credentials!

    # generate an access token
    access_token = create_access_token(identity=user.email)
    # create a json friendly representation of the user object and add the access token
    user_dict = simplify_user(user)
    user_dict["accessToken"] = access_token
    # generate and add a refresh token
    refresh_token = create_refresh_token(identity=user.email)
    user_dict["refreshToken"] = refresh_token
    # return that representation
    return user_dict

@auth.route('/api/register', methods=['POST'])
def reg_api():
    # login code goes here
    content = request.json
    name = content["name"]
    email = content["email"]
    password = content["password"]

    # check if the email is valid
    if not re.match(EMAIL_REGEX, email):
        return {"msg":"Invalid credentials"}, 400

    # check if the password is valid
    pw_check = password_check(password)
    if not pw_check["password_ok"]:
        if pw_check["length_error"]:
            return {"msg":"Password must have at least 8 characters"}, 400
        elif pw_check["digit_error"]:
            return {"msg":"Password must have at least 1 number"}, 400
        elif pw_check["uppercase_error"]:
            return {"msg":"Password must have at least 1 uppercase letter"}, 400
        elif pw_check["lowercase_error"]:
            return {"msg":"Password must have at least 1 lowercase letter"}, 400
        elif pw_check["symbol_error"]:
            return {"msg":"Password must have at least 1 symbol"}, 400

    # check if the user already exists
    user = User.query.filter_by(email=email).first()
    if user:
        return {"msg":"User already exists"}, 400

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    user = User(email=email, name=name, password=generate_password_hash(password, method='pbkdf2:sha512'), is_confirmed=False)
    # add the new user to the database
    db.session.add(user)
    db.session.commit()

    # generate a token
    token = generate_token(user.email)
    # create the confirm URL
    confirm_url = url_for("auth.confirm_email", token=token, _external=True)
    # render the registration email template
    html = render_template("email_reg.html", confirm_url=confirm_url)
    subject = "Avoor: Please confirm your email"
    # send the email
    send_email(user.email, subject, html)

    # generate an access token
    access_token = create_access_token(identity=user.email)
    # add the access token and a message to the response
    resp = {"msg":"Please check your email."}
    resp["accessToken"] = access_token
    # generate and add a refresh token
    refresh_token = create_refresh_token(identity=user.email)
    resp["refreshToken"] = refresh_token
    # return that representation
    return resp

@auth.route('/api/resend', methods=['POST'])
@api_unconfirmed_required
def resend(current_api_user):
    # generate a token
    token = generate_token(current_api_user.email)
    # create the confirm URL
    confirm_url = url_for("auth.confirm_email", token=token, _external=True)
    # render the registration email template
    html = render_template("email_reg.html", confirm_url=confirm_url)
    subject = "Avoor: Please confirm your email"
    # send the email
    send_email(current_api_user.email, subject, html)

    return {"msg":"OK"}

@auth.route("/api/confirm", methods=["POST"])
@api_auth_required
def confirm_email_api(current_api_user):
    content = request.json
    if not "token" in content:
        return {"msg":"Missing attribute: token"}, 400
    token = content["token"]

    if current_api_user.is_confirmed:
        return {"msg":"Account already confirmed."}
    email = confirm_token(token)
    user = User.query.filter_by(email=current_api_user.email).first_or_404()
    if user.email == email:
        user.is_confirmed = True
        db.session.add(user)
        db.session.commit()
        # simplify the user and return it alongside a message
        simple_user = simplify_user(user)
        return {"msg":"You have confirmed your account!", "user":simple_user}
    else:
        return {"msg":"The confirmation link is invalid or has expired."}


@auth.route("/api/refreshToken", methods=["POST"])
@jwt_required(refresh = True)
def refresh_token():
    access_token = create_access_token(identity=get_jwt_identity())
    return jsonify(accessToken=access_token)
