from apps.booking.api import CreateBookingAPIView, ConfirmBookingAPIView, CancelBookingAPIView
from django.urls import path

urlpatterns = [
    path('create', CreateBookingAPIView.as_view(), name='create-booking'),
    path('<uuid:booking_id>/confirm', ConfirmBookingAPIView.as_view(), name='confirm-booking'),
    path('<uuid:booking_id>/cancel', CancelBookingAPIView.as_view(), name='cancel-booking'),
]
