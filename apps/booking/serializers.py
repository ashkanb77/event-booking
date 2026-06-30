from apps.booking.choices import BookingStatusChoice
from apps.booking.models import Booking
from apps.event.models import Event
from django.utils import timezone
from rest_framework import serializers


class CreateBookingSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    event_id = serializers.PrimaryKeyRelatedField(queryset=Event.objects.all(), source='event', write_only=True)

    class Meta:
        model = Booking
        exclude = ('created_at', 'updated_at')
        read_only_fields = ('id', 'status', 'event', 'expires_at')

    def validate(self, data):
        if data['event'].has_event_date_past:
            raise serializers.ValidationError({"detail": "The date of the event has passed."})
        return data

    def create(self, validated_data):
        user, event = validated_data['user'], validated_data['event']

        Booking.objects.filter(
            user=user, event=event, status=BookingStatusChoice.PENDING, expires_at__lt=timezone.now()
        ).update(status=BookingStatusChoice.EXPIRED)
        booking = Booking.objects.create(user=user, event=event)
        return booking


class ConfirmBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ("id", "event_id", "status")
        read_only_fields = ("id", "event_id", "status")

    def validate(self, data):
        if self.instance and self.instance.event.has_event_date_past:
            raise serializers.ValidationError({"detail": "The date of the event has passed."})
        return data

    def update(self, instance, validated_data):
        instance.status = BookingStatusChoice.CONFIRMED
        instance.save(update_fields=("status",))
        return instance


class CancelBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ("id", "event_id", "status")
        read_only_fields = ("id", "event_id", "status")

    def validate(self, data):
        if self.instance and self.instance.event.has_event_date_past:
            raise serializers.ValidationError({"detail": "The date of the event has passed."})
        return data
