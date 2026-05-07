"""
Avoor - Common Utilities
(c) 2024-2025 githubcatw & Claude
"""
from .models import User
from . import lrtEventLoop, storage
from . import EMAIL_ADDRESS, EMAIL_PASSWORD

try:
    from google.appengine.api import mail as gae_mail
except ImportError:
    # Ignore if they can't be imported
    pass

import asyncio
import traceback

import requests
import os
import re
import tempfile
import pathlib
import css_inline

def simplify_user(user: User) -> dict:
    """
    Return a simple representation of a User as a dict.

    All internal fields (e.g. is_admin) are removed in this representation.
    """
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "photoUrl": user.photo_url,
        "confirmed": user.is_confirmed,
        "plancoins": user.plancoins,
        "currentStreak": user.current_streak,
        "longestStreak": user.longest_streak
    }

def oversimplify_user(user: User) -> dict:
    """
    Return a very simple representation of a User as a dict.

    In addition to all internal fields (e.g. is_admin), the email
    and confirmation status are removed in this representation.
    """
    return {
        "id": user.id,
        "name": user.name,
        "photoUrl": user.photo_url
    }

async def call_later(coro, *args, **kwargs):
    lrtEventLoop.create_task(coro(*args, **kwargs))
    return "ok"

def schedule_lrt(func, *args, **kwargs):
    """
    Schedules a long running task, passed in as func, on the LRT event loop and returns the task.
    """
    return asyncio.run_coroutine_threadsafe(call_later(func, *args, **kwargs), loop=lrtEventLoop)

def download_file(url: str, local_filename: str = None) -> str:
    if local_filename == None:
        local_filename = url.split('/')[-1]
    local_path = os.path.join(tempfile.gettempdir(), local_filename)
    # NOTE the stream=True parameter below
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                #if chunk: 
                f.write(chunk)
    return local_path

def password_check(password: str) -> dict:
    """
    Verify the strength of 'password'
    Returns a dict indicating the wrong criteria
    A password is considered strong if:
        8 characters length or more
        1 digit or more
        1 symbol or more
        1 uppercase letter or more
        1 lowercase letter or more
    """

    # calculating the length
    length_error = len(password) < 8

    # searching for digits
    digit_error = re.search(r"\d", password) is None

    # searching for uppercase
    uppercase_error = re.search(r"[A-Z]", password) is None

    # searching for lowercase
    lowercase_error = re.search(r"[a-z]", password) is None

    # searching for symbols
    symbol_error = re.search(r"\W", password) is None

    # overall result
    password_ok = not ( length_error or digit_error or uppercase_error or lowercase_error or symbol_error )

    return {
        'password_ok' : password_ok,
        'length_error' : length_error,
        'digit_error' : digit_error,
        'uppercase_error' : uppercase_error,
        'lowercase_error' : lowercase_error,
        'symbol_error' : symbol_error,
    }

def mirror_remote_photo(photo_url: str, remote_filename_prefix: str) -> str:
    # download the photo
    local_file = download_file(photo_url, "photo.jpg")
    # upload it to storage
    remote_filename = f"{remote_filename_prefix}/{os.path.basename(local_file)}"
    storage.upload(local_file, remote_filename)
    # remove the temporary file
    pathlib.Path(local_file).unlink()
    # return the web URL for this file
    return storage.get_url(remote_filename)

def send_email(to, subject, html):
    # inline the CSS stylesheet for it to work in the email
    html = css_inline.inline(html)
    # send the email
    if EMAIL_PASSWORD == "GAEIgnore":
        send_gae_email(to, subject, html)
    else:
        send_flask_email(to, subject, html)

def send_flask_email(to, subject, html):
    raise Exception("Not implemented")

def send_gae_email(to, subject, html):
    message = gae_mail.EmailMessage(
        sender=EMAIL_ADDRESS,
        subject=subject)

    message.to = to
    message.html = html
    message.send()
