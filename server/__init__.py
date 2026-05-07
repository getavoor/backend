"""
Avoor
Initialization script
(c) 2024-2025 githubcatw & Claude
"""

# Import environment variables
from .env_vars import *

# Import flask
from flask import Flask

# Import uvicorn (web server) and async extensions for Flask
import uvicorn
from asgiref.wsgi import WsgiToAsgi

# Import SQLAlchemy extensions
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Import login (for web-based auth)
from flask_login import LoginManager

# Import JWT manager (for API auth)
from flask_jwt_extended import JWTManager

# Try to import App Engine APIs
try:
    from google.appengine.api import wrap_wsgi_app as wrap_wsgi_with_gae
except ImportError:
    # Ignore if they can't be imported
    pass

# Import socket.io (for creating a discovery WebSocket)
import socketio

from flask import send_from_directory

# Import and create AI engine
if AI_ENGINE == "gemini" and GEMINI_API_KEY is not None:
    from ai_engine.gemini import GeminiAIEngine
    ai = GeminiAIEngine(GEMINI_API_KEY)
elif AI_ENGINE == "mock":
    from ai_engine import AIEngine
    ai = AIEngine()
else:
    print("Unknown AI engine " + AI_ENGINE + ". AI responses will be replaced with placeholders.")
    from ai_engine import AIEngine
    ai = AIEngine()

# Set up storage access
storage = None
# If the storage variable is set to "folder", set up folder-based storage
if FILE_STORAGE == "folder":
    from abstract_storage.folder import FolderStorage
    storage = FolderStorage("instance/storage")
# If the storage variable is set to "google_storage", set up Google Cloud Storage
elif FILE_STORAGE == "google_bucket":
    from abstract_storage.google import GoogleCloudStorage
    storage = GoogleCloudStorage()

# Create a separate event loop for long-running tasks
import asyncio
from threading import Thread

import traceback

def start_background_loop(loop):
    print("Starting event loop...")
    loop.run_forever()

def lrt_exception_handler(loop, context):
    print('===== Exception in long running task =====')
    print(context)
    print("\n")
    traceback.print_exception(context["exception"])
    print("===== End exception =====")

lrtEventLoop = asyncio.new_event_loop()
lrtEventLoop.set_exception_handler(lrt_exception_handler)

# Create a separate thread to manage the new loop
t = Thread(target=start_background_loop, args=(lrtEventLoop,), daemon=True)
t.start()
print("Created and started LRT event loop thread")

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()

# create a socket.io server
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

# forward all events to the discovery ws handler
from . import discovery
@sio.event
async def connect(sid, environ, auth):
    print('connect ', sid)
    discovery.connect(sid, environ, auth)
@sio.event
def disconnect(sid):
    discovery.disconnect(sid)
@sio.event
async def avr(sid, data):
    return await discovery.avr(sid, data)
@sio.event
async def dsc(sid, data):
    return await discovery.avr(sid, data)
discovery.set_sio(sio)

def create_flask_app() -> Flask:
    """
    Creates a Flask app.
    """
    app = Flask(__name__)

    # init the DB manager
    app.config['SECRET_KEY'] = DB_SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
    # tell sqlalchemy to check if the connection is alive before recycling it
    # this must be set BEFORE db.init_app() for the options to take effect
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }
    db.init_app(app)

    # init migration
    migrate = Migrate(app, db)

    # init the JWT manager
    app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
    jwt = JWTManager(app)

    # init the web login manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    # setup discovery
    discovery.set_flask_app(app)

    # set up lrts
    from .longRunningTasks import set_flask_app as lrt_set_flask
    lrt_set_flask(app)

    # blueprint for auth routes in our app
    from .routes.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .routes.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # blueprint for admin parts of app
    from .routes.admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint)

    # blueprints for API routes
    from .routes.api_user import api as api_user_blueprint
    from .routes.api_streak import api as api_streak_blueprint
    from .routes.api_plancoin import api as api_plancoin_blueprint
    from .routes.api_misc import api as api_misc_blueprint

    app.register_blueprint(api_misc_blueprint)
    app.register_blueprint(api_plancoin_blueprint)
    app.register_blueprint(api_streak_blueprint)
    app.register_blueprint(api_user_blueprint)

    # blueprint for redirecting to the mobile app
    from .routes.app_only import app_only as ad_blueprint
    app.register_blueprint(ad_blueprint)

    # create a route for serving static files
    @app.route('/static/<path:path>')
    def send_static(path):
        # this is ok to use without sanitizing as it already protects
        # against directory traversal attacks
        return send_from_directory('static', path)

    # create a route for serving well-known files
    @app.route('/.well-known/<path:path>')
    def send_wk(path):
        return send_from_directory('well_known', path)

    # for folder-based storage, expose a route that sends the requested photo
    if FILE_STORAGE == "folder":
        @app.route('/photos/<path:path>')
        def send_photo(path):
            # this is ok to use without sanitizing as it already protects
            # against directory traversal attacks
            return send_from_directory('instance/photos', path)

    return app

def create_app() -> socketio.ASGIApp:
    """
    Creates the server's app.
    """

    # create a flask app
    flask_app = create_flask_app()

    # if the App Engine API is available, wrap the ASGI app
    if wrap_wsgi_with_gae:
        flask_app = wrap_wsgi_with_gae(flask_app, use_deferred=True)

    # wrap the socket.io server and flask server together
    # this sends socket.io requests to the socket.io server and sends
    # all other requests to the flask server
    wrapp = socketio.ASGIApp(sio, WsgiToAsgi(flask_app))

    return wrapp

def start_dev():
    """
    Starts the development API server.
    """

    # create the app
    app = create_app()
    # runs the app and makes it visible to everyone
    app.run(host="0.0.0.0")

def create_ws() -> uvicorn.Server:
    """
    Creates a web server for the Flask app.
    """

    return uvicorn.Server(
        config=uvicorn.Config(
            app=create_app(),
            port=int(PORT),
            use_colors=False,
            host="0.0.0.0",
        )
    )


async def start():
    """
    Starts the production API server.
    """
    ws = create_ws()
    await ws.serve()
