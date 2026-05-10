from django.urls import path
from . import views

urlpatterns = [
    path("register/",      views.register,      name="register"),
    path("login/",         views.login_view,     name="login"),
    path("token/refresh/", views.token_refresh,  name="token_refresh"),
    path("me/",            views.me,             name="me"),
]
