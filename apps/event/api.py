from apps.booking.choices import BookingStatusChoice
from django.db.models import Q, F
from django.db.models.aggregates import Count
from django.utils import timezone
from apps.event.models import Event
from apps.event.serializers import CreateEventSerializer, DetailEventSerializer
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class CreateEventAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CreateEventSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DetailEventAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = DetailEventSerializer


    def get(self, request, event_id):
        pending_qs = Q(
            bookings__status=BookingStatusChoice.PENDING, bookings__expires_at__gte=timezone.now()
        )
        confirmed_qs = Q(bookings__status=BookingStatusChoice.CONFIRMED)
        event = Event.objects.filter(pk=event_id).annotate(
            active_booking=Count("bookings", filter=pending_qs | confirmed_qs),
            confirmed_booking=Count("bookings", filter=confirmed_qs),
            remaining_booking=F("capacity") - F("active_booking")
        ).first()

        if not event:
            return Response({"detail": "event not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(event)
        return Response(serializer.data, status=status.HTTP_200_OK)
