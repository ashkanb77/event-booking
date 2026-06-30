from datetime import timedelta

from apps.booking.choices import BookingStatusChoice
from apps.booking.constants import BOOKING_EXPIRATION_MINUTES
from apps.booking.managers import ActiveBookingManager
from apps.core.models import BaseModel
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Manager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


def _default_booking_expires_at():
    return timezone.now() + timedelta(minutes=BOOKING_EXPIRATION_MINUTES)


class Booking(BaseModel):
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE, related_name="bookings", verbose_name=_("User"))
    event = models.ForeignKey("event.Event", on_delete=models.CASCADE, related_name="bookings", verbose_name=_("Event"))
    status = models.PositiveSmallIntegerField(
        choices=BookingStatusChoice.choices, default=BookingStatusChoice.PENDING, verbose_name=_("Booking status")
    )
    expires_at = models.DateTimeField(default=_default_booking_expires_at, verbose_name=_("Expiration time"))

    active_objects = ActiveBookingManager()
    objects = Manager()

    class Meta:
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "event"],
                condition=models.Q(status__in=[BookingStatusChoice.PENDING, BookingStatusChoice.CONFIRMED]),
                name="unique_active_booking_per_user_event",
            ),
        ]

    @property
    def is_active(self):
        return self.status == BookingStatusChoice.CONFIRMED or (
                self.status == BookingStatusChoice.PENDING and self.expires_at >= timezone.now()
        )

    def clean(self):
        super().clean()
        if not self.is_active:
            return

        active_count = Booking.active_objects.filter(event=self.event).exclude(pk=self.pk).count()
        if active_count >= self.event.capacity:
            raise ValidationError("Event capacity exceeded.")

    def __str__(self) -> str:
        return f"Booking #{self.pk} | user={self.user_id} event={self.event_id} [{self.status}]"
