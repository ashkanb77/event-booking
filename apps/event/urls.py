from django.urls import path

from apps.event.api import CreateEventAPIView, DetailEventAPIView

urlpatterns = [
    path('create', CreateEventAPIView.as_view(), name='create-event'),
    path('detail/<uuid:event_id>', DetailEventAPIView.as_view(), name='create-event')
]
