from django.urls import path, include

urlpatterns = [
    path("booking/", include("app.urls")),
]
