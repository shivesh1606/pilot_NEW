from itsdangerous import URLSafeTimedSerializer

SECRET_KEY = "Asdsad"
SECURITY_PASSWORD_SALT = "Asdsad"

def generate_token(email):
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    return serializer.dumps(email, salt=SECURITY_PASSWORD_SALT)


def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    try:
        email = serializer.loads(
            token, salt=SECURITY_PASSWORD_SALT, max_age=expiration
        )
        return email
    except Exception:
        return False