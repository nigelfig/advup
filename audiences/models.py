from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()
from stores.models import Place
from django.shortcuts import get_object_or_404


# # Create your models here.
class Audience(models.Model):
    PROCESSING = 'PROCESSING'
    UPTODATE = 'UPTODATE'
    PROBLEM = 'PROBLEM'

    AUDIENCE_STATUS_CHOICES = [
        (PROCESSING, 'processing'),
        (UPTODATE, 'up to date'),
        (PROBLEM, 'error processing'),
    ]
    audience_status = models.CharField(
        max_length=16,
        choices=AUDIENCE_STATUS_CHOICES,
        null=True,
        blank=True
    )

    audience_name = models.CharField(max_length=50)
    create_date = models.DateTimeField()
    store = models.ForeignKey(Place, on_delete=models.CASCADE)

    def get_subscribers(self):
        return Subscriber.objects.filter(audience=self.id).count()

    def __str__(self):
        return self.audience_name

class Subscriber(models.Model):
    phone_number = models.CharField(max_length=12)
    definitely_cell_number = models.BooleanField(default=False)
    first_name = models.CharField(max_length=15, blank=True)
    last_name = models.CharField(max_length=15, blank=True)
    audience = models.ForeignKey(Audience, on_delete=models.CASCADE)
    create_date = models.DateTimeField(auto_now_add=True)

    def is_unsubscribed(self):
        return GlobalUnsubscriber.objects.filter(unsubscriber_number=self.phone_number, place = self.audience.store).exists()

    def __str__(self):
        return self.phone_number

class GlobalUnsubscriber(models.Model):
    unsubscriber_number = models.CharField(max_length=12)
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    staff_unsubscribed = models.BooleanField(default=False)
    unsubscribed_on = models.DateTimeField(auto_now_add=True)

class StoreDefaultAudience(models.Model):
    store = models.OneToOneField(Place, on_delete=models.CASCADE)

    @property
    def default_audience(self): return self.store.audiences.all()