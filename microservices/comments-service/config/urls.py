from django.urls import path, include

urlpatterns = [
    path("comments/", include("app.urls")),
]
