from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()
from stores.models import Place

#Analytics Models
# Create your models here.
class Stat(models.Model):
    REQ = 'REQU'
    REP = 'REPL'
    RAT = 'RATE'
    MESSAGE_CATEGORIES = (
        (REQ, 'Request Sent'),
        (REP, 'Customer Reply'),
        (RAT, 'Customer Reply with Rating'),
    )
    place = models.ForeignKey(Place, on_delete=models.SET_NULL, null=True)
    business_number = models.CharField(max_length=20)
    customer_number = models.CharField(max_length=20)
    feedback_on = models.BooleanField() #review or feedback
    message_category = models.CharField(
        choices=MESSAGE_CATEGORIES,
        max_length=30)
    feedback_rating = models.IntegerField(null=True, blank=True)
    message = models.TextField(max_length=160)
    created_at = models.DateTimeField()

    def __str__(self):
        return self.place.placename

