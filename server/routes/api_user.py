"""
Avoor - API user management routes
(c) 2024-2025 githubcatw & Claude
"""
from flask import Blueprint, request

from .. import db, storage
from ..models import User
from ..decorators import api_confirmation_required, api_auth_required
from ..common import simplify_user
from ..compressor import compress_image
from ..discovery import forget_user as discovery_forget

import tempfile
from pathlib import Path
import random

api = Blueprint('api_user', __name__)

@api.route('/api/me')
@api_auth_required
def me(current_user):
    return simplify_user(current_user)

@api.route('/api/me', methods=["DELETE"])
@api_auth_required
def delete_me(current_user: User):
    # ask the discovery process to forget the user
    print("Stopping discovery tasks")
    discovery_forget(current_user)
    # delete the user's profile picture, if it has one
    if current_user.photo_url is not None:
        print("Deleting profile picture")
        remote_url = storage.get_url(current_user.photo_url)
        storage.delete(remote_url)
    # delete the user
    print("Deleting user")
    db.session.delete(current_user)
    db.session.commit()
    # return a success
    return {"msg":"OK"}

ALLOWED_EXTENSIONS = ("png", "jpg")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@api.route('/api/setPicture', methods=['POST'])
@api_confirmation_required
def upload_pfp(current_user):
    # check if the post request has the file part
    if 'picture' not in request.files:
        return {"msg": "No file part"}, 400
    picture = request.files['picture']
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if picture.filename == '':
        return {"msg": "No selected file"}, 400
    if picture and picture.filename and allowed_file(picture.filename):
        # Create a temporary file
        with tempfile.NamedTemporaryFile() as tmp:
            # Save the uploaded file there
            picture.save(tmp)
            # Compress the image
            try:
                compressed_image = compress_image(Path(tmp.name), tmp)
            # ValueErrors are raised if the image is too small
            except ValueError:
                return {"msg": "Image is too small"}, 400
            # Build a path
            remote_path = f"profile/{current_user.id}/pfp{random.randrange(10000000, 99999999)}.jpg"
            # Upload it to cloud storage
            storage.upload_file_object(tmp, remote_path)
            remote_url = storage.get_url(remote_path)
            # Remove the compressed image
            compressed_image.unlink()
            # Set the user's photo URL and update it
            current_user.photo_url = remote_url
            db.session.add(current_user)
            db.session.commit()
        # The temporary file will be removed now

        # Tell the client that the operation was successful
        return {"msg": "Success", "user":simplify_user(current_user)}
    # Otherwise, return a bad request.
    return {"msg": "Bad request"}, 400
