from functools import wraps
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_login import current_user, login_required
from flask import flash, request, redirect, url_for
import inspect

from server.bouncer import is_version_allowed

from .models import User

def admin_required(f):
    """
    Only allow admins to use this URL.

    Assumes that the user is already authenticated (e.g. using @login_required).
    """
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('Sorry!')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def api_auth_required(f):
    """
    Only allow authenticated users to use this endpoint.

    Only to be used in API endpoints; for the web interface use flask_login's @login_required.

    Functions that use this decorator can also have a "current_user" argument.
    If a user is found, the corresponding User object will be passed with that argument.
    If "current_user" is already used in a function, "current_api_user" can be used instead.
    """
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        # get the authenticated user's email and try to find the user
        email = get_jwt_identity()
        current_user = User.query.filter_by(email=email).first()

        # check if the user actually exists
        if not current_user:
            return {"msg":'Please check your login details and try again.'}, 400

        # if the user is requested as an argument, pass it
        if 'current_user' in inspect.signature(f).parameters:
            kwargs['current_user'] = current_user

        # in case current_user is already used, check for current_api_user too
        if 'current_api_user' in inspect.signature(f).parameters:
            kwargs['current_api_user'] = current_user

        # call the function
        return f(*args, **kwargs)
    return decorated_function

def api_confirmation_required(f):
    """
    Only allow authenticated and confirmed users to use this endpoint.

    Only to be used in API endpoints; for the web interface use flask_login's @login_required.

    Functions that use this decorator can also have a "current_user" argument.
    If a user is found, the corresponding User object will be passed with that argument.
    If "current_user" is already used in a function, "current_api_user" can be used instead.
    """
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        # get the authenticated user's email and try to find the user
        email = get_jwt_identity()
        current_user = User.query.filter_by(email=email).first()

        # check if the user actually exists
        if not current_user:
            return {"msg":'Please check your login details and try again.'}, 400

        # check if the user is confirmed
        if not current_user.is_confirmed:
            return {"msg":'Please verify your email first.'}, 400

        # if the user is requested as an argument, pass it
        if 'current_user' in inspect.signature(f).parameters:
            kwargs['current_user'] = current_user

        # in case current_user is already used, check for current_api_user too
        if 'current_api_user' in inspect.signature(f).parameters:
            kwargs['current_api_user'] = current_user

        # call the function
        return f(*args, **kwargs)
    return decorated_function

def api_unconfirmed_required(f):
    """
    Only allow authenticated but unconfirmed users to use this endpoint.

    Only to be used in API endpoints; for the web interface use flask_login's @login_required.

    Functions that use this decorator can also have a "current_user" argument.
    If a user is found, the corresponding User object will be passed with that argument.
    If "current_user" is already used in a function, "current_api_user" can be used instead.
    """
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        # get the authenticated user's email and try to find the user
        email = get_jwt_identity()
        current_user = User.query.filter_by(email=email).first()

        # check if the user actually exists
        if not current_user:
            return {"msg":'Please check your login details and try again.'}, 400

        # check if the user is confirmed
        if current_user.is_confirmed:
            return {"msg":'Only unconfirmed users can do this.'}, 400

        # if the user is requested as an argument, pass it
        if 'current_user' in inspect.signature(f).parameters:
            kwargs['current_user'] = current_user

        # in case current_user is already used, check for current_api_user too
        if 'current_api_user' in inspect.signature(f).parameters:
            kwargs['current_api_user'] = current_user

        # call the function
        return f(*args, **kwargs)
    return decorated_function

def logout_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            flash("You are already authenticated.")
            return redirect(url_for("main.index"))
        return func(*args, **kwargs)

    return decorated_function

def confirmed_user_required(f):
    """
    Only allow confirmed users to use this URL.
    """
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_confirmed:
            flash('Please verify your email before using this feature.')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_version_required(f):
    """
    Only allow approved versions of Planbot to access this endpoint.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # read the user agent
        ua = request.headers.get('User-Agent')
        # if the version is not allowed or the check fails, reject the request
        if not ua or not is_version_allowed(ua):
            return {
                "msg": "Please update your version of Avoor."
            }, 400

        # call the function
        return f(*args, **kwargs)
    return decorated_function
