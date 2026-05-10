from typing import cast
from django.db import models
from django.contrib.auth.models import User


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    date = models.DateField()
    time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date", "time"]

    def __str__(self):
        user = cast(User, self.user)
        return f"{user.first_name or user.username} — {self.date} {self.time}"


class FeedbackMessage(models.Model):
    SUBJECT_CHOICES = [
        ("booking", "Бронирование"),
        ("technical", "Техническая проблема"),
        ("suggestion", "Предложение"),
        ("other", "Другое"),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=20, choices=SUBJECT_CHOICES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Сообщение обратной связи"
        verbose_name_plural = "Сообщения обратной связи"

    def __str__(self):
        return f"{self.name} ({self.get_subject_display()}) — {self.created_at:%d.%m.%Y %H:%M}"


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    def __str__(self):
        author = cast(User, self.author)
        return f"{author.first_name or author.username}: {self.text[:50]}"

    def to_dict(self):
        author = cast(User, self.author)
        return {
            "id": self.pk,
            "author": author.first_name or author.username,
            "text": self.text,
            "created_at": self.created_at.strftime("%d.%m.%Y %H:%M"),
        }
