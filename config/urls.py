from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/v1/core/", include("apps.core.urls")),
    path("api/v1/accounts/", include("apps.account.urls")),
    path("api/v1/events/", include("apps.event.urls")),
    path("api/v1/booking/", include("apps.booking.urls")),
]
