from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('booking/', views.booking_create, name='booking_create'),
    path('api/book/', views.booking_api, name='booking_api'),
    path('api/booked-slots/', views.booked_slots_api, name='booked_slots_api'),
    path('mybookings/', views.my_bookings, name='my_bookings'),
    path('mybookings/cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('info/', views.info_view, name='info'),
    path('feedback/', views.feedback_view, name='feedback'),
    path('comments/', views.comments_page, name='comments'),
    path('api/comments/', views.comments_api, name='comments_api'),
    path('api/comments/stream/', views.comments_stream, name='comments_stream'),
]
