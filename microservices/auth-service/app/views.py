import json
import re
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .jwt_utils import generate_tokens, decode_token


def _json_body(request):
    try:
        return json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


@csrf_exempt
@require_http_methods(["POST"])
def register(request):
    """POST /auth/register/ — регистрация нового пользователя."""
    data = _json_body(request)
    if data is None:
        return JsonResponse({"error": "Некорректный JSON"}, status=400)

    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    errors = {}
    if len(name) < 2:
        errors["name"] = "Имя не менее 2 символов"
    elif not re.match(r"^[А-ЯЁ][а-яё]+$", name):
        errors["name"] = "Имя с заглавной буквы, только русские буквы"
    if not email:
        errors["email"] = "Введите email"
    elif User.objects.filter(email=email).exists():
        errors["email"] = "Email уже зарегистрирован"
    if len(password) < 6:
        errors["password"] = "Пароль не менее 6 символов"

    if errors:
        return JsonResponse({"errors": errors}, status=422)

    base = email.split("@")[0]
    username = base
    i = 1
    while User.objects.filter(username=username).exists():
        username = f"{base}{i}"
        i += 1

    user = User.objects.create_user(
        username=username, email=email, password=password, first_name=name
    )
    access, refresh = generate_tokens(user)
    return JsonResponse({
        "access": access,
        "refresh": refresh,
        "user": {"id": user.id, "name": user.first_name, "email": user.email},
    }, status=201)


@csrf_exempt
@require_http_methods(["POST"])
def login_view(request):
    """POST /auth/login/ — вход, возвращает JWT токены."""
    data = _json_body(request)
    if data is None:
        return JsonResponse({"error": "Некорректный JSON"}, status=400)

    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return JsonResponse({"error": "Неверный email или пароль"}, status=401)

    if not user.check_password(password):
        return JsonResponse({"error": "Неверный email или пароль"}, status=401)

    access, refresh = generate_tokens(user)
    return JsonResponse({
        "access": access,
        "refresh": refresh,
        "user": {"id": user.id, "name": user.first_name, "email": user.email},
    })


@csrf_exempt
@require_http_methods(["POST"])
def token_refresh(request):
    """POST /auth/token/refresh/ — обновление access токена через refresh."""
    data = _json_body(request)
    if data is None:
        return JsonResponse({"error": "Некорректный JSON"}, status=400)

    refresh_token = data.get("refresh") or ""
    payload = decode_token(refresh_token, expected_type="refresh")
    if payload is None:
        return JsonResponse({"error": "Недействительный или просроченный refresh токен"}, status=401)

    try:
        user = User.objects.get(id=payload["user_id"])
    except User.DoesNotExist:
        return JsonResponse({"error": "Пользователь не найден"}, status=404)

    access, new_refresh = generate_tokens(user)
    return JsonResponse({"access": access, "refresh": new_refresh})


@csrf_exempt
@require_http_methods(["GET"])
def me(request):
    """GET /auth/me/ — информация о текущем пользователе из JWT."""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return JsonResponse({"error": "Требуется токен"}, status=401)

    payload = decode_token(auth[7:], expected_type="access")
    if payload is None:
        return JsonResponse({"error": "Недействительный токен"}, status=401)

    return JsonResponse({
        "user_id": payload["user_id"],
        "username": payload["username"],
        "first_name": payload["first_name"],
        "email": payload["email"],
    })
