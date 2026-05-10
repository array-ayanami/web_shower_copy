# Shower Booking — Dormitory (Бронирование душевых | Общежитие)

A Django web application for dormitory residents to book shower time slots online.

## Run & Operate
- **Dev (Replit):** `python manage.py runserver 0.0.0.0:5000`
- **Docker (монолит):** `docker compose up --build` → http://localhost
- **Docker (микросервисы):** `cd microservices && docker compose up --build` → http://localhost
- **Migrate:** `python manage.py migrate`
- **Superuser:** admin / admin1234

## Stack
- Django 5.2 + SQLite (dev) / PostgreSQL (Docker)
- Gunicorn + Nginx (production)
- PyJWT 2.9 (микросервисы: JWT auth)
- Telegram Bot API (feedback)
- Vanilla JS + Django templates

## Where things live
```
shower_booking/settings.py   # конфиг монолита (SQLite ↔ PostgreSQL через DATABASE_URL)
booking/views.py             # все views + SSE endpoint
booking/models.py            # Booking, FeedbackMessage, Comment
booking/urls.py              # URL routing монолита
templates/booking/           # HTML шаблоны
static/booking/css/          # стили
nginx/                       # Nginx конфиг для монолита в Docker
microservices/               # микросервисная архитектура
  docker-compose.yml
  postgres-init/init.sql     # создаёт 4 БД при первом запуске
  nginx/                     # API gateway
  auth-service/              # регистрация/вход, выдаёт JWT
  booking-service/           # брони и слоты
  comments-service/          # комментарии + SSE
  feedback-service/          # обратная связь + Telegram
```

## Architecture decisions
- **Монолит** на Django sessions + SQLite — используется в Replit dev
- **Docker-монолит** (`docker-compose.yml`) — тот же Django, но с PostgreSQL + Gunicorn + Nginx
- **Микросервисы** (`microservices/`) — 4 отдельных Django-процесса; авторизация через JWT (PyJWT), общий `JWT_SECRET_KEY` во всех сервисах; каждый сервис имеет свою PostgreSQL БД
- SSE (Server-Sent Events) используется в comments-service для real-time обновлений; Gunicorn запускается с `--worker-class gthread --threads 8` чтобы держать SSE-соединения
- Nginx routes: `/auth/→8001`, `/booking/→8002`, `/comments/→8003`, `/feedback/→8004`

## Product
- Регистрация / вход (email + пароль)
- Бронирование душевой: сетка слотов 08:00–22:00 каждые 30 мин, один клик → мгновенная бронь
- Мои брони: просмотр и отмена без подтверждения (AJAX)
- Комментарии с SSE real-time обновлением
- Обратная связь → Telegram бот

## User preferences
- Все UI тексты на русском языке
- Минимальная высота кликабельных элементов 44px (закон Фитса)

## Gotchas
- `booking.time` после `Booking.objects.create(time="14:00")` остаётся строкой — не вызывать `.strftime()` на ней
- SSE требует `proxy_buffering off` в Nginx и `gthread` worker в Gunicorn
- `import time` в views.py — не называть локальную переменную `time`, будет конфликт
- Для Docker монолита: скопировать `.env.example` → `.env` перед запуском
- Для микросервисов: скопировать каждый `service/.env.example` → `service/.env`, указать одинаковый `JWT_SECRET_KEY` во всех

## Pointers
- Микросервисы JWT: `microservices/auth-service/app/jwt_utils.py`
- Docker монолит: `Dockerfile` + `docker-compose.yml` + `nginx/nginx.conf`
- Микросервисы оркестрация: `microservices/docker-compose.yml`
