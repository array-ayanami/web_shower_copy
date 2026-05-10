import json
import time
import requests as http_requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.http import require_http_methods
from django.db import close_old_connections

from .models import Booking, FeedbackMessage, Comment


def index(request):
    return render(request, 'booking/index.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')
            else:
                messages.error(request, 'Неверный email или пароль.')
        except User.DoesNotExist:
            messages.error(request, 'Неверный email или пароль.')
    return render(request, 'booking/login.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        errors = {}

        if len(name) < 2:
            errors['name'] = 'Имя должно быть не менее 2 символов'
        elif len(name) > 32:
            errors['name'] = 'Имя не должно превышать 32 символа'
        elif not __import__('re').match(r'^[А-ЯЁ][а-яё]*$', name):
            errors['name'] = 'Имя с заглавной буквы, только русские буквы'

        if not email:
            errors['email'] = 'Введите email'
        elif User.objects.filter(email=email).exists():
            errors['email'] = 'Этот email уже зарегистрирован'

        if len(password) < 6:
            errors['password'] = 'Пароль должен быть не менее 6 символов'
        elif len(password) > 32:
            errors['password'] = 'Пароль не должен превышать 32 символа'

        if not errors:
            username = email.split('@')[0]
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f'{base_username}{counter}'
                counter += 1
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=name,
            )
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('booking_create')

        return render(request, 'booking/register.html', {'errors': errors, 'values': request.POST})

    return render(request, 'booking/register.html')


def logout_view(request):
    logout(request)
    return redirect('index')


@login_required
def booking_create(request):
    if request.method == 'POST':
        date = request.POST.get('date')
        time_val = request.POST.get('time')
        if not date or not time_val:
            messages.error(request, 'Заполните дату и время')
            return render(request, 'booking/booking.html')
        Booking.objects.create(user=request.user, date=date, time=time_val)
        messages.success(request, 'Бронирование успешно выполнено!')
        return redirect('my_bookings')
    return render(request, 'booking/booking.html')


@login_required
@require_http_methods(["POST"])
def booking_api(request):
    """Мгновенное бронирование одним кликом. Принимает JSON {date, time}."""
    try:
        data = json.loads(request.body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'success': False, 'error': 'Некорректный JSON'}, status=400)

    date = (data.get('date') or '').strip()
    time_val = (data.get('time') or '').strip()
    if not date or not time_val:
        return JsonResponse({'success': False, 'error': 'Укажите дату и время'}, status=400)

    if Booking.objects.filter(date=date, time=time_val).exists():
        return JsonResponse({'success': False, 'error': 'Этот слот уже занят'}, status=409)

    booking = Booking.objects.create(user=request.user, date=date, time=time_val)
    return JsonResponse({
        'success': True,
        'booking': {
            'id': booking.id,
            'date': date,
            'time': time_val,
        },
    }, status=201)


def booked_slots_api(request):
    """Возвращает занятые слоты за дату: все занятые + персональные."""
    date = request.GET.get('date', '').strip()
    if not date:
        return JsonResponse({'success': False, 'error': 'Укажите дату'}, status=400)
    booked = [
        t.strftime('%H:%M')
        for t in Booking.objects.filter(date=date).values_list('time', flat=True)
    ]
    mine = []
    if request.user.is_authenticated:
        mine = [
            t.strftime('%H:%M')
            for t in Booking.objects.filter(date=date, user=request.user).values_list('time', flat=True)
        ]
    return JsonResponse({'success': True, 'booked': booked, 'mine': mine})


@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'booking/mybookings.html', {'bookings': bookings})


@login_required
@require_http_methods(["POST"])
def cancel_booking(request, booking_id):
    """Отмена брони — один клик, без подтверждения."""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    booking.delete()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    messages.success(request, 'Бронирование отменено.')
    return redirect('my_bookings')


def info_view(request):
    return render(request, 'booking/info.html')


