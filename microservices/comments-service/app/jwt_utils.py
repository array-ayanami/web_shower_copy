import jwt
from django.conf import settings


def get_jwt_payload(request):
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    try:
        payload = jwt.decode(auth[7:], settings.JWT_SECRET_KEY, algorithms=["HS256"])
        return payload if payload.get("type") == "access" else None
    except jwt.PyJWTError:
        return None


def require_auth(view_func):
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
