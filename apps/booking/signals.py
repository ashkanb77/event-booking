from apps.booking.constants import BOOKING_EXPIRATION_MINUTES
from apps.booking.models import Booking
from apps.booking.tasks import expire_booking
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=Booking)
def schedule_booking_expiry(sender, instance, created, **kwargs):
    if created:
        expire_booking.apply_async(args=[instance.id], countdown=60 * BOOKING_EXPIRATION_MINUTES)
