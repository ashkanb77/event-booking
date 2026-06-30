from apps.account.api import RegisterAPIView
from django.urls import path

urlpatterns = [
    path('register', RegisterAPIView.as_view(), name='register'),
]
