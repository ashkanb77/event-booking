from apps.booking.choices import BookingStatusChoice
from apps.booking.models import Booking
from apps.booking.serializers import CreateBookingSerializer, ConfirmBookingSerializer, CancelBookingSerializer
from apps.event.models import Event
from django.db.transaction import atomic
from django.utils import timezone
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class CreateBookingAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CreateBookingSerializer

    @atomic
    def post(self, request):

        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        event = Event.objects.select_for_update().get(id=serializer.validated_data['event'].id)

        has_user_booking = Booking.active_objects.filter(event=event, user=request.user).exists()
        if has_user_booking:
            return Response({"detail": "Booking already exists"}, status=status.HTTP_409_CONFLICT)

        booking_counts = Booking.active_objects.filter(event=event).count()
        if booking_counts >= event.capacity:
            return Response({"detail": "Event capacity is full."}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ConfirmBookingAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ConfirmBookingSerializer

    @atomic
    def post(self, request, booking_id):
        booking = get_object_or_404(
            Booking.active_objects.select_related('event'),
            id=booking_id, user=request.user, status=BookingStatusChoice.PENDING, expires_at__gt=timezone.now()
        )

        serializer = self.serializer_class(instance=booking, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        booking = Booking.objects.select_related('event').select_for_update(of=('self', 'event')).get(id=booking_id)

        if booking.status != BookingStatusChoice.PENDING or booking.expires_at < timezone.now():
            return Response({"detail": "Booking is no longer available to confirm."}, status=status.HTTP_409_CONFLICT)

        event = booking.event
        active_others = Booking.active_objects.filter(event=event).exclude(pk=booking.pk).count()
        if active_others >= event.capacity:
            return Response({"detail": "Event is fully booked."}, status=status.HTTP_400_BAD_REQUEST)

        serializer.instance = booking
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CancelBookingAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CancelBookingSerializer

    @atomic
    def post(self, request, booking_id):
        booking = get_object_or_404(
            Booking.objects.select_related('event'), id=booking_id, user=request.user,
            status__in=[BookingStatusChoice.PENDING, BookingStatusChoice.CONFIRMED]
        )
        serializer = self.serializer_class(instance=booking, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        Booking.objects.filter(id=booking.id).update(status=BookingStatusChoice.CANCELLED)
        return Response(status=status.HTTP_204_NO_CONTENT)
