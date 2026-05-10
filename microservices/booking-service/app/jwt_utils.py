import jwt
from django.conf import settings


def get_jwt_payload(request):
    """Извлекает и проверяет JWT из заголовка Authorization: Bearer <token>."""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth[7:]
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        if payload.get("type") != "access":
            return None
        return payload
    except jwt.PyJWTError:
        return None


def require_auth(view_func):
    """Декоратор: требует валидный JWT. Кладёт payload в request.user_payload."""
    from functools import wraps
    from django.http import JsonResponse

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        payload = get_jwt_payload(request)
        if payload is None:
            return JsonResponse({"error": "Требуется авторизация"}, status=401)
        request.user_payload = payload
        return view_func(request, *args, **kwargs)

    return wrapper
