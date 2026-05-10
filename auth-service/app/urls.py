from django.urls import path
from . import views

urlpatterns = [
    path("",               views.login_page,      name="login_page"),
    path("login-page/",    views.login_page,      name="login_page_full"),
    path("register/",      views.register,        name="register"),
    path("login/",         views.login_view,      name="login"),
    path("token/refresh/", views.token_refresh,   name="token_refresh"),
    path("me/",            views.me,              name="me"),
]
