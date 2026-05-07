from itsdangerous import URLSafeTimedSerializer

from .env_vars import TOKEN_SALT, DB_SECRET_KEY

def generate_token(email):
    serializer = URLSafeTimedSerializer(DB_SECRET_KEY)
    return serializer.dumps(email, salt=TOKEN_SALT)


def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(DB_SECRET_KEY)
    try:
        email = serializer.loads(
            token, salt=TOKEN_SALT, max_age=expiration
        )
        return email
    except Exception:
        return False
