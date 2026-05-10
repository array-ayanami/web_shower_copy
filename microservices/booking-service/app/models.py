from django.db import models


class Booking(models.Model):
    """Бронь душевой. user_id и username берутся из JWT — без FK на User."""
    user_id = models.IntegerField(db_index=True)
    username = models.CharField(max_length=150)
    date = models.DateField()
    time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date", "time"]
        # Один слот — одна бронь (любым пользователем)
        unique_together = [("date", "time")]

    def __str__(self):
        return f"{self.username} — {self.date} {self.time}"

    def to_dict(self):
        return {
            "id": self.pk,
            "user_id": self.user_id,
            "username": self.username,
            "date": str(self.date),
            "time": self.time.strftime("%H:%M"),
            "created_at": self.created_at.strftime("%d.%m.%Y %H:%M"),
        }
