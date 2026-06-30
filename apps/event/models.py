from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.booking.models import Booking
from apps.core.models import BaseModel


class Event(BaseModel):
    admin = models.ForeignKey(
        "auth.User", on_delete=models.CASCADE, verbose_name=_('Administrator'), related_name="events"
    )
    title = models.CharField(max_length=255, verbose_name=_('Title'))
    description = models.TextField(verbose_name=_('Description'))
    capacity = models.PositiveIntegerField(verbose_name=_('Capacity'), validators=[MinValueValidator(1)])
    event_date = models.DateTimeField(verbose_name=_('Event Date'))

    class Meta:
        verbose_name = 'Event'
        verbose_name_plural = 'Events'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(capacity__gte=1), name='event_capacity_min_1'
            )
        ]

    @property
    def has_event_date_past(self):
        return self.event_date < timezone.now()

    def clean(self):
        super().clean()
        if self.has_event_date_past:
            raise ValidationError({'event_date': _('Event date cannot be in the past.')})

        active_bookings_count = Booking.active_objects.filter(event=self).count()
        if active_bookings_count > self.capacity:
            raise ValidationError({'capacity': _('Event capacity exceeds the maximum capacity.')})

    def __str__(self) -> str:
        return f"{self.title} ({self.capacity}, {self.event_date.date()})"
