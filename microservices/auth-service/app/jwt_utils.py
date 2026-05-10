import jwt
from datetime import datetime, timedelta, timezone
from django.conf import settings


def generate_tokens(user):
    """Генерирует пару access + refresh JWT токенов для пользователя."""
    now = datetime.now(timezone.utc)
    access_payload = {
        "user_id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "email": user.email,
        "exp": now + timedelta(hours=settings.JWT_ACCESS_TTL_HOURS),
        "iat": now,
        "type": "access",
    }
    refresh_payload = {
        "user_id": user.id,
        "username": user.username,
        "exp": now + timedelta(days=settings.JWT_REFRESH_TTL_DAYS),
        "iat": now,
        "type": "refresh",
    }
    access = jwt.encode(access_payload, settings.JWT_SECRET_KEY, algorithm="HS256")
    refresh = jwt.encode(refresh_payload, settings.JWT_SECRET_KEY, algorithm="HS256")
    return access, refresh


def decode_token(token, expected_type=None):
    """Декодирует JWT, возвращает payload или None при ошибке."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        if expected_type and payload.get("type") != expected_type:
            return None
        return payload
    except jwt.PyJWTError:
        return None
