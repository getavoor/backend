"""
Avoor - Long Running Tasks
(c) 2024-2025 githubcatw & Claude
"""
from .models import User
from . import ai, db, storage
from .common import simplify_user
from .env_vars import GEMINI_API_KEY
from ai_engine import AIChatSession
from ai_engine.exceptions import *

from sqlalchemy.orm.util import has_identity

import asyncio
import os
import pathlib
import time

flask_app = None

def set_flask_app(app):
    global flask_app
    flask_app = app

# Add time management-related long-running tasks here as needed
# For example: tasks for streak calculations, scheduled notifications, etc.
