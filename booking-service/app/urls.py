from django.urls import path
from . import views

urlpatterns = [
    path("",              views.booking_page,    name="booking_page"),
    path("slots/",        views.slots,           name="slots"),
    path("my/",           views.my_bookings,     name="my_bookings"),
    path("create/",       views.create_booking,  name="create_booking"),
    path("cancel/<int:booking_id>/", views.cancel_booking, name="cancel_booking"),
]
