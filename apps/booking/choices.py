from django.db import models
from django.utils.translation import gettext_lazy as _


class BookingStatusChoice(models.IntegerChoices):
    PENDING = 1, _('Pending')
    CONFIRMED = 2, _('Confirmed')
    CANCELLED = 3, _('Cancelled')
    EXPIRED = 4, _('Expired')
