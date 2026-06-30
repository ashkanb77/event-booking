from django.contrib import admin
from apps.event.models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "admin", "capacity", "event_date")
    list_filter = ("event_date",)
    search_fields = ("title", "admin__username")
