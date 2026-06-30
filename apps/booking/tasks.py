from celery import shared_task
from django.db.transaction import atomic
from django.utils import timezone

from apps.booking.choices import BookingStatusChoice
from apps.booking.models import Booking


@shared_task(acks_late=True)
@atomic
def expire_booking(booking_id):
    booking = Booking.objects.filter(
        id=booking_id, status=BookingStatusChoice.PENDING, expires_at__lt=timezone.now()
    ).first()

    if not booking:
        return f"Booking {booking_id} not found!"

    booking.status = BookingStatusChoice.EXPIRED
    booking.save(update_fields=["status", ])
    return f"Expired booking {booking.id}"


@shared_task()
def cleanup_expired_bookings():
    batch_size = 1000
    now = timezone.now()

    while True:
        ids = list(
            Booking.objects.filter(
                status=BookingStatusChoice.PENDING, expires_at__lt=now,
            ).order_by("created_at").values_list("id", flat=True)[:batch_size]
        )
        if not ids:
            break

        updated_count = Booking.objects.filter(id__in=ids).update(status=BookingStatusChoice.EXPIRED)
        if updated_count == 0:
            break
    return "Bookings cleaned up."