def feedback_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject_key = request.POST.get('subject', '')
        message_text = request.POST.get('message', '').strip()

        subject_labels = {
            'booking': 'Бронирование',
            'technical': 'Техническая проблема',
            'suggestion': 'Предложение',
            'other': 'Другое',
        }

        if not all([name, email, subject_key, message_text]):
            messages.error(request, 'Заполните все поля')
            return render(request, 'booking/feedback.html', {'values': request.POST})

        FeedbackMessage.objects.create(
            name=name,
            email=email,
            subject=subject_key,
            message=message_text,
        )

        subject_text = subject_labels.get(subject_key, subject_key)
        telegram_message = (
            f'💬 <b>Новое сообщение обратной связи</b>\n'
            f'👤 Имя: {name}\n'
            f'📧 Email: {email}\n'
            f'📌 Тема: {subject_text}\n'
            f'💭 Сообщение:\n{message_text}\n'
            f'🕐 Время: {timezone.now().strftime("%d.%m.%Y %H:%M")}'
        )

        try:
            token = settings.TELEGRAM_BOT_TOKEN
            chat_id = settings.TELEGRAM_CHAT_ID
            url = f'https://api.telegram.org/bot{token}/sendMessage'
            http_requests.post(url, json={
                'chat_id': chat_id,
                'text': telegram_message,
                'parse_mode': 'HTML',
            }, timeout=5)
        except Exception:
            pass

        messages.success(request, 'Сообщение отправлено!')
        return redirect('feedback')

    return render(request, 'booking/feedback.html')


def comments_page(request):
    return render(request, 'booking/comments.html')


@require_http_methods(["GET", "POST"])
def comments_api(request):
    if request.method == 'GET': #  возвращает все комментарии в JSON (последние 100)
        comments = Comment.objects.all()[:100]
        return JsonResponse({
            'success': True,
            'comments': [c.to_dict() for c in comments],
        })

    if not request.user.is_authenticated:
        return JsonResponse(
            {'success': False, 'error': 'Требуется авторизация'},
            status=401,
        )

    try:
        data = json.loads(request.body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse(
            {'success': False, 'error': 'Некорректный JSON'},
            status=400,
        )

    text = (data.get('text') or '').strip()
    if not text:
        return JsonResponse(
            {'success': False, 'error': 'Сообщение не может быть пустым'},
            status=400,
        )
    if len(text) > 1000:
        return JsonResponse(
            {'success': False, 'error': 'Слишком длинное сообщение (максимум 1000 символов)'},
            status=400,
        )

    comment = Comment.objects.create(author=request.user, text=text)
    return JsonResponse({'success': True, 'comment': comment.to_dict()}, status=201)


def comments_stream(request):
    """Server-Sent Events: отправляет новые комментарии клиенту в реальном времени."""
    try:
        last_id = int(request.GET.get('last_id', 0))
    except (TypeError, ValueError):
        last_id = 0

    def event_stream(start_id):
        current_id = start_id
        # Сначала отправляем все существующие комментарии (если клиент только подключился)
        if current_id == 0:
            initial = list(Comment.objects.order_by('id')[:100])
            for c in initial:
                yield f"data: {json.dumps(c.to_dict())}\n\n"
                current_id = max(current_id, c.id)
            close_old_connections()

        # Длительность одного соединения — 5 минут, потом клиент сам переподключится
        deadline = time.time() + 300
        while time.time() < deadline:
            new_comments = list(
                Comment.objects.filter(id__gt=current_id).order_by('id')
            )
            close_old_connections()
            for c in new_comments:
                yield f"data: {json.dumps(c.to_dict())}\n\n"
                current_id = c.id
            # Heartbeat (комментарий в SSE) — чтобы прокси не закрывали соединение
            yield ": ping\n\n"
            time.sleep(1.5)

    response = StreamingHttpResponse(
        event_stream(last_id),
        content_type='text/event-stream',
    )
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response
