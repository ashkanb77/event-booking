from apps.booking.models import Booking
from django.contrib import admin


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("user", "event", "status", "expires_at", "created_at")
    list_filter = ("status", "event")
    search_fields = ("user__username", "event__title")
    readonly_fields = ("status", "expires_at")
