from django.utils import timezone
from apps.event.models import Event
from rest_framework import serializers


class CreateEventSerializer(serializers.ModelSerializer):
    admin = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Event
        exclude = ('created_at', 'updated_at')
        read_only_fields = ('id',)

    def validate_event_date(self, event_date):
        if event_date < timezone.now():
            raise serializers.ValidationError('Event date cannot be in the past')
        return event_date


class DetailEventSerializer(serializers.ModelSerializer):
    confirmed_booking = serializers.IntegerField(read_only=True)
    active_booking = serializers.IntegerField(read_only=True)
    remaining_booking = serializers.IntegerField(read_only=True)

    class Meta:
        model = Event
        exclude = ('id', 'created_at', 'updated_at', 'admin')
