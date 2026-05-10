from django.urls import path
from . import views

urlpatterns = [
    path("",        views.list_comments,  name="list_comments"),
    path("create/", views.create_comment, name="create_comment"),
    path("stream/", views.stream,         name="stream"),
]
