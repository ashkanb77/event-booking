from django.db import models
from django.db.models import Q
from django.utils import timezone

from apps.booking.choices import BookingStatusChoice


class ActiveBookingManager(models.Manager):

    def get_queryset(self):
        qs = (Q(status=BookingStatusChoice.CONFIRMED)
              | Q(status=BookingStatusChoice.PENDING, expires_at__gte=timezone.now()))
        return super().get_queryset().filter(qs)
