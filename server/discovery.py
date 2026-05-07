"""
Avoor - WebSocket Discovery & Authentication
(c) 2024-2025 githubcatw & Claude
"""
from flask_jwt_extended import decode_token

from .models import User
from .longRunningTasks import *
from .common import *

import time
import logging

# Dictionary of authorized users, where the key is the socket.io SID and the value the User object.
AUTHED_USERS = {}

# Dictionary of authorized users, where the key is the socket.io SID and the value the provided refresh token's expiry date.
AUTHED_USER_EXP = {}

# List of commands available to unauthorized users.
UNAUTHED_COMMANDS = ("enter", "compat")

class ErrorCodes:
    """
    Error codes for sending as responses to invalid data sent over socket.io.

    Loosely match HTTP error codes.
    """

    UNAUTHORIZED = 403
    INVALID_DATA = 400
    UNKNOWN_COMMAND = 404
    OK = 200
    CONFIRMED_ONLY = 600

# The protocol version.
PROTOCOL_VER = 10
# The minimum supported protocol version.
MIN_COMPATIBLE_PROTOCOL_VER = 10

sio = None
flask_app = None

def set_sio(nsio):
    global sio
    sio = nsio

def set_flask_app(app):
    global flask_app
    flask_app = app

def connect(sid, environ, auth):
    """
    Called when a client connects.
    """
    print(sid + " connected!")

def forget_user(user: User):
    """
    Delete all data about the user.
    """
    # find the user's sid
    for sid in AUTHED_USERS:
        if AUTHED_USERS[sid].id == user.id:
            forget(sid)
            return

def forget(sid: str):
    """
    Delete all data about the user with the provided SID.
    """
    # remove the SID from all dictionaries that use the SID as a key (to prevent reuse attacks)
    if sid in AUTHED_USERS:
        del AUTHED_USERS[sid]
    if sid in AUTHED_USER_EXP:
        del AUTHED_USER_EXP[sid]

def disconnect(sid):
    """
    Called when a client disconnects.
    """
    print(sid + " disconnected!")
    # if it is authorized:
    if sid in AUTHED_USERS:
        forget(sid)
    print("Deleted all links to sid " + sid)

async def avr(sid, data):
    """
    Handle WebSocket messages.
    """
    # check if the message is valid
    if "cmd" not in data:
        print(f'SID {sid} - request "{data.get("cmd", "unknown")}" {ErrorCodes.INVALID_DATA} Invalid Data')
        return ErrorCodes.INVALID_DATA
    # unauthorized clients don't have permission to run some commands
    if not sid in AUTHED_USERS and not data["cmd"] in UNAUTHED_COMMANDS:
        print(f'SID {sid} - request "{data["cmd"]}" {ErrorCodes.UNAUTHORIZED} Unauthorized')
        return ErrorCodes.UNAUTHORIZED
    # if the user _is_ authorized, but their token has expired, reject the request
    if sid in AUTHED_USER_EXP and not data["cmd"] in UNAUTHED_COMMANDS:
        if time.time() > AUTHED_USER_EXP[sid]:
            print(f'SID {sid} - request "{data["cmd"]}" {ErrorCodes.UNAUTHORIZED} Unauthorized (token expired)')
            return ErrorCodes.UNAUTHORIZED
    print(f'SID {sid} - request "{data["cmd"]}" (passed prechecks)')
    # now check the command:
    if data["cmd"] == "enter":
        return await avr_enter(sid, data)
    # if the command is "compat" (compatibility check):
    elif data["cmd"] == "compat":
        return await avr_compat(sid, data)
    else:
        return ErrorCodes.UNKNOWN_COMMAND

async def avr_enter(sid, data):
    """
    Handle the enter (login) command.
    """
    # check if the message is valid
    if "arg" not in data:
        print("Invalid data!")
        return ErrorCodes.INVALID_DATA
    # check the token and reject invalid ones
    try:
        with flask_app.app_context():
            decoded = decode_token(data["arg"])
            # retrieve the user
            current_user = User.query.filter_by(email=decoded['sub']).first()
            AUTHED_USERS[sid] = current_user
            AUTHED_USER_EXP[sid] = decoded["exp"]
            # check if the user actually exists
            if not current_user:
                return ErrorCodes.INVALID_DATA
            # check if the user is confirmed
            if not current_user.is_confirmed:
                return ErrorCodes.CONFIRMED_ONLY
            print("Authorized")
            return ErrorCodes.OK
    except Exception as e:
        print("JWT decode exception:" + str(e))
        return ErrorCodes.INVALID_DATA

async def avr_compat(sid, data):
    """
    Handle the compat (compatibility check) command.
    """

    # if the client sent its own protocol version:
    if "arg" in data:
        # well, it must be an int
        if type(data["arg"]) != int:
            print("Invalid data!")
            return ErrorCodes.INVALID_DATA
        # if the client's protocol version is older than 3, it likely ignores acknowledgements
        # emit an old style response telling it that it's incompatible and return nothing
        client_proto = data["arg"]
        if client_proto < 3:
            await sio.emit("avr",{"version":PROTOCOL_VER, "supported":False}, to=sid)
            return
        # compare it and send the verdict along with the protocol version
        return ErrorCodes.OK, PROTOCOL_VER, client_proto >= MIN_COMPATIBLE_PROTOCOL_VER
    # otherwise return OK and the protocol version
    else:
        return ErrorCodes.OK, PROTOCOL_VER
