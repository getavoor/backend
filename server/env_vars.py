"""
Avoor - server
Environment variable loader
(c) 2024 githubcatw
"""

# Load variables from the .env file, if it exists
from dotenv import load_dotenv
import os

# load_dotenv() returns if it was successful - in that case print a message
if load_dotenv():
    print("Loaded .env file successfully.")
    # Check if the .env file has been loaded by testing the bot token variable
    test = os.environ.get("AVR_DB_SK", None)
    if test == None:
        print("Self test: DB secret key is UNSET - this will cause an error")
    else:
        print("Self test: DB secret key is set")

def get_env_or_exit(name: str) -> str:
    """
    Gets an environment variable and closes the program if it doesn't exist.
    """
    # Get the variable if possible
    var = os.environ.get(name, None)
    # If it doesn't exist, print a warning and exit
    if var == None:
        print(f"Avoor can't work without the environment variable {name} being set.")
        print("Please set this variable and restart the Avoor server.")
        exit()
    # Otherwise, return the variable
    return var

# Load required environment variables
DB_SECRET_KEY = get_env_or_exit("AVR_DB_SK")
DB_URI = get_env_or_exit("AVR_DB_URL")
JWT_SECRET_KEY = get_env_or_exit("AVR_JW_SK")
SOCK_SECRET_KEY = get_env_or_exit("AVR_SI_SK")
TOKEN_SALT = get_env_or_exit("AVR_TK_SL")
EMAIL_ADDRESS = get_env_or_exit("AVR_EM_AD")

if EMAIL_ADDRESS.endswith("appspotmail.com"):
    EMAIL_PASSWORD = "GAEIgnore"
    try:
        import google.appengine.api.mail
        print("App Engine email detected. No password is required.")
    except ImportError:
        print("To use Google App Engine email, install the App Engine bundled services SDK:")
        print("pip3 install appengine-python-standard>=1.0.0")
        print('(Or set the environment variable AVR_EM_AD to an address that doesn\'t end with "appspotmail.com" to disable App Engine email)')
        exit()
else:
    EMAIL_PASSWORD = os.environ.get("AVR_EM_PW", None)
    if EMAIL_PASSWORD == None:
        print("Avoor can't work without the environment variable AVR_EM_PW being set.")
        print("Please set this variable and restart the Avoor server.")
        print('(Hint: if you want to use Google App Engine email, set it to "GAEIgnore")')
        exit()
    elif EMAIL_PASSWORD == "GAEIgnore":
        try:
            import google.appengine.api.mail
            print("Ignoring password and using Google App Engine email.")
        except ImportError:
            print("To use Google App Engine email, install the App Engine bundled services SDK:")
            print("pip3 install appengine-python-standard>=1.0.0")
            print('(Or set the environment variable AVR_EM_PW to anything other than "GAEIgnore" to disable App Engine email)')
            exit()

# Load AI engine related config
AI_ENGINE = os.environ.get("AVR_AI", "mock")
GEMINI_API_KEY = os.environ.get("AVR_GAK", None)

if AI_ENGINE == "gemini" and GEMINI_API_KEY is None:
    print("Since Gemini is selected as the AI engine, the Planbot+ backend cannot work without a Gemini API key.")
    print("Please set the variable AVR_GAK to a Gemini API key and restart the Planbot+ backend.")
    print('(Hint: to use another AI engine, set the variable AVR_AI to its ID, or to "mock" to use a placeholder.)')
    exit()

# Load optional environment variables
PORT = os.environ.get("AVR_PORT", 8080)
FILE_STORAGE = os.environ.get("AVR_FS", "folder")
