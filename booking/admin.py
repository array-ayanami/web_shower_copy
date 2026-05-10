from django.contrib import admin
from .models import Booking, FeedbackMessage, Comment


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "date", "time", "created_at")
    list_filter = ("date",)
    search_fields = ("user__username", "user__email", "user__first_name")
    ordering = ("date", "time")


@admin.register(FeedbackMessage)
class FeedbackMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "subject", "created_at")
    list_filter = ("subject",)
    search_fields = ("name", "email", "message")
    readonly_fields = ("name", "email", "subject", "message", "created_at")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "text", "created_at")
    search_fields = ("author__username", "text")
    ordering = ("-created_at",)
