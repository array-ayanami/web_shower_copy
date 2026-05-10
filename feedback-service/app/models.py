from django.db import models


class FeedbackMessage(models.Model):
    SUBJECT_CHOICES = [
        ("booking",    "Бронирование"),
        ("technical",  "Техническая проблема"),
        ("suggestion", "Предложение"),
        ("other",      "Другое"),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=20, choices=SUBJECT_CHOICES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.get_subject_display()}) — {self.created_at:%d.%m.%Y %H:%M}"
