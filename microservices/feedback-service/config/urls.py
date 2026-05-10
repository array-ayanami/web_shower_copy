from django.urls import path, include

urlpatterns = [
    path("feedback/", include("app.urls")),
]
